from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from app.core.context import MediaInfo, Context
from app.core.event import eventmanager, Event
from app.core.meta.metabase import MetaBase
from app.db.downloadhistory_oper import DownloadHistoryOper
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.directory import DirectoryHelper
from app.helper.downloader import DownloaderHelper
from app.helper.service import ServiceConfigHelper
from app.log import logger
from app.modules.filemanager.transhandler import TransHandler
from app.plugins import _PluginBase
from app.schemas.event import ResourceDownloadEventData
from app.schemas.types import EventType, MediaType, ChainEventType, SystemConfigKey


@dataclass
class FormatHistory:
    """
    格式化路径历史记录
    """
    # 种子名称
    title: str
    # 原始路径
    original_path: str
    # 格式化后路径
    formatted_path: str
    # 下载器
    downloader: str
    # 处理时间
    date: str
    # 类别
    category: str = ""
    # 是否成功
    success: bool = True
    # 失败原因
    reason: str = ""


class FormatDownloadPath(_PluginBase):
    # 插件名称
    plugin_name = "下载路径格式化"
    # 插件描述
    plugin_desc = "监听资源下载事件，格式化下载路径。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "1.0.4"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "formatdownloadpath_"
    # 加载顺序
    plugin_order = 17
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None

    # 配置属性
    # 启用插件
    _enabled: bool = False
    # 启用监听
    _enable_listener: bool = False
    # 监听的下载器
    _downloaders: List[str] = None  # 初始化为None，将在load_config中设置为默认空列表
    # 电影格式化路径模板
    _movie_format_path_template: str = "{{ title }}{% if year %}({{ year }}){% endif %}"
    # 剧集格式化路径模板
    _tv_format_path_template: str = "{{ title }}{% if year %}({{ year }}){% endif %}"
    # 排除目录
    _exclude_dirs: str = ""
    # 格式化历史记录字典缓存
    _format_history_dict: Optional[Dict[str, Dict]] = None
    # 格式化历史记录字典是否已修改
    _format_history_dict_dirty: bool = False

    downloader_helper = None
    downloadhis = None

    def __init__(self):
        super().__init__()
        # 初始化配置属性
        self._downloaders = []
        # 初始化时加载缓存
        self.__load_format_history_cache()

    def __load_format_history_cache(self):
        """
        加载格式化历史记录到缓存
        """
        history = self.get_data(key="format_history") or []
        self._format_history_dict = {f"{record['title']}_{record['date']}": record for record in history}
        self._format_history_dict_dirty = False

    def __get_format_history_cache(self) -> Dict[str, Dict]:
        """
        获取格式化历史记录缓存
        :return: 以title_date为键的历史记录字典
        """
        if self._format_history_dict is None:
            self.__load_format_history_cache()

        return self._format_history_dict

    def __record_format_history(self, title: str, original_path: str,
                                formatted_path: str, downloader: str = None,
                                category: str = None, reason: str = None, success: bool = True):
        """
        记录格式化历史
        """
        # 添加到缓存
        self.__add_to_format_history_cache(title, original_path, formatted_path,
                                           downloader, category, reason, success)

    def __add_to_format_history_cache(self, title: str, original_path: str,
                                      formatted_path: str, downloader: str = None,
                                      category: str = None, reason: str = None, success: bool = True):
        """
        添加记录到格式化历史缓存
        """
        if self._format_history_dict is None:
            self.__load_format_history_cache()

        record = {
            "title": title,
            "original_path": original_path,
            "formatted_path": formatted_path,
            "downloader": downloader or "",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": category or "",
            "success": success,
            "reason": reason or ""
        }

        # 添加到缓存开头（按时间倒序）
        key = f"{title}_{record['date']}"
        self._format_history_dict[key] = record
        self._format_history_dict_dirty = True

    def __sync_format_history_to_storage(self):
        """
        将缓存的历史记录同步到存储
        """
        if self._format_history_dict_dirty and self._format_history_dict is not None:
            # 将字典转换为列表格式并保存
            history_list = list(self._format_history_dict.values())
            # 按时间倒序排列
            history_list.sort(key=lambda x: x.get("date", ""), reverse=True)
            self.save_data(key="format_history", value=history_list)
            self._format_history_dict_dirty = False
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
        self.update_config(config=config)

    def load_config(self, config: dict):
        """加载配置"""
        if not config:
            return

        # 遍历配置中的键并设置相应的属性
        for key in (
                "enabled",
                "enable_listener",
                "movie_format_path_template",
                "tv_format_path_template",
                "exclude_dirs"
        ):
            setattr(self, f"_{key}", config.get(key, getattr(self, f"_{key}")))
        
        # 特殊处理downloaders字段，确保它是列表类型
        downloaders_value = config.get("downloaders")
        if downloaders_value is not None:
            self._downloaders = downloaders_value if isinstance(downloaders_value, list) else []
        else:
            # 如果配置中没有downloaders字段，保持默认值
            if not hasattr(self, '_downloaders') or self._downloaders is None:
                self._downloaders = []

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字列表
        """
        return [{
            "cmd": "/format_download_path",
            "event": EventType.PluginAction,
            "desc": "格式化下载路径",
            "category": "下载",
            "data": {
                "action": "format_download_path"
            }
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [{
            "path": "/get_config",
            "endpoint": self._get_config,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取插件配置",
            "description": "获取插件当前配置"
        }, {
            "path": "/format_history",
            "endpoint": self.get_format_history,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取格式化历史",
            "description": "获取路径格式化历史记录"
        }, {
            "path": "/delete_format_history",
            "endpoint": self.delete_format_history,
            "auth": "bear",
            "methods": ["POST"],
            "summary": "删除格式化历史记录",
            "description": "删除指定的格式化历史记录"
        }, {
            "path": "/get_downloaders",
            "endpoint": self.get_downloaders,
            "auth": "bear",
            "methods": ["GET"],
            "summary": "获取可用下载器",
            "description": "获取系统中可用的下载器列表"
        }]

    def get_form(self):
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return None, {
            "enabled": False,
            "enable_listener": False,
            "downloaders": [],
            "movie_format_path_template": self._movie_format_path_template,
            "tv_format_path_template": self._tv_format_path_template,
            "exclude_dirs": ""
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
            self.__sync_format_history_to_storage()

    def _get_config(self):
        """
        获取插件配置
        """
        return {
            "id": "FormatDownloadPath",
            "name": "下载路径格式化",
            "enabled": self._enabled,
            "enable_listener": self._enable_listener,
            "downloaders": self._downloaders or [],
            "movie_format_path_template": self._movie_format_path_template,
            "tv_format_path_template": self._tv_format_path_template,
            "exclude_dirs": self._exclude_dirs
        }

    def get_format_history(self):
        """
        获取格式化历史记录
        """
        # 从缓存获取历史记录
        history_dict = self.__get_format_history_cache()
        # 转换为列表并按时间倒序排列
        history_list = list(history_dict.values())
        history_list.sort(key=lambda x: x.get("date", ""), reverse=True)
        return history_list

    @eventmanager.register(ChainEventType.ResourceDownload)
    def resource_download_handler(self, event: Event):
        """
        处理资源下载事件
        """
        if not self._enabled or not self._enable_listener or not event:
            return

        logger.debug(f"收到资源下载事件：{event}")
        event_data: ResourceDownloadEventData = event.event_data
        if not event_data:
            logger.debug("事件数据为空，跳过处理")
            return

        # 获取下载器信息
        downloader = event_data.downloader or ""
        # 检查是否配置了特定下载器，如果是，只处理指定的下载器
        # 如果_downloaders为空列表，则监听所有下载器
        if not downloader:
            configs = ServiceConfigHelper.get_downloader_configs()
            for config in configs:
               if config.default:  # 找到标记为默认的下载器
                   logger.debug(f"默认下载器: {config.name}")
                   downloader = config.name
                   break
            else:
               # 如果没有设置默认下载器，则使用第一个
               if configs:
                   logger.debug(f"第一个下载器作为默认: {configs[0].name}")
                   downloader = configs[0].name

        if self._downloaders and downloader not in self._downloaders:
            logger.debug(f"下载器 {downloader} 不在监听列表中，跳过处理")
            return

        # 获取上下文信息
        context: Context = event_data.context
        if not context:
            logger.debug("事件中没有上下文信息，跳过处理")
            return

        # 获取媒体信息
        media_info = context.media_info
        if not media_info:
            logger.debug("上下文中没有媒体信息，跳过处理")
            return

        # 获取原始路径
        options = event_data.options or {}
        original_path = options.get("save_path", "")
        basedir = None
        if original_path:
            basedir = Path(original_path)
        else:
            basedir = self.get_auto_download_path(media_info)

        if basedir is None:
            logger.debug("没有获取到下载路径，跳过处理")
            return

        basedir_str = basedir.as_posix()
        # 检查是否在排除目录中
        if self._exclude_dirs:
            exclude_dirs = [d.strip() for d in self._exclude_dirs.split("\n") if d.strip()]
            for exclude_dir in exclude_dirs:
                try:
                    exclude_path = Path(exclude_dir.strip())
                    if basedir.is_relative_to(exclude_path):
                        logger.debug(f"目录 {basedir} 在排除列表中，跳过格式化")
                        return
                except Exception as e:
                    logger.debug(f"检查排除目录时出错 {exclude_dir}: {str(e)}")
                    continue

        # 根据媒体类型选择模板
        if media_info.type == MediaType.MOVIE:
            template_string = self._movie_format_path_template
        else:
            template_string = self._tv_format_path_template

        # 格式化路径
        formatted_path = self.format_path(
            template_string=template_string,
            meta=context.meta_info,
            mediainfo=media_info
        )

        if not formatted_path:
            logger.debug(f"路径格式化失败，原路径：{basedir_str}")
            self.__record_format_history(
                title=media_info.title,
                original_path=basedir_str,
                formatted_path=basedir_str,  # 失败时仍使用原路径
                downloader=downloader,
                category=media_info.category,
                reason="路径格式化失败",
                success=False
            )
            return

        # 检查路径是否与原路径相同
        if (basedir / formatted_path) == basedir_str:
            logger.debug(f"格式化后路径与原路径相同，无需修改：{basedir_str}")
            self.__record_format_history(
                title=media_info.title,
                original_path=basedir_str,
                formatted_path=formatted_path,
                downloader=downloader,
                category=media_info.category,
                reason="路径已符合格式要求",
                success=True
            )
            return

        # 更新事件数据中的路径
        if event and event.event_data and formatted_path:
            if hasattr(event, 'event_data') and event.event_data:
                options = event.event_data.options or {}
                if basedir is None:
                    return
                options['save_path'] = basedir / formatted_path
                event.event_data.options = options
            else:
                return

        logger.info(f"路径已格式化：{basedir_str} -> {event.event_data.options['save_path']}")
        self.__record_format_history(
            title=media_info.title,
            original_path=basedir_str,
            formatted_path=event.event_data.options['save_path'],
            downloader=downloader,
            category=media_info.category,
            reason="",
            success=True
        )

    def format_path(self, template_string: str, meta: MetaBase, mediainfo: MediaInfo) -> Optional[str]:
        """
        根据媒体信息格式化路径
        """
        if not template_string or not mediainfo:
            return None

        try:
            handler = TransHandler()
            rename_dict = handler.get_naming_dict(meta=meta, mediainfo=mediainfo)
            logger.debug(f"路径格式化模板：{template_string}")
            logger.debug(f"重命名字典：{rename_dict}")
            formatted_path = handler.get_rename_path(template_string, rename_dict)
            return formatted_path.as_posix() if formatted_path else None
        except Exception as e:
            logger.error(f"路径格式化失败：{str(e)}")
            return None

    def get_downloaders(self):
        """
        获取可用下载器列表
        """
        try:
            # 获取所有下载器实例
            downloaders: List[dict] = SystemConfigOper().get(SystemConfigKey.Downloaders)
            if downloaders:
                return [{"title": d.get("name"), "value": d.get("name")} for d in downloaders if d.get("enabled")]
            return []
        except Exception as e:
            logger.error(f"获取下载器列表失败: {str(e)}")
            return []

    def delete_format_history(self, request_body: dict):
        """
        删除格式化历史记录
        :param request_body: 请求体，包含要删除的记录列表
        """
        try:
            # 获取要删除的记录列表
            records_to_delete = request_body.get("records", [])

            if not records_to_delete:
                return {
                    "success": False,
                    "message": "未提供要删除的记录"
                }

            # 创建一个集合来存储要删除的记录的键
            keys_to_delete = set()
            for record in records_to_delete:
                title = record.get("title")
                date = record.get("date")
                if title and date:
                    key = f"{title}_{date}"
                    keys_to_delete.add(key)

            # 从缓存中删除记录
            for key in keys_to_delete:
                if key in self._format_history_dict:
                    del self._format_history_dict[key]
                    self._format_history_dict_dirty = True

            logger.debug(f"删除了 {len(keys_to_delete)} 条格式化历史记录")

            return {
                "success": True,
                "message": f"成功删除 {len(keys_to_delete)} 条记录"
            }

        except Exception as e:
            logger.error(f"删除格式化历史记录失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除格式化历史记录失败: {str(e)}"
            }

    def get_auto_download_path(self, _media: MediaInfo):
        storage = 'local'
        # 根据媒体信息查询下载目录配置
        dir_info = DirectoryHelper().get_dir(_media, include_unsorted=True)
        storage = dir_info.storage if dir_info else storage
        # 拼装子目录
        if dir_info:
            # 一级目录
            if not dir_info.media_type and dir_info.download_type_folder:
                # 一级自动分类
                download_dir = Path(dir_info.download_path) / _media.type.value
            else:
                # 一级不分类
                download_dir = Path(dir_info.download_path)

            # 二级目录
            if not dir_info.media_category and dir_info.download_category_folder and _media and _media.category:
                # 二级自动分类
                download_dir = download_dir / _media.category
        else:
            # 未找到下载目录，且没有自定义下载目录
            logger.error(f"未找到下载目录：{_media.type.value} {_media.title_year}")
            return None
        return download_dir