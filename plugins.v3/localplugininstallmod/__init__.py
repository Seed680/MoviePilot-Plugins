import ast
import json
import keyword
import os
import shutil
import stat
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Depends, File, UploadFile

from app.api.deps import get_current_active_superuser
from app.api.endpoints.plugin import register_plugin_api
from app.db.oper.systemconfig import SystemConfigOper
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import Response
from app.schemas.types import SystemConfigKey
from app.sdk.config import settings
from app.sdk.logging import logger
from app.sdk.plugins import PluginManager
from app.sdk.utilities import SystemUtils


class LocalPluginInstallMod(_PluginBase):
    plugin_name = "本地插件安装魔改版"
    plugin_desc = "上传本地 ZIP 插件包进行安装。"
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    plugin_version = "2.0.0"
    plugin_author = "Seed680"
    author_url = "https://github.com/Seed680"
    plugin_config_prefix = "localplugininstallmod_"
    plugin_order = 0
    auth_level = 1

    _enabled = False
    _config = {
        "enabled": False,
        "temp_path": "/tmp/moviepilot/upload",
        "max_file_size": 10 * 1024 * 1024,
        "max_members": 500,
        "max_member_size": 20 * 1024 * 1024,
        "max_extract_size": 100 * 1024 * 1024,
    }

    def init_plugin(self, config: dict = None):
        if config:
            self._config.update(config)
        self._enabled = bool(self._config.get("enabled", False))
        try:
            Path(self._config["temp_path"]).expanduser().mkdir(parents=True, exist_ok=True)
        except Exception as err:
            logger.error(f"本地插件上传临时目录创建失败：{err}")
            self._enabled = False

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def _response(success: bool, message: str, data: Optional[dict] = None) -> Response:
        return Response(success=success, message=message, data=data)

    @staticmethod
    def _member_path(info: zipfile.ZipInfo) -> PurePosixPath:
        name = info.filename
        if not name or "\x00" in name:
            raise ValueError("ZIP 包含空路径或 NUL 字符")
        if "\\" in name:
            raise ValueError("ZIP 路径不得包含反斜杠")
        if name.startswith(("/", "//")) or (len(name) >= 2 and name[0].isalpha() and name[1] == ":"):
            raise ValueError("ZIP 包含绝对路径、盘符或 UNC 路径")

        path = PurePosixPath(name)
        if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
            raise ValueError("ZIP 包含不安全的路径")
        return path

    @classmethod
    def _validate_archive(cls, archive: zipfile.ZipFile, limits: dict) -> Tuple[str, List[Tuple[zipfile.ZipInfo, PurePosixPath]]]:
        infos = archive.infolist()
        if not infos:
            raise ValueError("ZIP 包为空")
        if len(infos) > limits["max_members"]:
            raise ValueError("ZIP 成员数量超过限制")

        members: List[Tuple[zipfile.ZipInfo, PurePosixPath]] = []
        roots = set()
        targets = set()
        total_size = 0
        for info in infos:
            path = cls._member_path(info)
            normalized = path.as_posix().rstrip("/")
            target_key = normalized.casefold()
            if target_key in targets:
                raise ValueError("ZIP 包含重复的归一化目标")
            targets.add(target_key)
            roots.add(path.parts[0])

            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if file_type and not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError("ZIP 不得包含符号链接或设备文件")
            if info.file_size < 0 or info.file_size > limits["max_member_size"]:
                raise ValueError("ZIP 单个成员超过解压限制")
            total_size += info.file_size
            if total_size > limits["max_extract_size"]:
                raise ValueError("ZIP 总解压大小超过限制")
            members.append((info, path))

        if len(roots) != 1:
            raise ValueError("ZIP 必须且只能包含一个插件根目录")
        root = next(iter(roots))
        if not root.isidentifier() or keyword.iskeyword(root):
            raise ValueError("插件根目录不是合法的 Python 标识符")
        return root, members

    @staticmethod
    def _validate_entry(entry: Path, root_name: str) -> str:
        try:
            source = entry.read_text(encoding="utf-8")
            tree = ast.parse(source, filename="__init__.py")
        except (OSError, UnicodeError, SyntaxError) as err:
            raise ValueError(f"插件入口无法解析：{err}") from err

        plugin_classes = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            inherits_plugin_base = any(
                (isinstance(base, ast.Name) and base.id == "_PluginBase")
                or (isinstance(base, ast.Attribute) and base.attr == "_PluginBase")
                for base in node.bases
            )
            if inherits_plugin_base:
                plugin_classes.append(node.name)

        if len(plugin_classes) != 1:
            raise ValueError("插件入口必须且只能定义一个 _PluginBase 子类")
        plugin_id = plugin_classes[0]
        if not plugin_id.isidentifier() or keyword.iskeyword(plugin_id):
            raise ValueError("插件 ID 不是合法的 Python 标识符")
        if plugin_id.lower() != root_name.lower() or root_name != root_name.lower():
            raise ValueError("插件根目录必须是插件类名的小写形式")
        return plugin_id

    @classmethod
    def _extract_archive(cls, archive: zipfile.ZipFile, destination: Path, limits: dict) -> Tuple[str, Path]:
        root_name, members = cls._validate_archive(archive, limits)
        destination_resolved = destination.resolve()
        written = 0
        for info, relative in members:
            target = (destination / Path(*relative.parts)).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise ValueError("ZIP 成员目标越过临时目录")
            if info.is_dir() or info.filename.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            member_written = 0
            with archive.open(info, "r") as source, target.open("xb") as output:
                while chunk := source.read(1024 * 1024):
                    member_written += len(chunk)
                    written += len(chunk)
                    if member_written > limits["max_member_size"] or written > limits["max_extract_size"]:
                        raise ValueError("ZIP 实际解压大小超过限制")
                    output.write(chunk)
        return root_name, destination / root_name

    def _install_dependencies(self, requirements_file: Path) -> Tuple[bool, str]:
        if not requirements_file.is_file() or not requirements_file.read_text(encoding="utf-8").strip():
            return True, "无需安装依赖"

        command = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        if settings.PIP_PROXY:
            command.extend(["-i", settings.PIP_PROXY])
        if settings.PROXY_HOST:
            command.extend(["--proxy", settings.PROXY_HOST])
        logger.warning("宿主 SDK 未提供插件依赖安装接口，使用最小 pip 安装路径")
        success, _ = SystemUtils.execute_with_subprocess(
            command, safe_command=["pip", "install", "-r", "<plugin requirements>"]
        )
        return success, "依赖安装成功" if success else "依赖安装失败"

    @staticmethod
    def _restore_install(target: Path, backup: Optional[Path], plugin_id: str, old_plugins: List[str]):
        manager = PluginManager()
        try:
            manager.remove_plugin(plugin_id)
        except Exception:
            pass
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        if backup and backup.exists():
            os.replace(backup, target)
        SystemConfigOper().set(SystemConfigKey.UserInstalledPlugins, old_plugins)
        if backup:
            try:
                manager.reload_plugin(plugin_id)
                Scheduler().update_plugin_job(plugin_id)
                register_plugin_api(plugin_id)
            except Exception as err:
                logger.error(f"旧版插件目录已恢复，但运行态恢复失败，需重启 MoviePilot：{err}")

    async def upload_plugin(
        self,
        file: UploadFile = File(...),
        _: Any = Depends(get_current_active_superuser),
    ) -> Response:
        filename = Path(file.filename or "").name
        if not filename.lower().endswith(".zip"):
            return self._response(False, "只支持 ZIP 格式的插件包")

        max_file_size = int(self._config.get("max_file_size", 10 * 1024 * 1024))
        try:
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)
        except Exception:
            return self._response(False, "无法检查上传文件大小")
        if file_size > max_file_size:
            return self._response(False, f"文件大小超过限制：{max_file_size / 1024 / 1024:.1f}MB")

        limits = {
            "max_members": int(self._config.get("max_members", 500)),
            "max_member_size": int(self._config.get("max_member_size", 20 * 1024 * 1024)),
            "max_extract_size": int(self._config.get("max_extract_size", 100 * 1024 * 1024)),
        }
        upload_root = Path(self._config["temp_path"]).expanduser()
        archive_path: Optional[Path] = None
        transaction_root: Optional[Path] = None
        backup: Optional[Path] = None
        target: Optional[Path] = None
        plugin_id: Optional[str] = None
        old_plugins: List[str] = []
        swapped = False

        try:
            upload_root.mkdir(parents=True, exist_ok=True)
            fd, archive_name = tempfile.mkstemp(prefix="plugin-", suffix=".zip", dir=upload_root)
            os.close(fd)
            archive_path = Path(archive_name)
            with archive_path.open("wb") as output:
                shutil.copyfileobj(file.file, output)

            plugins_root = (Path(settings.ROOT_PATH) / "app" / "plugins").resolve()
            plugins_root.mkdir(parents=True, exist_ok=True)
            transaction_root = Path(tempfile.mkdtemp(prefix=".local-install-", dir=plugins_root))
            with zipfile.ZipFile(archive_path, "r") as archive:
                root_name, staged_plugin = self._extract_archive(archive, transaction_root, limits)
            plugin_id = self._validate_entry(staged_plugin / "__init__.py", root_name)

            target = plugins_root / plugin_id.lower()
            old_plugins = list(SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or [])
            backup = plugins_root / f".{plugin_id.lower()}.backup-{uuid.uuid4().hex}"
            if target.exists():
                os.replace(target, backup)
            else:
                backup = None
            os.replace(staged_plugin, target)
            swapped = True

            dependencies_ok, dependencies_message = self._install_dependencies(target / "requirements.txt")
            if not dependencies_ok:
                raise RuntimeError(dependencies_message)

            manager = PluginManager()
            installed_plugins = old_plugins if plugin_id in old_plugins else [*old_plugins, plugin_id]
            SystemConfigOper().set(SystemConfigKey.UserInstalledPlugins, installed_plugins)
            manager.reload_plugin(plugin_id)
            if plugin_id not in manager.get_running_plugin_ids():
                raise RuntimeError("插件未能加载到运行环境")
            Scheduler().update_plugin_job(plugin_id)
            register_plugin_api(plugin_id)

            if backup and backup.exists():
                shutil.rmtree(backup)
                backup = None
            logger.info(f"本地插件 {plugin_id} 安装成功")
            return self._response(
                True,
                f"插件 {plugin_id} 安装成功",
                {"plugin_id": plugin_id, "dependencies": {"status": "success", "message": dependencies_message}},
            )
        except (ValueError, zipfile.BadZipFile) as err:
            if target and plugin_id and (swapped or (backup and backup.exists())):
                self._restore_install(target, backup, plugin_id, old_plugins)
                backup = None
            logger.error(f"本地插件校验或安装失败：{err}")
            return self._response(False, str(err))
        except Exception as err:
            if target and plugin_id and (swapped or (backup and backup.exists())):
                self._restore_install(target, backup, plugin_id, old_plugins)
                backup = None
            logger.error(f"本地插件安装失败：{err}")
            return self._response(False, f"插件安装失败：{err}")
        finally:
            try:
                file.file.close()
            except Exception:
                pass
            if archive_path:
                archive_path.unlink(missing_ok=True)
            if transaction_root and transaction_root.exists():
                shutil.rmtree(transaction_root, ignore_errors=True)
            if backup and backup.exists():
                logger.error("插件备份目录未自动删除，需人工检查")

    def get_api(self) -> List[Dict[str, Any]]:
        return [{
            "path": "/localupload",
            "endpoint": self.upload_plugin,
            "methods": ["POST"],
            "summary": "上传本地插件",
            "description": "安全验证并安装本地 ZIP 插件包",
        }]

    def get_service(self) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [{
            "component": "VForm",
            "content": [{
                "component": "VSwitch",
                "props": {"model": "enabled", "label": "启用插件"},
            }],
        }], {"enabled": self._config.get("enabled", False)}

    def get_page(self) -> List[dict]:
        api_token = json.dumps(settings.API_TOKEN)
        max_size = int(self._config.get("max_file_size", 10 * 1024 * 1024))
        onclick = f"""
        (async (button) => {{
          const input = document.querySelector('#localupload-file-input');
          const alertBox = document.querySelector('#localupload-result');
          if (!input?.files?.length) {{ alertBox.textContent = '请先选择 ZIP 文件'; return; }}
          if (input.files[0].size > {max_size}) {{ alertBox.textContent = '文件大小超过限制'; return; }}
          button.disabled = true;
          const form = new FormData(); form.append('file', input.files[0]);
          try {{
            const token = {api_token};
            const response = await fetch(`/api/v1/plugin/LocalPluginInstallMod/localupload?apikey=${{encodeURIComponent(token)}}`, {{method: 'POST', body: form}});
            const envelope = await response.json();
            const result = envelope?.data && typeof envelope.data.success === 'boolean' ? envelope.data : envelope;
            alertBox.textContent = result?.message || (result?.success ? '安装成功' : '安装失败');
            alertBox.className = result?.success ? 'text-success mt-4' : 'text-error mt-4';
            if (result?.success) input.value = '';
          }} catch (error) {{ alertBox.textContent = '请求失败'; alertBox.className = 'text-error mt-4'; }}
          finally {{ button.disabled = false; }}
        }})(this)
        """
        return [{
            "component": "VContainer",
            "content": [{
                "component": "VFileInput",
                "props": {
                    "id": "localupload-file-input", "label": "选择插件 ZIP 包", "accept": ".zip",
                    "show-size": True, "prepend-icon": "mdi-folder-zip", "variant": "outlined",
                },
            }, {
                "component": "VBtn",
                "props": {"color": "primary", "onclick": onclick, "prepend-icon": "mdi-package-variant-plus"},
                "text": "安装插件",
            }, {
                "component": "div",
                "props": {"id": "localupload-result", "class": "mt-4"},
            }],
        }]

    def stop_service(self):
        self._enabled = False
