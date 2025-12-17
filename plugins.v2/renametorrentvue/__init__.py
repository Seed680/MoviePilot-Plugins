import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from typing import List, Tuple, Dict, Any, Optional, Union, Set
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.core.meta.metabase import MetaBase
from app.core.metainfo import MetaInfo
from app.db.downloadhistory_oper import DownloadHistoryOper, DownloadHistory
from app.db.models.plugindata import PluginData
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.modules.qbittorrent import Qbittorrent
from app.plugins import _PluginBase
from app.schemas import Notification, NotificationType
from app.schemas.types import EventType, MediaType, SystemConfigKey
from app.core.context import MediaInfo, TorrentInfo, Context
from app.modules.filemanager.transhandler import TransHandler


@dataclass
class TorrentFile:
    """
    文件列表
    """
    # 文件名称(包含子文件夹路径和文件后缀)
    name: str
    # 文件大小
    size: int
    # 文件优先级
    priority: int = 0


@dataclass
class TorrentInfoRT:
    """
    种子信息
    """
    # 种子名称
    name: str
    # 种子保存路径
    save_path: str
    # 种子大小
    total_size: int
    # 种子哈希
    hash: str
    # Torrent 自动管理
    auto_tmm: bool = False
    # 种子分类
    category: str = ""
    # 种子标签
    tags: List[str] = field(default_factory=list)
    # 种子文件列表
    files: List[TorrentFile] = field(default_factory=list)


@dataclass
class RenameHistory:
    """
    重命名历史记录
    """
    # 种子哈希
    hash: str
    # 种子原始名称
    original_name: str
    # 重命名后的名称
    after_name: str
    # 是否成功
    success: bool
    # 处理时间
    date: str


class QbittorrentDownloader():
    def __init__(self, qbc: Qbittorrent):
        self.qbc = qbc.qbc

    def torrents_rename(self, torrent_hash: str, new_torrent_name: str) -> None:
        self.qbc.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=new_torrent_name)

    def torrents_info(self, torrent_hash: Optional[Union[str, list]] = None) -> List[TorrentInfoRT]:
        """
        获取种子信息
        """
        torrents = []
        torrents_info = self.qbc.torrents_info(torrent_hashes=torrent_hash) if torrent_hash else self.qbc.torrents_info()
        if torrents_info:
            for torrent_info in torrents_info:
                torrents.append(TorrentInfoRT(
                    name = torrent_info.get('name'),
                    save_path = torrent_info.get('save_path'),
                    total_size = torrent_info.get('total_size'),
                    hash=torrent_info.get('hash'),
                    auto_tmm=torrent_info.get('auto_tmm'),
                    category=torrent_info.get('category'),
                    tags=torrent_info.get('tags').split(","),
                    files= [
                        TorrentFile(
                            name=file.get('name'),
                            size=file.get('size'),
                            priority=file.get('priority'))
                        for file in torrent_info.files
                    ]
                ))
        return torrents

    def torrents_add_tags(self, torrent_hash: Optional[Union[str, list]] = None, tags: Optional[list] = None) -> None:
        """
        添加标签
        """
        if torrent_hash:
            self.qbc.torrents_add_tags(torrent_hashes=torrent_hash, tags=tags)

    def get_torrents(self):
        """
        获取种子列表(Vue兼容方法)
        """
        return self.torrents_info()

    def rename_torrent(self, hash: str, new_name: str):
        """
        重命名单个种子(Vue兼容方法)
        """
        try:
            self.torrents_rename(hash, new_name)
            return True
        except Exception as e:
            logger.error(f"重命名种子失败：{str(e)}")
            return False

    def add_torrent_tag(self, hash: str, tag: str):
        """
        添加标签(Vue兼容方法)
        """
        try:
            self.torrents_add_tags(hash, [tag])
            return True
        except Exception as e:
            logger.error(f"添加标签失败：{str(e)}")
            return False

    @property
    def type(self):
        """
        下载器类型(Vue兼容属性)
        """
        return "qbittorrent"


