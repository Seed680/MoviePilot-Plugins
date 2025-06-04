import datetime
import threading
from typing import List, Tuple, Dict, Any, Optional

import pytz
from app.helper.sites import SitesHelper
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.context import Context
from app.core.event import eventmanager, Event
from app.db.downloadhistory_oper import DownloadHistoryOper
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.modules.qbittorrent.qbittorrent import Qbittorrent
from app.plugins import _PluginBase
from app.schemas import ServiceInfo
from app.schemas.types import EventType
from app.schemas.types import SystemConfigKey
from app.utils.string import StringUtils
from modules.transmission import Transmission


class TrackerSpeedLimit(_PluginBase):
    # 插件名称
    plugin_name = "Tracker速度限制"
    # 插件描述
    plugin_desc = "Tracker速度限制"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/Seed680/MoviePilot-Plugins/main/icons/customplugin.png"
    # 插件版本
    plugin_version = "0.1"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "TrackerSpeedLimit_"
    # 加载顺序
    plugin_order = 2
    # 可使用的用户级别
    auth_level = 1
    # 日志前缀
    LOG_TAG = "[TrackerSpeedLimit] "

    # 退出事件
    _event = threading.Event()
    # 私有属性
    downloadhistory_oper = None
    sites_helper = None
    downloader_helper = None
    tracker_limit_map = None

    _scheduler = None
    _enable = False
    _onlyonce = False
    _interval = "计划任务"
    _interval_cron = "5 4 * * *"
    _interval_time = 6
    _interval_unit = "小时"
    _downloaders = None
    _siteConfig = None
    

    def init_plugin(self, config: dict = None):
        self.downloadhistory_oper = DownloadHistoryOper()
        self.downloader_helper = DownloaderHelper()
        self.sites_helper = SitesHelper()

        # 读取配置
        logger.debug(f"读取配置")
        if config:
            self._enable = config.get("enable", False)
            self._onlyonce = config.get("onlyonce", False)
            self._interval = config.get("interval","计划任务")
            self._interval_cron = config.get("interval_cron", "5 4 * * *")
            self._interval_time = self.str_to_number(config.get("interval_time"), 6)
            self._interval_unit = config.get("interval_unit", "小时")
            self._downloaders = config.get("downloaders")
            self._siteConfig = config.get("siteConfig", {})
            self.tracker_limit_map = self.process_site_config(self._siteConfig)
            logger.debug(f"tracker_limit_map: {self.tracker_limit_map}")
        # 停止现有任务
        self.stop_service()

        if self._onlyonce:
            # 创建定时任务控制器
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            # 执行一次, 关闭onlyonce
            self._onlyonce = False
            config.update({"onlyonce": self._onlyonce})
            self.update_config(config)
            # 添加 任务
            self._scheduler.add_job(func=self._speed_limit, trigger='date',
                                    run_date=datetime.datetime.now(
                                        tz=pytz.timezone(settings.TZ)) + datetime.timedelta(seconds=3)
                                    )

            if self._scheduler and self._scheduler.get_jobs():
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()
        else:
            self.update_config(config)

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
         # This dict is passed as initialConfig to Config.vue by the host
         return None, self._get_config()
        # logger.debug(f"all_cat_rename:{self._all_cat_rename}")


    def load_config(self, config: dict):
        """加载配置"""
        if config:
            # 遍历配置中的键并设置相应的属性
            for key in (
                "enable",
                "interval",
                "interval_cron",
                "interval_time",
                "interval_unit",
                "downloaders",
                "onlyonce",
                "siteConfig",
            ):
                setattr(self, f"_{key}", config.get(key, getattr(self, f"_{key}")))

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify
        :return: 2、组件路径，默认 dist/assets
        """
        return "vue", "dist/assets"

    # --- Instance methods for API endpoints ---
    def _get_config(self) -> Dict[str, Any]:
        """API Endpoint: Returns current plugin configuration."""

        return {
            "enable": self._enable,
            "interval": self._interval,
            "interval_cron": self._interval_cron,
            "interval_time": self._interval_time,
            "interval_unit": self._interval_unit,
            "downloaders": self._downloaders,
            "onlyonce": False,  # 始终返回False,
            "siteConfig": self._siteConfig,
        }

    def _save_config(self, config_payload: dict) -> Dict[str, Any]:
        # Update instance variables directly from payload, defaulting to current values if key is missing
            self.load_config(config_payload)
            # 忽略onlyonce参数
            config_payload.onlyonce = False

            # Prepare config to save
            # config_to_save = self._get_config()

            # 保存配置
            self.update_config(config_payload)

            # 重新初始化插件
            self.stop_service()
            self.init_plugin(self.get_config())

            logger.info(f"{self.plugin_name}: 配置已保存并通过 init_plugin 重新初始化。当前内存状态: enable={self._enable}")

            # 返回最终状态
            return {"message": "配置已成功保存", "saved_config": self._get_config()}
    @property
    def service_infos(self) -> Optional[Dict[str, ServiceInfo]]:
        """
        服务信息
        """
        if not self._downloaders:
            logger.warning("尚未配置下载器，请检查配置")
            return None

        services = self.downloader_helper.get_services(name_filters=self._downloaders)
        if not services:
            logger.warning("获取下载器实例失败，请检查配置")
            return None

        active_services = {}
        for service_name, service_info in services.items():
            if service_info.instance.is_inactive():
                logger.warning(f"下载器 {service_name} 未连接，请检查配置")
            else:
                active_services[service_name] = service_info

        if not active_services:
            logger.warning("没有已连接的下载器，请检查配置")
            return None

        return active_services

    @property
    def _all_downloaders(self) -> List[str]:
        sys_downloader = SystemConfigOper().get(SystemConfigKey.Downloaders)
        if sys_downloader:
            all_downloaders = [{"title": d.get("name"), "value": d.get("name")} for d in sys_downloader if d.get("enabled")]
        else:
            all_downloaders = []
        return all_downloaders

    def get_state(self) -> bool:
        return self._enable

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {
                "path": "/config",
                "endpoint": self._get_config,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取当前配置"
            },
            {
                "path": "/getDownloaders",
                "endpoint": self._all_downloaders,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取下载器列表"
            }
        ]

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        [{
            "id": "服务ID",
            "name": "服务名称",
            "trigger": "触发器：cron/interval/date/CronTrigger.from_crontab()",
            "func": self.xxx,
            "kwargs": {} # 定时器参数
        }]
        """
        if self._enable:
            if self._interval == "计划任务" or self._interval == "固定间隔":
                if self._interval == "固定间隔":
                    if self._interval_unit == "小时":
                        return [{
                            "id": "DownloadSiteTag",
                            "name": "补全下载历史的标签与分类",
                            "trigger": "interval",
                            "func": self._speed_limit,
                            "kwargs": {
                                "hours": self._interval_time
                            }
                        }]
                    else:
                        if self._interval_time < 5:
                            self._interval_time = 5
                            logger.info(f"{self.LOG_TAG}启动定时服务: 最小不少于5分钟, 防止执行间隔太短任务冲突")
                        return [{
                            "id": "DownloadSiteTag",
                            "name": "补全下载历史的标签与分类",
                            "trigger": "interval",
                            "func": self._speed_limit,
                            "kwargs": {
                                "minutes": self._interval_time
                            }
                        }]
                else:
                    return [{
                        "id": "DownloadSiteTag",
                        "name": "补全下载历史的标签与分类",
                        "trigger": CronTrigger.from_crontab(self._interval_cron),
                        "func": self._speed_limit,
                        "kwargs": {}
                    }]
        return []

    @staticmethod
    def str_to_number(s: str, i: int) -> int:
        try:
            return int(s)
        except ValueError:
            return i

    def _speed_limit(self, hash=None):
        """
        补全下载历史的标签与分类
        """
        if not self.service_infos:
            return
        logger.info(f"{self.LOG_TAG}开始执行 ...")
        for service in self.service_infos.values():
            downloader = service.name
            downloader_obj = service.instance
            logger.info(f"{self.LOG_TAG}开始扫描下载器 {downloader} ...")
            if not downloader_obj:
                logger.error(f"{self.LOG_TAG} 获取下载器失败 {downloader}")
                continue
            # 获取下载器中的种子
            torrents, error = downloader_obj.get_torrents(ids=hash)
            # 如果下载器获取种子发生错误 或 没有种子 则跳过
            if error or not torrents:
                continue
            logger.info(f"{self.LOG_TAG}下载器 {downloader} 分析种子信息中 ...")
            for torrent in torrents:
                try:
                    if self._event.is_set():
                        logger.info(
                            f"{self.LOG_TAG}停止服务")
                        return
                    # 获取已处理种子的key (size, name)
                    _size, _name = self._torrent_key(torrent=torrent, dl_type=service.type)
                    # 获取种子hash
                    _hash = self._get_hash(torrent=torrent, dl_type=service.type)
                    if not _hash:
                        continue
                    trackers = self._get_trackers(torrent=torrent, dl_type=service.type)
                    for tracker in trackers:
                        logger.debug(f"tracker: {tracker} ...")
                        # 检查tracker是否包含特定的关键字，并进行相应的映射
                        if self._siteConfig is not None:
                            for site in self._siteConfig:
                                if site.get("enabled"):
                                    domain = StringUtils.get_url_domain(tracker)
                                    logger.debug(f"tracker domain: {domain} ...")
                                    if self.tracker_limit_map.get(domain) :
                                        logger.debug(f"获取到{domain}的设置 ...")
                                        if self.tracker_limit_map.get(domain).get(
                                            "enabled") :
                                                logger.debug(f"{domain}设置已生效 ...")
                                                if self.tracker_limit_map.get(domain).get(
                                            "speedLimit"):
                                                    logger.debug(f"{domain} {_name} {_hash} 设置限速 {int(self.tracker_limit_map.get(domain).get(
                                                        "speedLimit"))} ...")
                                                    self.torrents_set_upload_limit(_hash, int(self.tracker_limit_map.get(domain).get(
                                                        "speedLimit")), downloader_obj)
                                                    break
                                    else:
                                        logger.debug(f"未获取到{domain}的设置 设置为不限速...")
                                        self.torrents_set_upload_limit(_hash, -1, downloader_obj)

                except Exception as e:
                    logger.error(
                        f"{self.LOG_TAG}分析种子信息时发生了错误: {str(e)}", exc_info=True)

        logger.info(f"{self.LOG_TAG}执行完成")


    @staticmethod
    def _torrent_key(torrent: Any, dl_type: str) -> Optional[Tuple[int, str]]:
        """
        按种子大小和时间返回key
        """
        if dl_type == "qbittorrent":
            size = torrent.get('size')
            name = torrent.get('name')
        else:
            size = torrent.total_size
            name = torrent.name
        if not size or not name:
            return None
        else:
            return size, name

    @staticmethod
    def _get_hash(torrent: Any, dl_type: str):
        """
        获取种子hash
        """
        try:
            return torrent.get("hash") if dl_type == "qbittorrent" else torrent.hashString
        except Exception as e:
            print(str(e))
            return ""

    @staticmethod
    def _get_trackers(torrent: Any, dl_type: str) -> List[str]:
        """
        获取种子trackers
        """
        try:
            if dl_type == "qbittorrent":
                """
                url	字符串	跟踪器网址
                status	整数	跟踪器状态。有关可能的值，请参阅下表
                tier	整数	跟踪器优先级。较低级别的跟踪器在较高级别的跟踪器之前试用。当特殊条目（如 DHT）不存在时，层号用作占位符时，层号有效。>= 0< 0tier
                num_peers	整数	跟踪器报告的当前 torrent 的对等体数量
                num_seeds	整数	当前种子的种子数，由跟踪器报告
                num_leeches	整数	当前种子的水蛭数量，如跟踪器报告的那样
                num_downloaded	整数	跟踪器报告的当前 torrent 的已完成下载次数
                msg	字符串	跟踪器消息（无法知道此消息是什么 - 由跟踪器管理员决定）
                """
                return [tracker.get("url") for tracker in (torrent.trackers or []) if
                        tracker.get("tier", -1) >= 0 and tracker.get("url")]
            else:
                """
                class Tracker(Container):
                    @property
                    def id(self) -> int:
                        return self.fields["id"]

                    @property
                    def announce(self) -> str:
                        return self.fields["announce"]

                    @property
                    def scrape(self) -> str:
                        return self.fields["scrape"]

                    @property
                    def tier(self) -> int:
                        return self.fields["tier"]
                """
                return [tracker.announce for tracker in (torrent.trackers or []) if
                        tracker.tier >= 0 and tracker.announce]
        except Exception as e:
            print(str(e))
            return []


    def _set_torrent_info(self, service: ServiceInfo, _hash: str, _torrent: Any = None, _tags=None, _cat: str = None,
                          _original_tags: list = None):
        """
        设置种子标签与分类
        """
        if not service or not service.instance:
            return
        if _tags is None:
            _tags = []
        downloader_obj = service.instance
        if not _torrent:
            _torrent, error = downloader_obj.get_torrents(ids=_hash)
            if not _torrent or error:
                logger.error(
                    f"{self.LOG_TAG}设置种子标签与分类时发生了错误: 通过 {_hash} 查询不到任何种子!")
                return
            logger.info(
                f"{self.LOG_TAG}设置种子标签与分类: {_hash} 查询到 {len(_torrent)} 个种子")
            _torrent = _torrent[0]
        # 判断是否可执行
        if _hash and _torrent:
            # 下载器api不通用, 因此需分开处理
            if service.type == "qbittorrent":
                # 设置标签
                if _tags:
                    downloader_obj.set_torrents_tag(ids=_hash, tags=_tags)
                # 设置分类 <tr暂不支持>
                if _cat:
                    # 尝试设置种子分类, 如果失败, 则创建再设置一遍
                    try:
                        _torrent.setCategory(category=_cat)
                    except Exception as e:
                        logger.warn(f"下载器 {service.name} 种子id: {_hash} 设置分类 {_cat} 失败：{str(e)}, "
                                    f"尝试创建分类再设置 ...")
                        downloader_obj.qbc.torrents_createCategory(name=_cat)
                        _torrent.setCategory(category=_cat)
            else:
                # 设置标签
                if _tags:
                    # _original_tags = None表示未指定, 因此需要获取原始标签
                    if _original_tags is None:
                        _original_tags = self._get_label(torrent=_torrent, dl_type=service.type)
                    # 如果原始标签不是空的, 那么合并原始标签
                    if _original_tags:
                        _tags = list(set(_original_tags).union(set(_tags)))
                    downloader_obj.set_torrent_tag(ids=_hash, tags=_tags)
            logger.warn(
                f"{self.LOG_TAG}下载器: {service.name} 种子id: {_hash} {('  标签: ' + ','.join(_tags)) if _tags else ''} {('  分类: ' + _cat) if _cat else ''}")

    @eventmanager.register(EventType.DownloadAdded)
    def download_added(self, event: Event):
        """
        添加下载事件
        """
        if not self.get_state():
            return

        if not event.event_data:
            return

        try:
            downloader = event.event_data.get("downloader")
            if not downloader:
                logger.info("触发添加下载事件，但没有获取到下载器信息，跳过后续处理")
                return

            service = self.service_infos.get(downloader)
            if not service:
                logger.info(f"触发添加下载事件，但没有监听下载器 {downloader}，跳过后续处理")
                return

            context: Context = event.event_data.get("context")
            _hash = event.event_data.get("hash")
            _torrent = context.torrent_info
            # 获取下载器中的种子
            downloader_obj = service.instance
            torrents, error = downloader_obj.get_torrents(ids=hash)
            # 如果下载器获取种子发生错误 或 没有种子 则跳过
            if error or not torrents:
                return
            logger.info(f"{self.LOG_TAG}下载器 {downloader} 分析种子信息中 ...")
            for torrent in torrents:
                if self._event.is_set():
                    logger.info(
                        f"{self.LOG_TAG}停止服务")
                    return
                # 获取已处理种子的key (size, name)
                _size, _name = self._torrent_key(torrent=torrent, dl_type=service.type)
                # 获取种子hash
                _hash = self._get_hash(torrent=torrent, dl_type=service.type)
                if not _hash:
                    continue
                trackers = self._get_trackers(torrent=torrent, dl_type=service.type)
                for tracker in trackers:
                    logger.debug(f"tracker: {tracker} ...")
                    # 检查tracker是否包含特定的关键字，并进行相应的映射
                    if self._siteConfig is not None:
                        for site in self._siteConfig:
                            if site.get("enabled"):
                                domain = StringUtils.get_url_domain(tracker)
                                logger.debug(f"tracker domain: {domain} ...")
                                if self.tracker_limit_map.get(domain):
                                    logger.debug(f"获取到{domain}的设置 ...")
                                    if self.tracker_limit_map.get(domain).get(
                                            "enabled"):
                                        logger.debug(f"{domain}设置已生效 ...")
                                        if self.tracker_limit_map.get(domain).get(
                                                "speedLimit"):
                                            logger.debug(
                                                f"{domain} {_name} {_hash} 设置限速 {int(self.tracker_limit_map.get(domain).get(
                                                    "speedLimit"))} ...")
                                            self.torrents_set_upload_limit(_hash, int(self.tracker_limit_map.get(
                                                domain).get(
                                                "speedLimit")), downloader_obj)
                                            break
                                else:
                                    logger.debug(f"未获取到{domain}的设置 设置为不限速...")
                                    self.torrents_set_upload_limit(_hash, -1, downloader_obj)
        except Exception as e:
            logger.error(
                f"{self.LOG_TAG}分析下载事件时发生了错误: {str(e)}", exc_info=True)

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._event.set()
                    self._scheduler.shutdown()
                    self._event.clear()
                self._scheduler = None
        except Exception as e:
            print(str(e))

    def torrents_set_upload_limit(self, torrent_hash:str, limit: str | int, service_instance:Qbittorrent | Transmission):
        if service_instance is Qbittorrent:
            service_instance.qbc.torrents_set_upload_limit(torrent_hashes=torrent_hash,limit=limit)
        else:
            service_instance.trc.change_torrent(ids=torrent_hash,upload_limit=int(limit))

    def process_site_config(self,site_list):

        result = {}

        for site in site_list:
            # 获取站点基本信息
            site_info = {
                'enabled': site['enabled'],
                'speedLimit': site['speedLimit']
            }

            # 添加站点自身
            result[site['url']] = site_info

            # 添加站点下的所有追踪器
            for tracker_id in site['tackerList']:
                result[tracker_id] = site_info.copy()  # 使用 copy 避免引用问题

        return result
