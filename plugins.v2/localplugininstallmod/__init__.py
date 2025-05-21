import os
import shutil
import zipfile
import json
from pathlib import Path
from typing import Any, List, Dict, Tuple

from fastapi import UploadFile, File
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.plugins import _PluginBase
from app.log import logger
from app.utils.system import SystemUtils
from app.core.plugin import PluginManager
from app.db.systemconfig_oper import SystemConfigOper
from app.schemas.types import SystemConfigKey
from app.scheduler import Scheduler
from app.api.endpoints.plugin import register_plugin_api


class LocalPluginInstallMod(_PluginBase):
    # 插件名称
    plugin_name = "本地插件安装魔改版"
    # 插件描述
    plugin_desc = "(基于KoWming魔改版)上传本地ZIP插件包进行安装。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "localplugininstallmod_"
    # 加载顺序
    plugin_order = 0
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _file = None
    _onlyonce = False

    # 配置信息
    _config = {
        "enabled": False,
        "notify": False,
        "temp_path": "/tmp/moviepilot/upload",    # 临时文件存储路径
        "max_file_size": 10 * 1024 * 1024,        # 最大文件大小（10MB）
        "allowed_extensions": ["zip"],            # 允许的文件扩展名
    }

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        if config:
            self._config.update(config)
            self._enabled = config.get("enabled", True)
            
        temp_path = Path(self._config.get('temp_path'))
        if not temp_path.exists():
            try:
                temp_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建临时目录: {temp_path}")
            except Exception as e:
                logger.error(f"创建临时目录失败 {temp_path}: {e}")
                self._enabled = False # 如果临时路径创建失败则禁用插件
            
    def get_state(self) -> bool:
        """
        获取插件运行状态
        """
        return self._enabled

    async def upload_plugin(self, file: UploadFile = File(...)) -> JSONResponse:
        """
        处理插件ZIP包上传和安装
        """
        logger.debug("=== LocalUploadPlugin: 开始处理插件上传 ===") # 调试日志入口
        temp_path = Path(self._config.get('temp_path'))
        save_path = None
        extract_path = None
        
        try:
            # --- 基本文件检查 ---
            logger.info(f"开始处理插件上传: {file.filename}")

            # 检查文件大小
            try:
                file.file.seek(0, os.SEEK_END)
                file_size = file.file.tell()
                file.file.seek(0)
            except Exception as e:
                 logger.error(f"检查文件大小失败: {e}")
                 return JSONResponse(status_code=500, content={
                     "code": 500, "message": "无法检查文件大小"
                 })

            if file_size > self._config.get('max_file_size'):
                msg = f"文件大小超过限制：{self._config.get('max_file_size') / 1024 / 1024:.1f}MB"
                logger.warning(f"{file.filename}: {msg} (实际大小: {file_size} bytes)")
                return JSONResponse(status_code=400, content={"code": 400, "message": msg})
            
            # 检查文件类型
            if not file.filename or not file.filename.lower().endswith('.zip'):
                msg = "只支持ZIP格式的插件包"
                logger.warning(f"{file.filename}: {msg}")
                return JSONResponse(status_code=400, content={"code": 400, "message": msg})

            # --- 保存文件 ---
            save_path = temp_path / file.filename
            logger.info(f"保存文件到: {save_path}")
            try:
                with save_path.open('wb') as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                logger.error(f"保存文件失败 {save_path}: {e}")
                return JSONResponse(status_code=500, content={"code": 500, "message": f"保存文件失败: {e}"})
            finally:
                 # 确保即使在复制过程中出错也能关闭文件句柄
                 if file and hasattr(file, 'file') and not file.file.closed:
                    file.file.close()

            # --- 处理ZIP文件 ---
            plugin_id = None
            try:
                logger.info(f"开始处理ZIP文件: {save_path}")
                with zipfile.ZipFile(save_path, 'r') as zip_ref:
                    # 首先列出所有文件
                    all_files = zip_ref.namelist()
                    logger.info(f"ZIP包内文件列表: {all_files}")
                    
                    # 查找符合要求的__init__.py文件
                    init_files = [f for f in all_files if f.endswith('__init__.py') and len(f.split('/')) ==2]
                    if not init_files:
                        msg = "ZIP包中未找到__init__.py文件"
                        logger.error(msg)
                        return JSONResponse(status_code=400, content={"code": 400, "message": msg})
                    
                    # 从第一个找到的__init__.py文件路径中提取插件ID
                    init_path = init_files[0]
                    path_parts = Path(init_path).parts
                    if path_parts.__len__() == 2:  # 至少应该有一个目录和文件名
                        plugin_id = file.filename.split('.', 1)[0]
                    else:
                        msg = "无效的插件包结构，__init__.py 文件必须在插件目录内"
                        logger.error(msg)
                        return JSONResponse(status_code=400, content={"code": 400, "message": msg})
                    
                    logger.info(f"确定插件ID为: {plugin_id}")
                    
                    # 清理并创建解压目录
                    extract_path = temp_path / plugin_id.lower()
                    if extract_path.exists():
                        logger.info(f"清理已存在的解压目录: {extract_path}")
                        shutil.rmtree(extract_path)
                    extract_path.mkdir(parents=True, exist_ok=True)
                    
                    # 解压文件
                    logger.info(f"开始解压到: {extract_path}")
                    for file_info in zip_ref.infolist():
                        # 跳过 __MACOSX 目录
                        if '__MACOSX' in file_info.filename:
                            continue
                            
                        # 处理文件路径
                        if file_info.filename.startswith(f'{plugin_id.lower()}/'):
                            # 如果文件在正确的插件目录下，直接解压
                            zip_ref.extract(file_info, extract_path.parent)
                        else:
                            # 如果文件不在插件目录下，创建正确的目录结构
                            target_path = extract_path / Path(file_info.filename).name
                            with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                    
                    logger.info(f"解压完成: {extract_path}")
                    
                    # 验证解压后的文件结构
                    logger.info("验证解压后的文件结构:")
                    for root, dirs, files in os.walk(extract_path):
                        for file in files:
                            logger.info(f"  - {os.path.join(root, file)}")

            except zipfile.BadZipFile:
                msg = "无效或损坏的ZIP文件"
                logger.error(f"{save_path}: {msg}")
                return JSONResponse(status_code=400, content={"code": 400, "message": msg})
            except Exception as e:
                msg = f"处理ZIP文件时出错: {e}"
                logger.error(f"{save_path}: {msg}", exc_info=True)
                return JSONResponse(status_code=500, content={"code": 500, "message": msg})
            
            # --- 验证插件 ---
            try:
                init_file = extract_path / '__init__.py'
                
                logger.info(f"验证插件文件: {init_file}")
                if not init_file.is_file():
                    # 尝试在子目录中查找
                    possible_init = list(extract_path.rglob('__init__.py'))
                    if possible_init:
                        init_file = possible_init[0]
                        logger.info(f"在子目录中找到 __init__.py: {init_file}")
                    else:
                        msg = "无效的插件包，未找到 __init__.py 文件"
                        logger.error(msg)
                        return JSONResponse(status_code=400, content={"code": 400, "message": msg})

                # 验证插件内容
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class ' not in content or '_PluginBase' not in content:
                        msg = "无效的插件包，插件未继承 _PluginBase"
                        logger.warning(f"{init_file}: {msg}")
                        return JSONResponse(status_code=400, content={"code": 400, "message": msg})
                    
                logger.info("插件验证通过")

            except Exception as e:
                 logger.error(f"验证插件失败 {extract_path}: {e}")
                 return JSONResponse(status_code=500, content={"code": 500, "message": f"验证插件内容失败: {e}"})

                
            # --- 安装插件 ---
            try:
                logger.info(f"开始安装插件: {plugin_id.lower()} 从 {extract_path}")
                
                # 确保目标目录存在
                target_dir = Path("/workspace/MoviePilot/app/plugins") / plugin_id.lower()
                if target_dir.exists():
                    logger.info(f"清理已存在的插件目录: {target_dir}")
                    shutil.rmtree(target_dir)
                
                # 复制文件到正确的插件目录
                logger.info(f"复制插件文件到: {target_dir}")
                shutil.copytree(extract_path, target_dir)
                
                # 安装依赖
                requirements_file = target_dir / 'requirements.txt'
                dependencies_status = {
                    "status": "success",
                    "message": "无需安装依赖"
                }
                
                if requirements_file.exists():
                    logger.info(f"检测到依赖文件: {requirements_file}")
                    try:
                        # 首先读取并显示所有依赖
                        with open(requirements_file, 'r', encoding='utf-8') as f:
                            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        if requirements:
                            logger.info(f"需要安装的依赖列表:")
                            for req in requirements:
                                logger.info(f"  - {req}")
                            
                            # 尝试使用不同的安装策略
                            strategies = []
                            
                            # 添加镜像站策略
                            if settings.PIP_PROXY:
                                strategies.append(("镜像站", ["pip", "install", "-r", str(requirements_file), "-i", settings.PIP_PROXY, "-v"]))
                            
                            # 添加代理策略
                            if settings.PROXY_HOST:
                                strategies.append(("代理", ["pip", "install", "-r", str(requirements_file), "--proxy", settings.PROXY_HOST, "-v"]))
                            
                            # 添加直连策略
                            strategies.append(("直连", ["pip", "install", "-r", str(requirements_file), "-v"]))
                            
                            # 遍历策略进行安装
                            success = False
                            for strategy_name, pip_command in strategies:
                                logger.info(f"[PIP] 开始使用{strategy_name}策略安装依赖")
                                logger.info(f"[PIP] 执行命令: {' '.join(pip_command)}")
                                
                                success, message = SystemUtils.execute_with_subprocess(pip_command)
                                
                                # 解析pip输出
                                if message:
                                    # 分行处理输出
                                    for line in message.splitlines():
                                        # 过滤一些不重要的日志
                                        if any(x in line.lower() for x in ['collecting', 'downloading', 'installing', 'successfully']):
                                            logger.info(f"[PIP] {line.strip()}")
                                        elif 'error' in line.lower():
                                            logger.error(f"[PIP] {line.strip()}")
                                        elif 'warning' in line.lower():
                                            logger.warning(f"[PIP] {line.strip()}")
                                
                                if success:
                                    logger.info(f"[PIP] 使用{strategy_name}策略安装依赖成功")
                                    dependencies_status = {
                                        "status": "success"
                                    }
                                    break
                                else:
                                    logger.warning(f"[PIP] 使用{strategy_name}策略安装依赖失败")
                                    if message:
                                        logger.warning(f"[PIP] 失败原因: {message}")
                            
                            if not success:
                                logger.error("[PIP] 所有依赖安装策略均失败")
                                return JSONResponse(status_code=500, content={
                                    "code": 500,
                                    "message": "依赖安装失败",
                                    "data": {
                                        "plugin_id": plugin_id,
                                        "dependencies": {
                                            "status": "failed",
                                            "message": "所有依赖安装策略均失败"
                                        }
                                    }
                                })
                        else:
                            logger.info("依赖文件为空，无需安装依赖")
                            dependencies_status = {
                                "status": "success",
                                "message": "依赖文件为空，无需安装依赖"
                            }
                            
                    except Exception as e:
                        logger.error(f"安装依赖时出错: {e}", exc_info=True)
                        return JSONResponse(status_code=500, content={
                            "code": 500,
                            "message": "依赖安装失败",
                            "data": {
                                "plugin_id": plugin_id,
                                "dependencies": {
                                    "status": "failed",
                                    "message": str(e)
                                }
                            }
                        })

                # 使用PluginManager加载插件
                plugin_manager = PluginManager()
                
                # 添加到已安装插件列表
                install_plugins = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
                if plugin_id not in install_plugins:
                    install_plugins.append(plugin_id)
                    SystemConfigOper().set(SystemConfigKey.UserInstalledPlugins, install_plugins)
                
                # 重新加载插件
                plugin_manager.reload_plugin(plugin_id)
                
                # 注册插件服务
                Scheduler().update_plugin_job(plugin_id)
                
                # 注册插件API
                register_plugin_api(plugin_id)
                
                logger.info(f"插件安装成功: {plugin_id}")
                return JSONResponse(status_code=200, content={
                    "code": 200,
                    "message": f"插件 {plugin_id} 安装成功",
                    "data": {
                        "plugin_id": plugin_id,
                        "dependencies": dependencies_status
                    }
                })
                
            except Exception as e:
                logger.error(f"插件安装过程中发生错误: {e}", exc_info=True)
                # 确保清理任何部分安装的文件
                target_dir = Path("/workspace/MoviePilot/app/plugins") / plugin_id.lower()
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                return JSONResponse(status_code=500, content={
                    "code": 500,
                    "message": f"插件安装过程中发生错误: {e}"
                })

        except Exception as e:
            # 捕获主流程中的意外错误
            logger.error(f"插件上传处理失败: {e}", exc_info=True) # 记录堆栈跟踪
            return JSONResponse(status_code=500, content={
                "code": 500,
                "message": f"插件上传处理失败：{e}"
            })

        finally:
            # --- 清理工作 ---
            if extract_path and extract_path.exists():
                try:
                    shutil.rmtree(extract_path)
                    logger.info(f"清理临时解压目录: {extract_path}")
                except Exception as e:
                    logger.error(f"清理目录失败 {extract_path}: {e}")
            if save_path and save_path.exists():
                try:
                    save_path.unlink()
                    logger.info(f"清理临时ZIP文件: {save_path}")
                except Exception as e:
                    logger.error(f"清理文件失败 {save_path}: {e}")
             # 确保文件句柄已关闭
            if file and hasattr(file, 'file') and not file.file.closed:
                try:
                    file.file.close()
                except Exception as e:
                    logger.warning(f"关闭上传文件句柄时出错: {e}")

    def get_api(self) -> List[Dict[str, Any]]:
        """
        注册API接口
        """
        return [
            {
                "path": "/localupload",
                "endpoint": self.upload_plugin,
                "methods": ["POST"],
                "summary": "上传插件",
                "description": "上传本地ZIP插件包进行安装"
            }
        ]

    def get_service(self) -> List[Dict[str, Any]]:
        pass

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面
        """
        return [
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 4
                        },
                        'content': [
                            {
                                'component': 'VSwitch',
                                'props': {
                                    'model': 'enabled',
                                    'label': '启用插件',
                                }
                            }
                        ]
                    }
                ]
            }
        ], {
            # 返回当前配置值作为初始状态
            "enabled": self._config.get("enabled", True)
        }

    def get_page(self) -> List[dict]:
        """
        拼装插件详情页面
        """
        # 获取 API Token 的值
        api_token_value = settings.API_TOKEN
        # 使用 json.dumps 将其转换为安全的 JavaScript 字符串字面量 (带引号)
        js_safe_api_token = json.dumps(api_token_value)

        # 构建 onclick JavaScript 代码, 使用 f-string 嵌入转换后的 token
        onclick_js = f"""
        (async (button) => {{
            const fileInput = document.querySelector('#localupload-file-input'); // 使用ID选择器
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {{
                alert('错误：请先选择一个ZIP文件！');
                return;
            }}
            const file = fileInput.files[0];

            const maxSize = {self._config.get('max_file_size', 10*1024*1024)};
            if (file.size > maxSize) {{
                 alert(`错误：文件大小超过限制 (${{(maxSize / 1024 / 1024).toFixed(1)}}MB)`);
                 return;
            }}

            const formData = new FormData();
            formData.append('file', file);

            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = '安装中...';

            const errorAlert = document.getElementById('localupload-error-alert');
            const successAlert = document.getElementById('localupload-success-alert');

            if (errorAlert) errorAlert.style.display = 'none';
            if (successAlert) successAlert.style.display = 'none';

            try {{
                // 正确嵌入 API Token 作为查询参数
                const apiKey = {js_safe_api_token};
                const apiUrl = `/api/v1/plugin/LocalPluginInstallMod/localupload?apikey=${{encodeURIComponent(apiKey)}}`; // 使用encodeURIComponent确保安全
                
                const response = await fetch(apiUrl, {{
                    method: 'POST',
                    body: formData,
                }});

                const result = await response.json();

                if (response.ok && result.code === 200) {{
                    if (successAlert) {{
                        let successMessage = result.message || '插件安装成功！';
                        if (result.data && result.data.dependencies) {{
                            successMessage += '<br>依赖安装状态: ' + 
                                (result.data.dependencies.status === 'success' ? '成功' : '失败');
                            if (result.data.dependencies.message) {{
                                successMessage += '<br>' + result.data.dependencies.message;
                            }}
                        }}
                        successAlert.innerHTML = successMessage;
                        successAlert.style.whiteSpace = 'pre-line';
                        successAlert.style.display = 'block';
                    }} else {{
                        alert('成功: ' + (result.message || '插件安装成功！'));
                    }}
                    if (fileInput) fileInput.value = '';
                }} else {{
                    const errorMsg = result.message || `安装失败，状态码: ${{response.status}}`;
                    if (errorAlert) {{
                        let errorMessage = errorMsg;
                        if (result.data && result.data.dependencies) {{
                            errorMessage += '<br>依赖安装状态: ' + 
                                (result.data.dependencies.status === 'success' ? '成功' : '失败');
                            if (result.data.dependencies.message) {{
                                errorMessage += '<br>' + result.data.dependencies.message;
                            }}
                        }}
                        errorAlert.innerHTML = errorMessage;
                        errorAlert.style.whiteSpace = 'pre-line';
                        errorAlert.style.display = 'block';
                    }} else {{
                        alert('失败: ' + errorMsg);
                    }}
                }}

            }} catch (error) {{
                const errorMsg = '请求发送失败: ' + error;
                if (errorAlert) {{
                    errorAlert.textContent = errorMsg;
                    errorAlert.style.display = 'block';
                }} else {{
                    alert(errorMsg);
                }}
                console.error("Fetch error:", error);

            }} finally {{
                button.disabled = false;
                button.textContent = originalText;
            }}
        }})(this)
        """

        page_structure = [
             {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'elevation': 3,
                                    'class': 'mx-auto rounded-lg',
                                    'border': True
                                },
                                'content': [
                                    {
                                        'component': 'VCardItem',
                                        'props': {
                                            'class': 'pb-0 d-flex flex-column align-center justify-center'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'mb-2'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VCardTitle',
                                                        'props': {
                                                            'class': 'text-h5 font-weight-bold d-flex align-center justify-center'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'VIcon',
                                                                'props': {
                                                                    'color': 'info',
                                                                    'size': 'large',
                                                                    'class': 'mr-2'
                                                                },
                                                                'text': 'mdi-upload'
                                                            },
                                                            {
                                                                'component': 'span',
                                                                'text': '上传插件'
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-center mb-2'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VCardSubtitle',
                                                        'props': {
                                                            'class': 'text-medium-emphasis'
                                                        },
                                                        'text': '上传本地ZIP插件包进行安装'
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'VDivider',
                                        'props': {
                                            'class': 'mx-4 my-2'
                                        }
                                    },
                                    {
                                        'component': 'VContainer',
                                        'props': {
                                            'class': 'px-md-10 py-4',
                                            'max-width': '800'
                                        },
                                        'content': [
                                            {
                                                'component': 'VCardText',
                                                'content': [
                                                    { # 信息提示
                                                        'component': 'VAlert',
                                                        'props': {
                                                            'type': 'info',
                                                            'variant': 'tonal',
                                                            'text': '请确保插件包包含__init__.py文件且继承_PluginBase类',
                                                            'class': 'mb-6',
                                                            'density': 'comfortable',
                                                            'border': 'start',
                                                            'border-color': 'primary',
                                                            'icon': 'mdi-information',
                                                            'elevation': 1,
                                                            'rounded': 'lg'
                                                        }
                                                    },
                                                    { # 成功提示
                                                        'component': 'VAlert',
                                                        'props': {
                                                            'type': 'success',
                                                            'variant': 'tonal',
                                                            'class': 'mb-6',
                                                            'density': 'comfortable',
                                                            'border': 'start',
                                                            'icon': 'mdi-check-circle',
                                                            'elevation': 1,
                                                            'rounded': 'lg',
                                                            'id': 'localupload-success-alert',
                                                            'style': 'display: none;'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    { # 错误提示
                                                        'component': 'VAlert',
                                                        'props': {
                                                            'type': 'error',
                                                            'variant': 'tonal',
                                                            'class': 'mb-6',
                                                            'density': 'comfortable',
                                                            'border': 'start',
                                                            'icon': 'mdi-alert',
                                                            'elevation': 1,
                                                            'rounded': 'lg',
                                                            'id': 'localupload-error-alert',
                                                            'style': 'display: none;'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VSheet',
                                                        'props': {
                                                            'class': 'pa-6',
                                                            'rounded': 'lg',
                                                            'elevation': 0,
                                                            'border': True,
                                                            'color': 'background'
                                                        },
                                                        'content': [
                                                            { # 文件输入框
                                                                'component': 'VFileInput',
                                                                'props': {
                                                                    'model': 'file',
                                                                    'label': '选择插件ZIP包',
                                                                    'hint': f'最大文件大小：{self._config.get("max_file_size") / 1024 / 1024:.1f}MB',
                                                                    'persistent-hint': True,
                                                                    'chips': True,
                                                                    'multiple': False,
                                                                    'show-size': True,
                                                                    'accept': '.zip',
                                                                    'prepend-icon': 'mdi-folder-zip',
                                                                    'size': 'x-large',
                                                                    'height': '64',
                                                                    'variant': 'outlined',
                                                                    'class': 'mb-6 custom-file-input',
                                                                    'style': 'font-size: 24px;',
                                                                    'id': 'localupload-file-input',
                                                                    'density': 'default',
                                                                    'color': 'primary',
                                                                    'bg-color': 'surface'
                                                                }
                                                            },
                                                            { # 按钮
                                                                'component': 'VBtn',
                                                                'props': {
                                                                    'color': 'primary',
                                                                    'block': True,
                                                                    'size': 'large',
                                                                    'onclick': onclick_js,
                                                                    'id': 'localupload-install-button',
                                                                    'elevation': 2,
                                                                    'rounded': 'lg',
                                                                    'class': 'text-none font-weight-bold'
                                                                },
                                                                'content': [
                                                                    {'component': 'VIcon', 'props': {'icon': 'mdi-package-variant-plus', 'class': 'mr-2'}},
                                                                    {'component': 'span', 'text': '安装插件'}
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            { # 添加提示信息卡片
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'elevation': 2,
                                    'class': 'mx-auto rounded-lg',
                                    'border': True
                                },
                                'content': [
                                    {
                                        'component': 'VCardItem',
                                        'props': {
                                            'class': 'pb-0'
                                        },
                                        'content': [
                                            {
                                                'component': 'VCardTitle',
                                                'props': {
                                                    'class': 'text-h6 font-weight-bold d-flex align-center'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VIcon',
                                                        'props': {
                                                            'color': 'info',
                                                            'size': 'default',
                                                            'class': 'mr-2'
                                                        },
                                                        'text': 'mdi-information'
                                                    },
                                                    {
                                                        'component': 'span',
                                                        'text': '插件安装说明'
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'VDivider',
                                        'props': {
                                            'class': 'mx-4 my-2'
                                        }
                                    },
                                    {
                                        'component': 'VCardText',
                                        'content': [
                                            {
                                                'component': 'VList',
                                                'props': {
                                                    'lines': 'two',
                                                    'density': 'comfortable'
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VListItem',
                                                        'props': {
                                                            'prepend-icon': 'mdi-cog',
                                                            'title': '首次安装'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-2'
                                                                },
                                                                'content': [
                                                                    {
                                                                        'component': 'span',
                                                                        'text': '首次安装请点击右下角设置打开 启用插件 保存，如果安装提示'
                                                                    },
                                                                    {
                                                                        'component': 'VChip',
                                                                        'props': {
                                                                            'color': 'error',
                                                                            'size': 'small',
                                                                            'class': 'mx-1'
                                                                        },
                                                                        'text': '安装失败，状态码: 404'
                                                                    },
                                                                    {
                                                                        'component': 'span',
                                                                        'text': '请重启MoviePilot生效上传API'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VListItem',
                                                        'props': {
                                                            'prepend-icon': 'mdi-folder-zip',
                                                            'title': 'ZIP文件结构'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-2'
                                                                },
                                                                'text': '插件包必须包含以下内容：- 插件目录（如 myplugin/）- __init__.py 文件（必须继承 _PluginBase）- requirements.txt（可选，用于声明依赖）- 其他插件相关文件'
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VListItem',
                                                        'props': {
                                                            'prepend-icon': 'mdi-alert',
                                                            'title': '注意事项'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-2'
                                                                },
                                                                'text': '1. 确保插件包大小不超过限制 2. 符合MP插件命名规范，压缩包名字需要为插件类名 3. 安装前请确保插件代码安全可靠 4. 安装失败时请检查错误信息'
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        'component': 'VListItem',
                                                        'props': {
                                                            'prepend-icon': 'mdi-help-circle',
                                                            'title': '常见问题'
                                                        },
                                                        'content': [
                                                            {
                                                                'component': 'div',
                                                                'props': {
                                                                    'class': 'text-body-2'
                                                                },
                                                                'text': '1. 安装失败？检查插件包结构是否正确 2. 依赖安装失败？尝试手动安装依赖 3. 插件不工作？检查日志获取详细信息'
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        return page_structure

    def stop_service(self):
        """
        停止插件
        """
        self._enabled = False
        logger.info("插件已停止")