class RenameTorrentVue(_PluginBase):
    # 插件名称
    plugin_name = "重命名种子Vue版"
    # 插件描述
    plugin_desc = "提供Vue界面重命名下载器中的种子。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "0.1.4"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "renametorrentvue_"
    # 加载顺序
    plugin_order = 16
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None

    # 配置属性
    # 启用插件
    _enabled: bool = False
    # 启用通知
    _notify: bool = False
    # cron表达式
    _cron: str = ""
    # 启用定时任务
    _cron_enabled: bool = False
    # 启用事件监听
    _event_enabled: bool = False
    # 格式化字符
    _format_torrent_name: str = "{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}"
    # 下载器
    _downloader: list = []
    # 排除标签
    _exclude_tags: str = ""
    # 包含标签
    _include_tags: str = ""
    # 排除目录
    _exclude_dirs: str = ""
    # 种子哈希白名单
    _hash_white_list: str = ""
    # 立即运行一次
    _onlyonce = False
    # 恢复记录
    _recovery = False
    # 尝试失败
    _retry = False
    # 成功后添加标签
    _add_tag_after_rename: bool = False
    # 重命名历史记录索引缓存
    _rename_history_index: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None
    # 已重命名的种子名称缓存
    _renamed_names_cache: Optional[Set[str]] = None

    downloader_helper = None
    downloadhis = None

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        self.load_config(config)
        self.downloader_helper = DownloaderHelper()
        self.downloadhis = DownloadHistoryOper()
        # 停止现有任务
        self.stop_service()

        # 如果启用插件
        if not self._enabled:
            self.update_config(config=config)
            return

        if not self._onlyonce:
            self.update_config(config=config)
            return

        self._onlyonce = False
        config.update({"onlyonce": False})
        self.update_config(config=config)

        if self._recovery:
            self._recovery = False
            config.update({"recovery": False})
            logger.info("立即恢复重命名下载器种子任务")
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(self.recoveryTorrent, 'date',
                                    run_date=datetime.now(
                                        tz=pytz.timezone(settings.TZ)
                                    ) + timedelta(seconds=3),
                                    name="恢复重命名下载器种子")
        else:
            logger.info("立即运行一次重命名下载器种子任务")
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(self.cron_process_main, 'date',
                                    run_date=datetime.now(
                                        tz=pytz.timezone(settings.TZ)
                                    ) + timedelta(seconds=3),
                                    name="重命名下载器种子")

        if self._scheduler.get_jobs():
            # 启动服务
            self._scheduler.print_jobs()
            self._scheduler.start()
    def load_config(self, config: dict):
        """加载配置"""
        if not config:
            return

        # 遍历配置中的键并设置相应的属性
        for key in (
                "enabled",
                "notify",
                "cron",
                "cron_enabled",
                "event_enabled",
                "downloader",
                "exclude_dirs",
                "hash_white_list",
                "exclude_tags",
                "include_tags",
                "format_torrent_name",
                "onlyonce",
                "recovery",
                "retry",
                "add_tag_after_rename"
        ):
            # 特殊处理downloader，确保始终是列表
            if key == "downloader":
                downloader_value = config.get(key, getattr(self, f"_{key}"))
                if isinstance(downloader_value, str):
                    # 如果是字符串，转换为列表
                    setattr(self, f"_{key}", [downloader_value] if downloader_value else [])
                elif isinstance(downloader_value, list):
                    # 如果已经是列表，直接赋值
                    setattr(self, f"_{key}", downloader_value)
                else:
                    # 其他情况，设置为空列表
                    setattr(self, f"_{key}", [])
            else:
                setattr(self, f"_{key}", config.get(key, getattr(self, f"_{key}")))

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字列表
        """
        return [{
            "cmd": "/rename_torrent_vue",
            "event": EventType.PluginAction,
            "desc": "重命名种子文件Vue版",
            "category": "下载",
            "data": {
                "action": "rename_torrent_vue"
            }
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [{
            "path": "/list_torrents",
            "endpoint": self.list_torrents,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取种子列表",
            "description": "获取下载器中的种子列表"
        }, {
            "path": "/rename_torrent",
            "endpoint": self.rename_torrent,
            "auth": "bear",
            "methods": ["POST"],
            "summary": "重命名单个种子",
            "description": "重命名单个种子文件"
        }, {
            "path": "/batch_rename_torrents",
            "endpoint": self.batch_rename_torrents,
            "auth": "bear",
            "methods": ["POST"],
            "summary": "批量重命名种子",
            "description": "批量重命名种子文件"
        }, {
            "path": "/get_config",
            "endpoint": self._get_config,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取插件配置",
            "description": "获取插件当前配置"
        }, {
            "path": "/rename_history",
            "endpoint": self.get_rename_history,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取重命名历史",
            "description": "获取种子重命名历史记录"
        }, {
            "path": "/delete_rename_history",
            "endpoint": self.delete_rename_history,
            "auth": "bear",
            "methods": ["POST"],
            "summary": "删除重命名历史记录",
            "description": "删除指定的重命名历史记录"
        }, {
            "path": "/rename_index",
            "endpoint": self.get_rename_index,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取重命名索引",
            "description": "获取重命名历史记录索引缓存"
        }, {
            "path": "/update_rename_index",
            "endpoint": self.update_rename_index,
            "auth": "bear",
            "methods": ["POST"],
            "summary": "更新重命名索引",
            "description": "更新重命名历史记录索引缓存并应用重命名"
        }]

    def get_form(self):
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """

        return None, {
            "enabled": False,
            "notify": False,
            "cron_enabled": False,
            "downloader": [],
            "exclude_dirs": "",
            "hash_white_list": "",
            "exclude_tags": "已重命名",
            "include_tags": "",
            "cron": "",
            "retry": False,
            "event_enabled": False,
            "format_torrent_name": "{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}",
            "add_tag_after_rename": False
        }

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify
        :return: 2、组件路径，默认 dist/assets
        """
        return "vue", "dist/assets"

    def get_page(self) -> Optional[List[dict]]:
        """Vue mode doesn't use Vuetify page definitions."""
        return None

    def get_dashboard(self, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any], List[dict]]:
        """
        获取仪表盘页面
        """
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        if self._enabled and self._cron_enabled:
            return [
                {
                    "id": "RenameTorrentVue",
                    "name": "种子重命名格式化",
                    "trigger": CronTrigger.from_crontab(self._cron or "0 8 * * *"),
                    "func": self.cron_process_main,
                    "kwargs": {},
                }
            ]
        return []

    def stop_service(self):
        """退出插件"""
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"退出插件失败：{str(e)}", exc_info=True)

    def _get_config(self):
        """
        获取插件配置
        """
        # 获取系统中已启用的下载器
        downloaders_config = SystemConfigOper().get(SystemConfigKey.Downloaders) or []
        _downloaders = [
            {"title": d.get("name"), "value": d.get("name")}
            for d in downloaders_config if d.get("enabled")
        ]

        return {
            "id": "RenameTorrentVue",
            "name": "重命名种子文件Vue版",
            "enabled": self._enabled,
            "notify": self._notify,
            "event_enabled": self._event_enabled,
            "cron_enabled": self._cron_enabled,
            "downloader": self._downloader,  # 兼容Vue前端
            "all_downloaders": _downloaders,
            "format_torrent_name": self._format_torrent_name,
            "exclude_tags": self._exclude_tags,
            "include_tags": self._include_tags,
            "exclude_dirs": self._exclude_dirs,
            "hash_white_list": self._hash_white_list,
            "add_tag_after_rename": self._add_tag_after_rename,
            "onlyonce": self._onlyonce,
            "recovery": self._recovery,
            "retry": self._retry,
            "cron": self._cron
        }

    def get_rename_history(self):
        """
        获取重命名历史记录
        """
        # 从插件数据中获取历史记录
        history = self.get_data(key="rename_history") or []
        # 按时间倒序排列
        history.sort(key=lambda x: x.get("date", ""), reverse=True)
        return history

    def get_rename_index(self):
        """
        获取重命名历史记录索引缓存
        """
        # 获取索引缓存
        index = self.__get_rename_history_index()
        # 转换为列表格式便于前端显示
        return [
            {"original_name": k, "after_name": v.get("after_name", "") if isinstance(v, dict) else ""}
            for k, v in index.items()
        ]

    def list_torrents(self):
        """
        获取种子列表
        """
        if not self._downloader:
            return []

        # 获取所有下载器实例
        torrent_list = []
        for downloader_name in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
            downloader_instance = self.__get_downloader_instance(downloader_name)
            if not downloader_instance:
                logger.warn(f"下载器 {downloader_name} 未找到或未启用")
                continue

            # 获取种子列表
            torrents = downloader_instance.get_torrents()
            if not torrents:
                continue

            # 转换为前端需要的格式
            for torrent in torrents:
                # 获取种子信息
                torrent_info = self.__convert_torrent_info(torrent, downloader_instance.type)
                if torrent_info:
                    torrent_list.append(torrent_info)

        return torrent_list

    def rename_torrent(self, hash: str, new_name: str):
        """
        重命名单个种子
        :param hash: 种子hash
        :param new_name: 新名称
        """
        if not self._downloader:
            return {
                "success": False,
                "message": "未配置下载器"
            }

        # 遍历所有下载器查找种子
        downloader_instance = None
        downloader_name = None
        torrent_info = None

        for name in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
            instance = self.__get_downloader_instance(name)
            if not instance:
                continue

            # 获取种子信息
            torrents = instance.torrents_info(torrent_hash=hash)
            if torrents:
                downloader_instance = instance
                downloader_name = name
                torrent_info = torrents[0]
                break

        if not downloader_instance or not torrent_info:
            return {
                "success": False,
                "message": "未找到指定种子"
            }

        try:
            original_name = torrent_info.name

            # 执行重命名操作
            success = downloader_instance.rename_torrent(hash, new_name)

            # 记录历史
            self.__record_rename_history(
                hash=hash,
                original_name=original_name,
                after_name=new_name if success else original_name,
                success=success,
                downloader_name=downloader_name
            )

            if success:
                # 如果设置了添加标签，则添加标签
                if self._add_tag_after_rename:
                    downloader_instance.add_torrent_tag(hash, "已重命名")

                return {
                    "success": True,
                    "message": "重命名成功"
                }
            else:
                return {
                    "success": False,
                    "message": "重命名失败，可能是下载器不支持该操作"
                }
        except Exception as e:
            logger.error(f"重命名种子失败：{str(e)}")
            # 记录失败历史
            self.__record_rename_history(
                hash=hash,
                original_name=original_name if 'original_name' in locals() else "Unknown",
                after_name=new_name,
                success=False,
                downloader_name=downloader_name
            )
            return {
                "success": False,
                "message": f"重命名失败：{str(e)}"
            }

    def batch_rename_torrents(self, hashes: List[str]):
        """
        批量重命名种子
        :param hashes: 种子hash列表
        """
        if not self._downloader:
            return {
                "success": False,
                "message": "未配置下载器"
            }

        success_count = 0
        failed_count = 0
        failed_details = []

        # 遍历所有下载器
        for downloader_name in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
            # 获取下载器实例
            downloader_instance = self.__get_downloader_instance(downloader_name)
            if not downloader_instance:
                logger.warn(f"下载器 {downloader_name} 未找到或未启用")
                continue

            # 获取所有种子信息
            all_torrents = downloader_instance.get_torrents()
            torrent_dict = {t.hash: t for t in all_torrents} if all_torrents else {}

            # 遍历要重命名的种子
            for hash_value in hashes:
                # 检查该种子是否属于当前下载器
                if hash_value not in torrent_dict:
                    continue

                try:
                    torrent = torrent_dict[hash_value]
                    original_name = torrent.name

                    # 获取元数据和媒体信息
                    meta = MetaInfo(torrent.name)
                    media_info = self.chain.recognize_media(meta=meta)

                    if not media_info:
                        failed_count += 1
                        failed_details.append(f"种子 {torrent.name} 无法识别媒体信息")
                        # 记录失败历史
                        self.__record_rename_history(
                            hash=hash_value,
                            original_name=original_name,
                            after_name=original_name,
                            success=False,
                            downloader_name=downloader_name
                        )
                        continue

                    # 格式化新名称
                    new_name = self.__format_torrent_name(meta, media_info)
                    if not new_name or new_name == torrent.name:
                        failed_count += 1
                        failed_details.append(f"种子 {torrent.name} 格式化名称失败或名称未改变")
                        # 记录失败历史
                        self.__record_rename_history(
                            hash=hash_value,
                            original_name=original_name,
                            after_name=original_name,
                            success=False,
                            downloader_name=downloader_name
                        )
                        continue

                    # 执行重命名操作
                    success = downloader_instance.rename_torrent(hash_value, new_name)
                    if success:
                        # 如果设置了添加标签，则添加标签
                        if self._add_tag_after_rename:
                            downloader_instance.add_torrent_tag(hash_value, "已重命名")
                        success_count += 1

                        # 记录成功历史
                        self.__record_rename_history(
                            hash=hash_value,
                            original_name=original_name,
                            after_name=new_name,
                            success=True,
                            downloader_name=downloader_name
                        )
                    else:
                        failed_count += 1
                        failed_details.append(f"种子 {torrent.name} 重命名失败")

                        # 记录失败历史
                        self.__record_rename_history(
                            hash=hash_value,
                            original_name=original_name,
                            after_name=new_name,
                            success=False,
                            downloader_name=downloader_name
                        )

                except Exception as e:
                    failed_count += 1
                    failed_details.append(f"种子 {hash_value} 处理异常：{str(e)}")

        return {
            "success": True,
            "message": f"批量重命名完成，成功 {success_count} 个，失败 {failed_count} 个",
            "details": {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_details": failed_details
            }
        }

    def __record_rename_history(self, hash: str, original_name: str, after_name: str, success: bool, downloader_name: str = None):
        """
        记录重命名历史
        """
        # 获取现有历史记录
        history = self.get_data(key="rename_history") or []

        # 创建新的历史记录
        record = {
            "hash": hash,
            "original_name": original_name,
            "after_name": after_name,
            "success": success,
            "downloader": downloader_name or "",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 添加到历史记录开头
        history.insert(0, record)

        # 保存历史记录
        self.save_data(key="rename_history", value=history)

        # 更新索引缓存
        if self._rename_history_index is not None:
            if success and original_name:
                # 如果是成功的记录，添加到索引中
                if original_name in self._rename_history_index:
                    # 如果已存在该原始名称，更新重命名后名称，并添加hash到列表中
                    self._rename_history_index[original_name]["after_name"] = after_name
                    hash_list = self._rename_history_index[original_name]["hash"]
                    if isinstance(hash_list, list):
                        hash_list.append(hash)
                    else:
                        self._rename_history_index[original_name]["hash"] = [hash_list, hash]
                else:
                    # 如果不存在该原始名称，创建新的条目
                    self._rename_history_index[original_name] = {
                        "after_name": after_name,
                        "hash": [hash]
                    }

                # 更新已重命名名称缓存
                if self._renamed_names_cache is not None:
                    self._renamed_names_cache.add(after_name)
            elif not success and original_name and original_name in self._rename_history_index:
                # 如果是失败的记录，且索引中有对应的项，则移除
                self._rename_history_index.pop(original_name, None)

    def __build_rename_history_index(self) -> Dict[str, Dict[str, Union[str, List[str]]]]:
        """
        构建重命名历史记录索引字典
        :return: 以原始名称为键，包含重命名后名称和hash值列表的字典
        """
        # 获取历史记录
        history = self.get_data(key="rename_history") or []

        # 按原始名称分组记录
        grouped_records = {}
        for record in history:
            if record.get("success") and record.get("original_name"):
                original_name = record.get("original_name")
                grouped_records.setdefault(original_name, []).append(record)

        # 构建以原始名称为键的成功记录索引字典，包含重命名后名称和hash值列表
        history_index = {
            original_name: {
                "after_name": records[-1].get("after_name"),  # 最新的一条记录的重命名后名称
                "hash": [record.get("hash", "") for record in records]  # 所有记录的hash值列表
            }
            for original_name, records in grouped_records.items()
        }

        # 重置已重命名名称缓存
        self._renamed_names_cache = None

        return history_index

    def __get_rename_history_index(self) -> Dict[str, Dict[str, Union[str, List[str]]]]:
        """
        获取重命名历史记录索引字典（带缓存）
        :return: 以原始名称为键，包含重命名后名称和hash值列表的字典
        """
        # 如果索引尚未构建，则构建索引
        if self._rename_history_index is None:
            self._rename_history_index = self.__build_rename_history_index()
        return self._rename_history_index

    def __build_renamed_names_cache(self) -> Set[str]:
        """
        构建已重命名的种子名称缓存
        :return: 包含所有已重命名后名称的集合
        """
        # 获取历史记录
        history = self.get_data(key="rename_history") or []

        # 构建已重命名名称的集合
        return {record.get("after_name") for record in history
                if record.get("success") and record.get("after_name")}

    def __get_renamed_names_cache(self) -> Set[str]:
        """
        获取已重命名的种子名称缓存（带缓存）
        :return: 包含所有已重命名后名称的集合
        """
        # 如果缓存尚未构建，则构建缓存
        if self._renamed_names_cache is None:
            self._renamed_names_cache = self.__build_renamed_names_cache()
        return self._renamed_names_cache

    def __get_processed_from_history(self) -> Set[str]:
        """
        从重命名历史记录中获取已成功处理的记录，构建processed集合
        :return: 包含已处理的hash值的集合
        """
        history = self.get_data(key="rename_history") or []
        return {record["hash"] for record in history
                if record.get("success") and record.get("hash")}

    def __get_pending_from_history(self) -> Set[str]:
        """
        从重命名历史记录中获取处理失败的记录，构建pending集合
        :return: 包含处理失败的hash值的集合
        """
        history = self.get_data(key="rename_history") or []
        return {record["hash"] for record in history
                if not record.get("success") and record.get("hash")}

    def __get_downloader_instance(self, downloader_name: str):
        """
        获取下载器实例
        """
        service = self.downloader_helper.get_service(downloader_name)
        if not service or not service.instance:
            return None

        # 检查是否为Qbittorrent下载器
        if self.downloader_helper.is_downloader("qbittorrent", service.config):
            return QbittorrentDownloader(qbc=service.instance)

        logger.info("只支持QB下载器")
        return None

    def __convert_torrent_info(self, torrent, downloader_type: str):
        """
        转换种子信息为前端需要的格式
        """
        try:
            if downloader_type == "qbittorrent":
                return {
                    "hash": torrent.hash,
                    "name": torrent.name,
                    "title": torrent.name,
                    "size": torrent.total_size,
                    "progress": getattr(torrent, 'progress', 0),
                    "state": getattr(torrent, 'state', ''),
                    "tags": torrent.tags.split(',') if torrent.tags else [],
                    "save_path": torrent.save_path
                }
            elif downloader_type == "transmission":
                return {
                    "hash": torrent.hashString,
                    "name": torrent.name,
                    "title": torrent.name,
                    "size": torrent.totalSize,
                    "progress": torrent.percentDone * 100 if torrent.percentDone else 0,
                    "state": "downloading" if torrent.status == 4 else "paused" if torrent.status == 0 else "completed",
                    "tags": torrent.labels if torrent.labels else [],
                    "save_path": torrent.downloadDir
                }
        except Exception as e:
            logger.debug(f"转换种子信息失败：{str(e)}")
            return None

        return None

    def __format_torrent_name(self, meta: MetaInfo, media_info) -> Optional[str]:
        """
        格式化种子名称
        """
        if not self._format_torrent_name:
            return None

        try:
            handler = TransHandler()
            rename_dict = handler.get_naming_dict(meta=meta, mediainfo=media_info)
            new_name = handler.get_rename_path(self._format_torrent_name, rename_dict)
            return new_name
        except Exception as e:
            logger.error(f"格式化种子名称失败：{str(e)}")
            return None

    def set_downloader(self, downloader: str):
        """
        获取下载器
        """
        if service := self.downloader_helper.get_service(name=downloader):
            is_qbittorrent = self.downloader_helper.is_downloader("qbittorrent", service.config)
            if is_qbittorrent:
                self.downloader = QbittorrentDownloader(qbc=service.instance)
            else:
                self.downloader: None
                logger.info("只支持QB下载器")
        else:
            # 暂时设为None, 跳过
            self.downloader = None

    def update_data(self, key: str, value: dict = None):
        """
        更新插件数据
        """
        if not value:
            return
        plugin_data: dict = self.get_data(key=key)
        if plugin_data and isinstance(plugin_data, dict):
            plugin_data.update(value)
            self.save_data(key=key, value=plugin_data)
        else:
            self.save_data(key=key, value=value)

    def format_torrent(self, torrent_info: TorrentInfoRT, meta: MetaBase, media_info: MediaInfo, downloader: str = None) -> bool:
        _torrent_hash = torrent_info.hash
        _torrent_name = torrent_info.name
        success = True

        # 直接执行重命名逻辑，历史记录检查已在main方法中完成
        new_name = self.format_torrent_name(
            template_string=self._format_torrent_name,
            meta=meta,
            mediainfo=media_info)

        logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 重命名种子名称:{new_name}")
        try:
            if None != new_name and None != _torrent_name and str(new_name) != _torrent_name :
                self.downloader.torrents_rename(torrent_hash=_torrent_hash, new_torrent_name=str(new_name))
                logger.info(f"种子重命名成功 hash: {_torrent_hash} {_torrent_name} ==> {new_name}")
                # 记录重命名历史
                self.__record_rename_history(
                    hash=_torrent_hash,
                    original_name=torrent_info.name,  # 这里应该是种子的原始名称，但在当前上下文中我们只有当前名称
                    after_name=new_name,
                    success=True,
                    downloader_name=downloader
                )
            else:
                if None == _torrent_name:
                    logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：种子名字为None")
                if None == new_name:
                    logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：新名字为None")
                if str(new_name) == _torrent_name:
                    logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：新名字与原来的名字相同")
                success = False

                # 记录重命名失败历史
                if _torrent_name is not None and new_name is not None:
                    self.__record_rename_history(
                        hash=_torrent_hash,
                        original_name=torrent_info.name,
                        after_name=new_name if new_name is not None else _torrent_name,
                        success=False,
                        downloader_name=downloader if downloader else "未知"
                    )
        except Exception as e:
            logger.error(f"种子重命名失败 hash: {_torrent_hash} {str(e)}", exc_info=True)
            success = False

            # 记录重命名异常历史
            self.__record_rename_history(
                hash=_torrent_hash,
                original_name=torrent_info.name,
                after_name=new_name if 'new_name' in locals() else _torrent_name,
                success=False,
                downloader_name=downloader if downloader else "未知"
            )
        return success

    @staticmethod
    def format_torrent_name(
            template_string: str,
            meta: MetaBase,
            mediainfo: MediaInfo,
            file_ext: str = None,
    ) -> str:
        """
        根据媒体信息，返回Format字典
        :param template_string: Jinja2 模板字符串
        :param meta: 文件元数据
        :param mediainfo: 识别的媒体信息
        :param file_ext: 文件扩展名
        """
        def format_dict(meta: MetaBase, mediainfo: MediaInfo, file_ext: str = None) -> Dict[str, Any]:
            handler = TransHandler()
            return handler.get_naming_dict(
                meta=meta, mediainfo=mediainfo, file_ext=file_ext)
        # 处理mp的历史记录种子名称
        logger.debug(f"处理前的种子名称:{meta.title}")
        # 移除可能的前缀（如 [站点名] 或 [标签]）及其后的分隔符（如空格、点等）
        # 这个模式匹配以 [ 开头，] 结尾的标签，后面可能跟着空格或点
        prefix_pattern = r'^\[.*?\][\s.]*'
        processed_title = re.sub(prefix_pattern, '', meta.title)

        # 移除末尾的 .torrent 后缀（如果存在）
        processed_title = re.sub(r'\.torrent$', '', processed_title)

        # 去除首尾的空白字符和可能的点（以防移除前缀后开头仍有分隔符）
        processed_title = processed_title.strip(' .')
        logger.debug(f"处理后的种子名称:{processed_title}")
        rename_dict = format_dict(meta=meta, mediainfo=mediainfo, file_ext=file_ext)
        logger.debug(f"rename_dict： {rename_dict}")
        handler = TransHandler()
        path = handler.get_rename_path(template_string, rename_dict)
        return path.as_posix() if path else None

    def recoveryTorrent(self):
        """
        恢复下载器中的种子名称
        """
        try:
            # 获取已处理数据
            history = self.get_data(key="rename_history") or []
            processed_records = {record["hash"]: record for record in history if record.get("success")}

            logger.debug(f"processed records count: {len(processed_records)}")
            if len(processed_records) == 0:
                logger.debug(f"历史记录为空，跳过恢复")
                return
            logger.debug(f"获取已处理数据成功")
            # 从下载器获取种子信息
            # 确保_downloader是列表格式
            downloader_list = self._downloader if isinstance(self._downloader, list) else [self._downloader] if self._downloader else []

            for d in downloader_list:
                self.set_downloader(d)
                if self.downloader is None:
                    logger.warn(f"下载器: {d} 不存在或未启用")
                    continue
                if self._hash_white_list:
                    logger.debug(f"存在hash白名单")
                    torrents_info_list = self.downloader.torrents_info(torrent_hash=self._hash_white_list.strip().split("\n"))
                    logger.debug(f"白名单内的种子 torrents_info_list{torrents_info_list}")
                else:
                    torrents_info_list = self.downloader.torrents_info(torrent_hash=processed_records.keys())
                for torrent_info in torrents_info_list:
                    if torrent_info:
                        torrent_hash = torrent_info.hash
                        torrent_name = torrent_info.name

                        # 从历史记录中获取原始名称
                        original_name = processed_records.get(torrent_hash, {}).get("original_name")
                        if original_name:
                            self.downloader.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=str(original_name))
                            logger.info(f"种子恢复成功 hash: {torrent_hash} {torrent_name} ==> {original_name}")

                            # 记录恢复历史
                            self.__record_rename_history(
                                hash=torrent_hash,
                                original_name=torrent_name,
                                after_name=original_name,
                                success=True,
                                downloader_name=d.name
                            )
                        else:
                            logger.debug(f"恢复处理记录: hash: {torrent_hash} 找不到原始名称,")
            logger.info(f"恢复完成")
        except Exception as e:
            logger.error(f"恢复下载器中的种子名称失败 {str(e)}", exc_info=True)

    def cron_process_main(self):
        """
        定时任务处理下载器中的种子
        """
        try:
            if not self._downloader:
                logger.info("下载器为空")
                return
            # 失败数据列表
            _failures: dict[str, str] = {}
            # 获取待处理数据
            pending: set[str] = self.__get_pending_from_history()
            # 获取已处理数据
            processed: set[str] = self.__get_processed_from_history()
            _processed_num = 0

            def create_hash_mapping() -> Dict[str, List[str]]:
                """
                生成源种子hash表
                """
                # 辅种插件数据
                assist: List[PluginData] = self.get_data(key=None, plugin_id="IYUUAutoSeed") or []
                # 辅种数据映射表 key: 源种hash, value: 辅种hash列表
                _mapping: dict[str, List[str]] = {}

                if assist:
                    for seed_data in assist:
                        hashes = []
                        for a in seed_data.value:
                            hashes.extend(a.get("torrents", []))
                        if seed_data.key in _mapping:
                            # 辅种插件中使用的源种子hash是下载的, 将辅种hash列表合并
                            _mapping[seed_data.key].extend(hashes)
                        else:
                            # 辅种插件中使用的源种子hash不是字典的键, 需要再次判断是不是辅种产生的种子
                            for _current_hash, _hashes in _mapping.items():
                                if seed_data.key in _hashes:
                                    _mapping[_current_hash].extend(hashes)
                                    break
                            # 不是辅种产生的种子, 作为源种子添加
                            _mapping[seed_data.key] = hashes
                return _mapping

            # 先生成源种子hash表
            logger.debug(f"先生成源种子hash表")
            assist_mapping = create_hash_mapping()
            # 从下载器获取种子信息
            for d in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
                self.set_downloader(d)
                if self.downloader is None:
                    logger.info(f"下载器: {d} 不存在或未启用")
                    continue
                # 判断是否尝试失败的种子
                if self._retry:
                    logger.debug(f"尝试失败的种子")
                    torrents_info = [torrent_info for torrent_info in self.downloader.torrents_info() if torrent_info.hash not in processed]
                else:
                    logger.debug(f"不尝试失败的种子")
                    torrents_info = [torrent_info for torrent_info in self.downloader.torrents_info() if torrent_info.hash not in processed and torrent_info.hash not in pending]
                    # 判断是否在白名单内
                if self._hash_white_list:
                    logger.debug(f"存在hash白名单")
                    torrents_info = self.downloader.torrents_info(torrent_hash=self._hash_white_list.strip().split("\n"))
                    logger.debug(f"白名单内的种子 torrents_info：{torrents_info}")
                if torrents_info:
                    for torrent_info in torrents_info:
                        # 检查当前种子名称是否与历史记录中的原始名称匹配
                        history_index = self.__get_rename_history_index()
                        cached_entry = history_index.get(torrent_info.name)

                        if cached_entry:
                            success = self._apply_cached_rename(torrent_info, cached_entry, d)
                            if success:
                                continue
                        renamed_names_cache = self.__get_renamed_names_cache()
                        if torrent_info.name in renamed_names_cache:
                            logger.info(f"种子 {torrent_info.name} 已经重命名过，跳过处理")
                            continue
                        _hash = ""
                        if assist_mapping:
                            logger.debug(f"存在IYUU辅种数据")
                            for source_hash, seeds in assist_mapping.items():
                                if torrent_info.hash in seeds:
                                    # 使用源下载种子识别
                                    logger.debug(f"查找到 {torrent_info.name} hash:{torrent_info.hash} 的IYUU辅种记录")
                                    logger.debug(f"{torrent_info.name} hash:{torrent_info.hash} 源hash:{source_hash} ")
                                    _hash = source_hash
                                    break
                        # 通过hash查询下载历史记录
                        result_hash = _hash or torrent_info.hash
                        logger.debug(f"通过hash查询下载历史记录开始 hash：{result_hash}")
                        downloadhis = DownloadHistoryOper().get_by_hash(result_hash)
                        if downloadhis:
                            logger.debug(f"通过hash查询下载历史记录完成 hash:{result_hash} his_id:{downloadhis.id} his_hash:{downloadhis.download_hash}")
                        else:
                            logger.debug(f"未查询到下载历史记录 hash:{result_hash}")
                        # 执行处理
                        if self.main(downloader=d, torrent_info=torrent_info, downloadhis=downloadhis ):
                            # 添加到已处理数据库
                            processed.add(torrent_info.hash)
                            _failures.pop(torrent_info.hash, None)
                            # 本次处理成功计数
                            _processed_num += 1
                        else:
                            # 添加到失败数据库
                            _failures[torrent_info.hash] = d
            if _failures:
                logger.info(f"失败 {len(_failures)} 个")
            if processed:
                logger.info(f"成功 {_processed_num} 个, 合计 {len(processed)} 个种子已保存至历史")
            logger.info(f"运行完成")
        except Exception as e:
            logger.error(f"种子重命名失败 {str(e)}", exc_info=True)

    @eventmanager.register(EventType.DownloadAdded)
    def event_process_main(self, event: Event):
        """
        处理下载添加事件
        """
        if not self._enabled or not self._event_enabled or not event:
            return

        if not self._downloader:
            logger.info("下载器为空")
            return

        event_data = event.event_data or {}
        hash = event_data.get("hash")
        downloader = event_data.get("downloader")

        # 获取待处理数据
        if self._event_enabled and downloader in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
            context: Context = event_data.get("context")
            self.main(downloader=downloader, hash=hash, meta=context.meta_info, media_info=context.media_info)

    def main(self, downloader: str = None, downloadhis: DownloadHistory = None,
             hash: str =None, torrent_info: TorrentInfoRT = None,
             meta: MetaBase = None, media_info: MediaInfo = None) -> bool:
        """
        处理单个种子
        :param downloader: 下载器名称
        :param hash: 种子哈希
        :param torrent_info: 种子信息
        :param meta: 文件元数据
        :param media_info: 媒体信息
        :return: 处理结果
        """
        success = True
        if downloader:
            # 设置下载器
            self.set_downloader(downloader)

        if self.downloader is None:
            logger.warn(f"未连接下载器")
            return False

        if not torrent_info and hash:
            torrent_info = self.downloader.torrents_info(torrent_hash=hash)
            # 种子被手动删除或转移
            if not torrent_info:
                logger.warn(f"下载器 {downloader} 不存在该种子: {hash}")
                return True
                # 取第一个种子
                torrent_info = torrent_info[0]

                # 检查种子是否已经被重命名过
                renamed_names_cache = self.__get_renamed_names_cache()
                if torrent_info.name in renamed_names_cache:
                    logger.info(f"种子 {torrent_info.name} 已经重命名过，跳过处理")
                    return True

                # 通过索引字典直接查找历史记录，时间复杂度O(1)
                history_index = self.__get_rename_history_index()
                cached_entry = history_index.get(torrent_info.name)

                # 如果在历史记录中找到了对应的重命名后名称，则直接使用
                if cached_entry:
                    return self._apply_cached_rename(torrent_info, cached_entry, downloader)
        # 保存目录排除
        if success and self._exclude_dirs:
            for exclude_dir in self._exclude_dirs.split("\n"):
                if exclude_dir and exclude_dir in str(torrent_info.save_path):
                    success = False
                    logger.info(f"{torrent_info.name} 保存路径: {torrent_info.save_path} 命中排除目录：{exclude_dir}")
                    return True
        # 标签排除
        if success and self._exclude_tags and \
                (common_tags := {tag.strip() for tag in self._exclude_tags.split(",") if tag} & {tag.strip() for tag in torrent_info.tags}):
            success = False
            logger.info(f"{torrent_info.tags} 命中排除标签：{common_tags}")
            return True
        # 标签包含
        if success and self._include_tags and \
                not (common_tags := {tag.strip() for tag in self._include_tags.split(",") if tag} & {tag.strip() for tag in torrent_info.tags}):
            success = False
            logger.info(f"{torrent_info.tags} 未命中包含标签：{common_tags}")
            return True
        if success and downloadhis:
            # 使用历史记录的识别信息
            logger.debug(f"识别到MP 下载历史名称:{downloadhis.torrent_name}")
            meta = MetaInfo(title=downloadhis.torrent_name, subtitle=downloadhis.torrent_description)
            media_info = self.chain.recognize_media(meta=meta, mtype=MediaType(downloadhis.type),
                                                    tmdbid=downloadhis.tmdbid)
        if success and not meta:
            logger.info(f"未找到与之关联的下载种子 hash: {torrent_info.hash} 种子名称：{torrent_info.name} 元数据识别可能不准确")
            meta = MetaInfo(torrent_info.name)
            logger.debug(f"种子名称:{torrent_info.name}")
            if not meta:
                logger.error(f"元数据获取失败，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                success = False
        if success and not media_info:
            media_info = self.chain.recognize_media(meta=meta)
            # meta = MetaInfo(media_info.en_title)
            if not media_info:
                logger.error(f"识别媒体信息失败，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                success = False
        if success:
            logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 开始执行重命名")
            logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} torrent_info：{torrent_info} meta：{meta} media_info：{media_info}")
            if self.format_torrent(torrent_info=torrent_info, meta=meta, media_info=media_info, downloader=downloader):
                logger.info(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 处理完成")
                # 添加已重命名标签
                if self._add_tag_after_rename:
                    self.downloader.torrents_add_tags(torrent_info.hash,["已重命名"])
                return True
        # 处理失败
        return False

    def _apply_cached_rename(self, torrent_info: TorrentInfoRT, cached_entry: dict, downloader: str) -> bool:
        """
        应用缓存的重命名记录到种子
        :param torrent_info: 种子信息
        :param cached_entry: 缓存条目
        :param downloader: 下载器名称
        :return: 重命名是否成功
        """
        cached_name = cached_entry.get("after_name")
        logger.info(f"从历史记录中找到匹配项，直接使用历史重命名结果: {torrent_info.name} ==> {cached_name}")
        try:
            self.downloader.torrents_rename(torrent_hash=torrent_info.hash, new_torrent_name=str(cached_name))
            logger.info(f"种子重命名成功 hash: {torrent_info.hash} {torrent_info.name} ==> {cached_name}")

            # 添加已重命名标签
            if self._add_tag_after_rename:
                self.downloader.torrents_add_tags(torrent_info.hash, ["已重命名"])

            # 记录重命名历史
            self.__record_rename_history(
                hash=torrent_info.hash,
                original_name=torrent_info.name,
                after_name=cached_name,
                success=True,
                downloader_name=downloader
            )
            return True
        except Exception as e:
            logger.error(f"种子重命名失败 hash: {torrent_info.hash} {str(e)}", exc_info=True)
            # 记录重命名异常历史
            self.__record_rename_history(
                hash=torrent_info.hash,
                original_name=torrent_info.name,
                after_name=cached_name,
                success=False,
                downloader_name=downloader
            )
            return False

    def _rename_single_torrent(self, torrent_info: TorrentInfoRT, new_name: str, downloader_name: str) -> bool:
        """
        重命名单个种子
        :param torrent_info: 种子信息
        :param new_name: 新名称
        :param downloader_name: 下载器名称
        :return: 重命名是否成功
        """
        try:
            self.downloader.torrents_rename(torrent_hash=torrent_info.hash, new_torrent_name=str(new_name))
            logger.info(f"种子重命名成功 hash: {torrent_info.hash} {torrent_info.name} ==> {new_name}")

            # 添加已重命名标签
            if self._add_tag_after_rename:
                self.downloader.torrents_add_tags(torrent_hash=torrent_info.hash, tags=["已重命名"])

            # 记录重命名历史
            self.__record_rename_history(
                hash=torrent_info.hash,
                original_name=torrent_info.name,
                after_name=new_name,
                success=True,
                downloader_name=downloader_name
            )
            return True
        except Exception as e:
            logger.error(f"种子重命名失败 hash: {torrent_info.hash} {str(e)}", exc_info=True)
            # 记录重命名异常历史
            self.__record_rename_history(
                hash=torrent_info.hash,
                original_name=torrent_info.name,
                after_name=new_name,
                success=False,
                downloader_name=downloader_name
            )
            return False

    def _rename_torrents_with_new_name(self, original_name: str, new_name: str) -> int:
        """
        使用新名称重命名相关种子
        :param original_name: 原始名称
        :param new_name: 新名称
        :return: 成功重命名的种子数量
        """
        renamed_count = 0
        if not self._downloader:
            return renamed_count

        # 从索引缓存中获取所有相关的种子hash值
        cached_entry = self._rename_history_index.get(original_name, {})
        related_hashes = cached_entry.get("hash", []) if cached_entry else []

        # 确保related_hashes是列表格式
        if not isinstance(related_hashes, list):
            related_hashes = [related_hashes]

        # 遍历所有配置的下载器
        downloader_list = self._downloader if isinstance(self._downloader, list) else [self._downloader] if self._downloader else []
        for downloader_name in downloader_list:
            downloader_instance = self.__get_downloader_instance(downloader_name)
            if downloader_instance and related_hashes:
                # 直接通过hash值获取相关种子，避免遍历所有种子
                torrents = downloader_instance.torrents_info(torrent_hash=related_hashes)
                for torrent in torrents:
                    try:
                        downloader_instance.torrents_rename(torrent.hash, new_name)
                        renamed_count += 1

                        # 添加标签
                        if self._add_tag_after_rename:
                            downloader_instance.add_torrent_tag(torrent.hash, "已重命名")

                    except Exception as e:
                        logger.error(f"重命名种子失败: {str(e)}")

        return renamed_count

    def update_rename_index(self, request_body: dict):
        """
        更新重命名索引缓存中的条目，并对相关种子应用重命名

        :param request_body: 包含 original_name 和 after_name 的字典
        """
        original_name = request_body.get("original_name")
        after_name = request_body.get("after_name")
        try:
            # 更新内存中的索引缓存
            if self._rename_history_index is not None:
                if original_name in self._rename_history_index:
                    # 如果已存在该原始名称，更新重命名后名称
                    self._rename_history_index[original_name]["after_name"] = after_name
                else:
                    # 如果不存在该原始名称，创建新的条目
                    self._rename_history_index[original_name] = {
                        "after_name": after_name,
                        "hash": []  # update_rename_index 方法中不涉及具体的hash值
                    }

            # 获取所有历史记录
            history = self.get_data(key="rename_history") or []

            # 更新历史记录中的相关条目
            updated_count = 0
            for record in history:
                if record.get("original_name") == original_name and record.get("success"):
                    record["after_name"] = after_name
                    updated_count += 1

            # 保存更新后的历史记录
            self.save_data(key="rename_history", value=history)

            # 更新已重命名名称缓存
            if self._renamed_names_cache is not None:
                self._renamed_names_cache.add(after_name)

            # 对仍在下载器中的相关种子执行重命名操作
            renamed_count = self._rename_torrents_with_new_name(original_name, after_name)

            return {
                "success": True,
                "message": f"成功更新索引并重命名了 {renamed_count} 个种子",
                "updated_records": updated_count,
                "renamed_torrents": renamed_count
            }

        except Exception as e:
            logger.error(f"更新重命名索引失败: {str(e)}")
            return {
                "success": False,
                "message": f"更新重命名索引失败: {str(e)}"
            }

    def delete_rename_history(self, request_body: dict):
        """
        删除重命名历史记录
        :param request_body: 请求体，包含要删除的记录列表
        """
        try:
            # 获取要删除的记录列表
            records_to_delete = request_body.get("records", [])
            
            # 调试输出接收到的数据
            logger.debug(f"Received records to delete: {records_to_delete}")
            
            if not records_to_delete:
                return {
                    "success": False,
                    "message": "未提供要删除的记录"
                }
            
            # 获取现有历史记录
            history = self.get_data(key="rename_history") or []
            
            # 创建一个集合来存储要删除的记录的hash值
            hashes_to_delete = set()
            for record in records_to_delete:
                record_hash = record.get("hash")
                if record_hash:
                    hashes_to_delete.add(record_hash)
            
            # 调试输出要删除的hash
            logger.debug(f"Hashes to delete: {hashes_to_delete}")
            
            # 过滤掉要删除的记录
            remaining_history = []
            deleted_count = 0
            for record in history:
                record_hash = record.get("hash")
                if record_hash and record_hash in hashes_to_delete:
                    deleted_count += 1
                    logger.debug(f"Deleting record: {record}")
                else:
                    remaining_history.append(record)
            
            # 保存更新后的历史记录
            self.save_data(key="rename_history", value=remaining_history)
            
            # 重建相关缓存
            self._rename_history_index = None
            self._renamed_names_cache = None
            
            logger.debug(f"Deleted {deleted_count} records, {len(remaining_history)} records remaining")
            logger.debug("Rebuilt rename history index and renamed names cache")
            
            return {
                "success": True,
                "message": f"成功删除 {deleted_count} 条记录"
            }
            
        except Exception as e:
            logger.error(f"删除重命名历史记录失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除重命名历史记录失败: {str(e)}"
            }
