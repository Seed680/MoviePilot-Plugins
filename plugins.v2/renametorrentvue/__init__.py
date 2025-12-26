import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional, Union, Set

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.context import MediaInfo, Context
from app.core.event import eventmanager, Event
from app.core.meta.metabase import MetaBase
from app.core.metainfo import MetaInfo
from app.db.downloadhistory_oper import DownloadHistoryOper, DownloadHistory
from app.db.models.plugindata import PluginData
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.modules.filemanager.transhandler import TransHandler
from app.modules.qbittorrent import Qbittorrent
from app.plugins import _PluginBase
from app.schemas.types import EventType, MediaType, SystemConfigKey


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


class QbittorrentDownloader:
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
                # 安全获取标签列表
                tags_str = torrent_info.get('tags', '')
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []
                
                # 安全获取文件列表
                files = []
                torrent_files = torrent_info.get('files', [])
                if torrent_files:
                    for file in torrent_files:
                        files.append(TorrentFile(
                            name=file.get('name', ''),
                            size=file.get('size', 0),
                            priority=file.get('priority', 0)
                        ))
                
                torrents.append(TorrentInfoRT(
                    name = torrent_info.get('name', ''),
                    save_path = torrent_info.get('save_path', ''),
                    total_size = torrent_info.get('total_size', 0),
                    hash=torrent_info.get('hash', ''),
                    auto_tmm=torrent_info.get('auto_tmm', False),
                    category=torrent_info.get('category', ''),
                    tags=tags,
                    files=files
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

    def rename_torrent(self, torrent_hash: str, new_name: str):
        """
        重命名单个种子(Vue兼容方法)
        """
        try:
            self.torrents_rename(torrent_hash, new_name)
            return True
        except Exception as e:
            logger.error(f"重命名种子失败：{str(e)}")
            return False

    def add_torrent_tag(self, torrent_hash: str, tag: str):
        """
        添加标签(Vue兼容方法)
        """
        try:
            self.torrents_add_tags(torrent_hash, [tag])
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
    plugin_version = "1.0.2.1"
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
    # 电影格式化字符
    _movie_format_torrent_name: str = "{{ title }}{% if year %} ({{ year }}){% endif %} - {{original_name}}"
    # 剧集格式化字符
    _tv_format_torrent_name: str = "{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %} - {{original_name}}"
    # 下载器
    _downloader: list| str = []
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
    # 重命名历史记录字典缓存
    _rename_history_dict: Optional[Dict[str, Dict]] = None
    # 重命名历史记录字典是否已修改
    _rename_history_dict_dirty: bool = False

    downloader_helper = None
    downloadhis = None

    def __init__(self):
        super().__init__()
        # 初始化时加载缓存
        self.__load_rename_history_cache()
        # 初始化downloader属性
        self.downloader = None

    def __load_rename_history_cache(self):
        """
        加载重命名历史记录到缓存
        """
        history = self.get_data(key="rename_history") or []
        self._rename_history_dict = {record["hash"]: record for record in history}
        self._rename_history_dict_dirty = False

    def __get_rename_history_cache(self) -> Dict[str, Dict]:
        """
        获取重命名历史记录缓存
        :return: 以hash为键的历史记录字典
        """
        if self._rename_history_dict is None:
            self.__load_rename_history_cache()
        
        return self._rename_history_dict

    def __record_rename_history(self, torrent_hash: str, original_name: str, after_name: str, success: bool, downloader_name: str = None, reason: str = None):
        """
        记录重命名历史
        """
        # 添加到缓存
        self.__add_to_rename_history_cache(torrent_hash, original_name, after_name, success, downloader_name, reason)

    def __add_to_rename_history_cache(self, torrent_hash: str, original_name: str, after_name: str, success: bool, downloader_name: str = None, reason: str = None):
        """
        添加记录到重命名历史缓存
        """
        if self._rename_history_dict is None:
            self.__load_rename_history_cache()
        
        record = {
            "hash": torrent_hash,
            "original_name": original_name,
            "after_name": after_name,
            "success": success,
            "downloader": downloader_name or "",
            "reason": reason,  # 添加失败原因字段
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到缓存开头（按时间倒序）
        self._rename_history_dict[torrent_hash] = record
        self._rename_history_dict_dirty = True

    def __update_rename_history_status_by_hash(self, torrent_hash: str, success: bool):
        """
        更新重命名历史记录缓存中的状态
        :param torrent_hash: 种子hash
        :param success: 成功状态
        """
        if self._rename_history_dict is None:
            self.__load_rename_history_cache()
        
        # 检查指定hash的记录是否存在且状态需要更新
        if torrent_hash in self._rename_history_dict and self._rename_history_dict[torrent_hash].get("success") != success:
            # 更新状态
            self._rename_history_dict[torrent_hash]["success"] = success
            self._rename_history_dict[torrent_hash]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._rename_history_dict_dirty = True
            logger.info(f"更新历史记录状态: {torrent_hash}, 成功: {success}")

    def __delete_from_rename_history_cache(self, hashes_to_delete: Set[str]):
        """
        从重命名历史缓存中删除记录
        :param hashes_to_delete: 要删除的hash集合
        """
        if self._rename_history_dict is None:
            self.__load_rename_history_cache()
        
        # 从缓存中删除指定的记录
        for hash_to_delete in hashes_to_delete:
            if hash_to_delete in self._rename_history_dict:
                del self._rename_history_dict[hash_to_delete]
                self._rename_history_dict_dirty = True

    def __sync_rename_history_to_storage(self):
        """
        将缓存的历史记录同步到存储
        """
        if self._rename_history_dict_dirty and self._rename_history_dict is not None:
            # 将字典转换为列表格式并保存
            history_list = list(self._rename_history_dict.values())
            # 按时间倒序排列
            history_list.sort(key=lambda x: x.get("date", ""), reverse=True)
            self.save_data(key="rename_history", value=history_list)
            self._rename_history_dict_dirty = False
            logger.debug(f"已同步 {len(history_list)} 条历史记录到存储")

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
            self._scheduler.add_job(self.recovery_torrent, 'date',
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
                "movie_format_torrent_name",
                "tv_format_torrent_name",
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
            "movie_format_torrent_name": self._movie_format_torrent_name,
            "tv_format_torrent_name": self._tv_format_torrent_name,
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
        """Vue mode doesn0t use Vuetify page definitions."""
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
        finally:
            # 在插件停止时，将缓存同步到存储
            self.__sync_rename_history_to_storage()

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
            "movie_format_torrent_name": self._movie_format_torrent_name,
            "tv_format_torrent_name": self._tv_format_torrent_name,
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
        # 从缓存获取历史记录
        history_dict = self.__get_rename_history_cache()
        # 转换为列表并按时间倒序排列
        history_list = list(history_dict.values())
        history_list.sort(key=lambda x: x.get("date", ""), reverse=True)
        return history_list



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


    # 统一使用 __get_rename_history_cache 方法，删除重复的 __get_rename_history_dict 方法

    def __update_rename_history_status(self, torrent_hash: str, success: bool):
        """
        更新重命名历史记录中的状态
        :param torrent_hash: 种子hash
        :param success: 成功状态
        """
        # 获取历史记录字典
        history_dict = self.__get_rename_history_cache()

        # 检查指定hash的记录是否存在且状态需要更新
        if torrent_hash in history_dict and history_dict[torrent_hash].get("success") != success:
            # 更新状态
            history_dict[torrent_hash]["success"] = success
            history_dict[torrent_hash]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 将字典转换回列表格式并保存
            updated_history = list(history_dict.values())
            self.save_data(key="rename_history", value=updated_history)

            # 更新缓存，而不是清空它
            self._rename_history_dict = history_dict

            logger.info(f"更新历史记录状态: {torrent_hash}, 成功: {success}")

    def __update_rename_history_cache(self):
        """
        更新重命名历史记录缓存
        """
        history = self.get_data(key="rename_history") or []
        self._rename_history_dict = {record["hash"]: record for record in history}

    def __get_processed_from_history(self) -> Set[str]:
        """
        从重命名历史记录中获取已成功处理的记录，构建processed集合
        :return: 包含已处理的hash值的集合
        """
        history_dict = self.__get_rename_history_cache()
        return {hash_value for hash_value, record in history_dict.items()
                if record.get("success") and hash_value}

    def __get_pending_from_history(self) -> Set[str]:
        """
        从重命名历史记录中获取处理失败的记录，构建pending集合
        :return: 包含处理失败的hash值的集合
        """
        history_dict = self.__get_rename_history_cache()
        return {hash_value for hash_value, record in history_dict.items()
                if not record.get("success") and hash_value}

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

    def set_downloader(self, downloader: str):
        """
        获取下载器
        """
        if service := self.downloader_helper.get_service(name=downloader):
            is_qbittorrent = self.downloader_helper.is_downloader("qbittorrent", service.config)
            if is_qbittorrent:
                self.downloader = QbittorrentDownloader(qbc=service.instance)
            else:
                self.downloader = None
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

        # 直接执行重命名逻辑，历史记录检查已在main方法中完成
        # 区分电影和剧集使用不同模板
        if media_info.type == MediaType.MOVIE:
            # 使用电影格式化模板
            new_name = self.format_torrent_name(
                template_string=self._movie_format_torrent_name,
                meta=meta,
                mediainfo=media_info)
        else:
            # 使用剧集格式化模板
            new_name = self.format_torrent_name(
                template_string=self._tv_format_torrent_name,
                meta=meta,
                mediainfo=media_info)

        logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 重命名种子名称:{new_name}")
        
        try:
            # 检查是否满足重命名条件
            if new_name is None:
                reason = "新名字为None"
                logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：{reason}")
                self.__record_rename_history(
                    torrent_hash=_torrent_hash,
                    original_name=torrent_info.name,
                    after_name=_torrent_name,  # 新名字为None，所以after_name仍为原名
                    success=False,
                    downloader_name=downloader,
                    reason=reason
                )
                return False
            
            if _torrent_name is None:
                reason = "种子名字为None"
                logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：{reason}")
                self.__record_rename_history(
                    torrent_hash=_torrent_hash,
                    original_name=torrent_info.name,
                    after_name=torrent_info.name,
                    success=False,
                    downloader_name=downloader,
                    reason=reason
                )
                return False
            
            if str(new_name) == _torrent_name:
                reason = "新名字与原来的名字相同"
                logger.debug(f"种子重命名失败 hash: {_torrent_hash} {_torrent_name} 原因：{reason}")
                self.__record_rename_history(
                    torrent_hash=_torrent_hash,
                    original_name=torrent_info.name,
                    after_name=_torrent_name,
                    success=False,
                    downloader_name=downloader,
                    reason=reason
                )
                return False
            
            # 执行重命名
            self.downloader.torrents_rename(torrent_hash=_torrent_hash, new_torrent_name=str(new_name))
            logger.info(f"种子重命名成功 hash: {_torrent_hash} {_torrent_name} ==> {new_name}")
            
            # 记录重命名成功历史
            self.__record_rename_history(
                torrent_hash=_torrent_hash,
                original_name=torrent_info.name,
                after_name=new_name,
                success=True,
                downloader_name=downloader
            )
            
            return True
            
        except Exception as e:
            reason = f"重命名异常: {str(e)}"
            logger.error(f"种子重命名失败 hash: {_torrent_hash} {reason}", exc_info=True)
            
            # 记录重命名异常历史
            self.__record_rename_history(
                torrent_hash=_torrent_hash,
                original_name=torrent_info.name,
                after_name=new_name if new_name is not None else _torrent_name,
                success=False,
                downloader_name=downloader if downloader else "未知",
                reason=reason
            )
            
            return False

    @staticmethod
    def format_torrent_name(
            template_string: str,
            meta: MetaBase,
            mediainfo: MediaInfo,
            file_ext: str = None,
    ) -> Optional[str]:
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
        if meta and meta.title:
            logger.debug(f"处理前的种子名称:{meta.title}")
            # 移除可能的前缀（如 [站点名] 或 [标签]）及其后的分隔符（如空格、点等）
            # 这个模式匹配以 [ 开头，] 结尾的标签，后面可能跟着空格或点
            prefix_pattern = r'\[.*\][\s.]*'
            processed_title = re.sub(prefix_pattern, '', meta.title)

            # 移除末尾的 .torrent 后缀（如果存在）
            processed_title = re.sub(r'\.torrent$', '', processed_title)

            # 去除首尾的空白字符和可能的点（以防移除前缀后开头仍有分隔符）
            processed_title = processed_title.strip(' .')
            logger.debug(f"处理后的种子名称:{processed_title}")
            meta.title = processed_title
        else:
            logger.warning("meta或meta.title为None，跳过处理")
            return None
        rename_dict = format_dict(meta=meta, mediainfo=mediainfo, file_ext=file_ext)
        logger.debug(f"rename_dict： {rename_dict}")
        handler = TransHandler()
        path = handler.get_rename_path(template_string, rename_dict)
        return path.as_posix() if path else None

    def recovery_torrent(self):
        """
        恢复下载器中的种子名称
        """
        try:
            # 获取已处理数据
            history_dict = self.__get_rename_history_cache()
            processed_records = {hash_value: record for hash_value, record in history_dict.items() if record.get("success")}

            logger.debug(f"processed records count: {len(processed_records)}")
            if len(processed_records) == 0:
                logger.debug(f"历史记录为空，跳过恢复")
                return
            logger.debug(f"获取已处理数据成功")
            # 从下载器获取种子信息
            # 确保_downloader是列表格式
            downloader_list = self._downloader if isinstance(self._downloader, list) else [self._downloader] if self._downloader else []

            # 记录成功恢复的种子hash值
            recovered_hashes = set()

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
                    torrents_info_list = self.downloader.torrents_info(torrent_hash=list(processed_records.keys()))
                for torrent_info in torrents_info_list:
                    if torrent_info:
                        torrent_hash = torrent_info.hash
                        torrent_name = torrent_info.name

                        # 从历史记录中获取原始名称
                        original_name = processed_records.get(torrent_hash, {}).get("original_name")
                        if original_name:
                            self.downloader.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=str(original_name))
                            logger.info(f"种子恢复成功 hash: {torrent_hash} {torrent_name} ==> {original_name}")

                            # 记录成功恢复的hash
                            recovered_hashes.add(torrent_hash)
                        else:
                            logger.debug(f"恢复处理记录: hash: {torrent_hash} 找不到原始名称,")

            # 在所有恢复任务完成后，统一删除已恢复的记录
            if recovered_hashes:
                # 从缓存中删除已恢复的记录
                self.__delete_from_rename_history_cache(recovered_hashes)

                logger.info(f"已从历史记录中删除 {len(recovered_hashes)} 条已恢复的记录")

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
                    logger.info(f"本次 {d} 处理种子数量为: {len(torrents_info)}")
                    # 判断是否在白名单内
                if self._hash_white_list:
                    logger.debug(f"存在hash白名单")
                    torrents_info = self.downloader.torrents_info(torrent_hash=self._hash_white_list.strip().split("\n"))
                    logger.debug(f"白名单内的种子 torrents_info：{torrents_info}")
                if torrents_info:
                    for torrent_info in torrents_info:
                        # 已删除缓存相关代码
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
                        result = self.main(downloader=d, torrent_info=torrent_info, downloadhis=downloadhis)
                        if result.get("success"):
                            # 添加到已处理数据库
                            processed.add(torrent_info.hash)
                            _failures.pop(torrent_info.hash, None)
                            # 本次处理成功计数
                            _processed_num += 1

                            # 如果该种子之前失败过，现在成功了，需要更新历史记录中的状态为成功
                            # 使用缓存的历史记录字典
                            history_dict = self.__get_rename_history_cache()

                            # 检查当前种子是否在失败记录中
                            if torrent_info.hash in history_dict and history_dict[torrent_info.hash].get("success") == False:
                                # 更新该记录为成功状态
                                self.__update_rename_history_status_by_hash(torrent_info.hash, True)
                        else:
                            # 添加到失败数据库
                            _failures[torrent_info.hash] = result.get("message", "未知错误")
            if _failures:
                logger.info(f"失败 {len(_failures)} 个")
            if processed:
                logger.info(f"成功 {_processed_num} 个")
            logger.info(f"运行完成")
        except Exception as e:
            logger.error(f"种子重命名失败 {str(e)}", exc_info=True)
        finally:
            # 在程序结束时，将缓存同步到存储
            self.__sync_rename_history_to_storage()

    @eventmanager.register(EventType.DownloadAdded)
    def event_process_main(self, event: Event):
        """
        处理下载添加事件
        """
        if not self._enabled or not self._event_enabled or not event:
            return

        if not self._downloader:
            logger.info("下载器为空")
            self.__sync_rename_history_to_storage()
            return

        logger.debug(f"event:{event}")
        event_data = event.event_data or {}
        torrent_hash = event_data.get("hash")
        downloader = event_data.get("downloader")

        # 获取待处理数据
        if self._event_enabled and downloader in (self._downloader if isinstance(self._downloader, list) else [self._downloader]):
            context: Context = event_data.get("context")
            result = self.main(downloader=downloader, torrent_hash=torrent_hash, meta=context.meta_info, media_info=context.media_info)
            if not result.get("success"):
                logger.debug(f"事件处理失败: {result.get('message')}")

        # 在程序结束时，将缓存同步到存储
        self.__sync_rename_history_to_storage()

    def main(self, downloader: str = None, downloadhis: DownloadHistory = None,
             torrent_hash: str =None, torrent_info: TorrentInfoRT = None,
             meta: MetaBase = None, media_info: MediaInfo = None) -> dict:
        """
        处理单个种子
        :param downloader: 下载器名称
        :param downloadhis: mp下载历史记录
        :param torrent_hash: 种子哈希
        :param torrent_info: 种子信息
        :param meta: 文件元数据
        :param media_info: 媒体信息
        :return: 处理结果字典，包含success和message字段
        """
        success = True
        message = ""
        if downloader:
            # 设置下载器
            self.set_downloader(downloader)

        if self.downloader is None:
            logger.warn(f"未连接下载器")
            reason = "未连接下载器"
            # 记录失败历史
            original_name = torrent_info.name if torrent_info else "unknown"
            self.__record_rename_history(
                torrent_hash=torrent_hash or "unknown",
                original_name=original_name,
                after_name=original_name,  # 未成功重命名，所以after_name与original_name相同
                success=False,
                downloader_name=downloader or "未知",
                reason=reason
            )
            return {"success": False, "message": reason}

        if not torrent_info and torrent_hash:
            torrent_info = self.downloader.torrents_info(torrent_hash=torrent_hash)
            # 种子被手动删除或转移
            if not torrent_info:
                reason = f"下载器 {downloader} 不存在该种子: {torrent_hash}"
                logger.warn(reason)

                return {"success": False, "message": reason}
            # 取第一个种子
            torrent_info = torrent_info[0]

        # 保存目录排除
        if success and self._exclude_dirs:
            for exclude_dir in self._exclude_dirs.split("\n"):
                if exclude_dir and exclude_dir in str(torrent_info.save_path):
                    success = False
                    reason = f"保存路径命中排除目录：{exclude_dir}"
                    message = reason
                    logger.info(f"{torrent_info.name} 保存路径: {torrent_info.save_path} {reason}")
                    return {"success": False, "message": message}
        # 标签排除
        if success and self._exclude_tags and \
                (common_tags := {tag.strip() for tag in self._exclude_tags.split(",") if tag} & {tag.strip() for tag in torrent_info.tags}):
            success = False
            reason = f"命中排除标签：{common_tags}"
            message = reason
            logger.info(f"{torrent_info.name}  {torrent_info.tags} {reason}")
            return {"success": False, "message": message}
        # 标签包含
        if success and self._include_tags and \
                not (common_tags := {tag.strip() for tag in self._include_tags.split(",") if tag} & {tag.strip() for tag in torrent_info.tags}):
            success = False
            reason = f"未命中包含标签：{common_tags}"
            message = reason
            logger.info(f"{torrent_info.name}  {torrent_info.tags} {reason}")
            return {"success": False, "message": message}
        if success and downloadhis:
            # 使用历史记录的识别信息
            logger.debug(f"识别到MP 下载历史名称:{downloadhis.torrent_name}")
            meta = MetaInfo(title=downloadhis.torrent_name, subtitle=downloadhis.torrent_description)
            media_info = self.chain.recognize_media(meta=meta, mtype=MediaType(downloadhis.type),
                                                    tmdbid=downloadhis.tmdbid)
            if not media_info:
                success = False
                reason = f"识别媒体信息失败，下载历史: {downloadhis.torrent_name}"
                message = reason
                logger.error(f"{reason}，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                # 记录失败历史
                self.__record_rename_history(
                    torrent_hash=torrent_info.hash,
                    original_name=torrent_info.name,
                    after_name=torrent_info.name,  # 名称未改变
                    success=False,
                    downloader_name=downloader or "未知",
                    reason=reason
                )
                return {"success": False, "message": message}
        if success and not meta:
            logger.info(f"未找到与之关联的下载种子 hash: {torrent_info.hash} 种子名称：{torrent_info.name} 元数据识别可能不准确")
            meta = MetaInfo(torrent_info.name)
            logger.debug(f"种子名称:{torrent_info.name}")
            if not meta or not meta.title:  # 检查meta对象和其title属性
                success = False
                reason = f"元数据获取失败，种子名称：{torrent_info.name}"
                message = reason
                logger.error(f"{reason}，hash: {torrent_info.hash}")
                # 记录失败历史
                self.__record_rename_history(
                    torrent_hash=torrent_info.hash,
                    original_name=torrent_info.name,
                    after_name=torrent_info.name,  # 名称未改变
                    success=False,
                    downloader_name=downloader or "未知",
                    reason=reason
                )
                return {"success": False, "message": message}
        if success and not media_info:
            media_info = self.chain.recognize_media(meta=meta)
            # meta = MetaInfo(media_info.en_title)
            if not media_info:
                success = False
                reason = f"识别媒体信息失败，种子名称：{torrent_info.name}"
                message = reason
                logger.error(f"{reason}，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                # 记录失败历史
                self.__record_rename_history(
                    torrent_hash=torrent_info.hash,
                    original_name=torrent_info.name,
                    after_name=torrent_info.name,  # 名称未改变
                    success=False,
                    downloader_name=downloader or "未知",
                    reason=reason
                )
                return {"success": False, "message": message}
        if success:
            logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 开始执行重命名")
            logger.debug(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} torrent_info：{torrent_info} meta：{meta} media_info：{media_info}")
            if self.format_torrent(torrent_info=torrent_info, meta=meta, media_info=media_info, downloader=downloader):
                logger.info(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 处理完成")
                # 添加已重命名标签
                if self._add_tag_after_rename:
                    self.downloader.torrents_add_tags(torrent_info.hash,["已重命名"])
                return {"success": True, "message": f"处理完成，种子名称：{torrent_info.name}"}
            else:
                # format_torrent返回False，表示重命名失败，但历史记录已在format_torrent中记录
                reason = f"重命名失败，种子名称：{torrent_info.name}"
                return {"success": False, "message": reason}
        # 处理失败
        reason = message or "处理失败"
        # 记录失败历史
        self.__record_rename_history(
            torrent_hash=torrent_info.hash if torrent_info else hash or "unknown",
            original_name=torrent_info.name if torrent_info else "unknown",
            after_name=torrent_info.name if torrent_info else "unknown",
            success=False,
            downloader_name=downloader or "未知",
            reason=reason
        )
        return {"success": False, "message": reason}

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

            # 创建一个集合来存储要删除的记录的hash值
            hashes_to_delete = set()
            for record in records_to_delete:
                record_hash = record.get("hash")
                if record_hash:
                    hashes_to_delete.add(record_hash)

            # 调试输出要删除的hash
            logger.debug(f"Hashes to delete: {hashes_to_delete}")

            # 从缓存中删除记录
            self.__delete_from_rename_history_cache(hashes_to_delete)

            logger.debug(f"Deleted {len(hashes_to_delete)} records from cache")

            return {
                "success": True,
                "message": f"成功删除 {len(hashes_to_delete)} 条记录"
            }

        except Exception as e:
            logger.error(f"删除重命名历史记录失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除重命名历史记录失败: {str(e)}"
            }
