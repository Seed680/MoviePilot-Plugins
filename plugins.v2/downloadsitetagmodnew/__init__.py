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
from app.db.models.downloadhistory import DownloadHistory
from app.modules.themoviedb import CategoryHelper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import ServiceInfo
from app.schemas.types import EventType, MediaType
from app.utils.string import StringUtils
from app.db.systemconfig_oper import SystemConfigOper
from app.schemas.types import SystemConfigKey


class DownloadSiteTagModNew(_PluginBase):
    # 插件名称
    plugin_name = "下载任务分类与标签魔改VUE版"
    # 插件描述
    plugin_desc = "(基于叮叮当原版修改)自动给下载任务分类与打站点标签、剧集名称标签"
    # 插件图标
    plugin_icon = "Youtube-dl_B.png"
    # 插件版本
    plugin_version = "0.0.9"
    # 插件作者
    plugin_author = "叮叮当,Seed680"
    # 作者主页
    author_url = "https://github.com/cikezhu"
    # 插件配置项ID前缀
    plugin_config_prefix = "DownloadSiteTagModNew_"
    # 加载顺序
    plugin_order = 2
    # 可使用的用户级别
    auth_level = 1
    # 日志前缀
    LOG_TAG = "[DownloadSiteTagModNew] "

    # 退出事件
    _event = threading.Event()
    # 私有属性
    downloadhistory_oper = None
    sites_helper = None
    downloader_helper = None
    category_helper: CategoryHelper = None
    _scheduler = None
    _enable = False
    _onlyonce = False
    _interval = "计划任务"
    _interval_cron = "5 4 * * *"
    _interval_time = 6
    _interval_unit = "小时"
    _enable_media_tag = False
    _enable_tag = True
    _enable_category = False
    _category_movie = None
    _category_tv = None
    _category_anime = None
    _downloaders = None
    _all_downloaders = []
    _all_cat = []
    _all_cat_rename = []
    _cat_rename_dict = {}
    _rename_type = False
    _path_rename = None
    _catprefix = ""
    _siteprefix = ""

    def init_plugin(self, config: dict = None):
        self.downloadhistory_oper = DownloadHistoryOper()
        self.downloader_helper = DownloaderHelper()
        self.sites_helper = SitesHelper()
        self.category_helper = CategoryHelper()

        self._all_cat = [*self.category_helper.tv_categorys, *self.category_helper.movie_categorys]
        self._all_cat_rename = self._all_cat
        # 读取配置
        logger.debug(f"读取配置")
        if config:
            self._enable = config.get("enable", False)
            self._onlyonce = config.get("onlyonce", False)
            self._interval = config.get("interval","计划任务")
            self._interval_cron = config.get("interval_cron", "5 4 * * *")
            self._interval_time = self.str_to_number(config.get("interval_time"), 6)
            self._interval_unit = config.get("interval_unit", "小时")
            self._enable_media_tag = config.get("enable_media_tag", False)
            self._enable_tag = config.get("enable_tag")
            self._enable_category = config.get("enable_category")
            self._downloaders = config.get("downloaders")
            self._catprefix = config.get("catprefix","")
            self._siteprefix = config.get("siteprefix","")
            logger.debug(f"all_cat:{self._all_cat}")
            if None == config.get("all_cat_rename") or len(config.get("all_cat_rename")) == 0 :
                self._all_cat_rename = self._all_cat
            else :
                self._all_cat_rename  = config.get("all_cat_rename")
            logger.debug(f"all_cat_rename:{self._all_cat_rename}")
            self._rename_type = config.get("rename_type", False) #False按二级分类 True按路径分类
            self._path_rename = config.get("path_rename", None)

            if not self._rename_type:
                for index, item in enumerate(self._all_cat):
                    self._cat_rename_dict[str(item)] = self._all_cat_rename[index]
                logger.debug(f"按二级分类设置分类")
                logger.debug(f"cat_rename_dict:{self._cat_rename_dict}")

            if self._rename_type and self._path_rename is not None:
                logger.debug(f"按目录关键字设置分类")
                formate_rule_list = self._path_rename.strip().split("\n")
                if len(formate_rule_list) < 1:
                    logger.error("分类规则为空")
                    return
                for rule in formate_rule_list:
                    if '#' not in rule:
                        logger.error(f"{rule}未包含#")
                        return
                    name_list = rule.split("#")
                    if len(name_list) < 2 or len(name_list) > 2:
                        logger.error(f"{name_list}不符合规则")
                        return
                    self._cat_rename_dict[name_list[0]] = name_list[1]

                logger.debug(f"cat_rename_dict:{self._cat_rename_dict}")
        # 停止现有任务
        self.stop_service()

        if self._onlyonce:
            # 创建定时任务控制器
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            # 执行一次, 关闭onlyonce
            self._onlyonce = False
            config.update({"onlyonce": self._onlyonce})
            self.update_config(config)
            # 添加 补全下载历史的标签与分类 任务
            self._scheduler.add_job(func=self._complemented_history, trigger='date',
                                    run_date=datetime.datetime.now(
                                        tz=pytz.timezone(settings.TZ)) + datetime.timedelta(seconds=3)
                                    )

            if self._scheduler and self._scheduler.get_jobs():
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
         # This dict is passed as initialConfig to Config.vue by the host
         # return None, self._get_config()
        # logger.debug(f"all_cat_rename:{self._all_cat_rename}")
        return None, {
            "enable": self._enable,
            "interval": self._interval,
            "interval_cron": self._interval_cron,
            "interval_time": self._interval_time,
            "interval_unit": self._interval_unit,
            "enable_media_tag": self._enable_media_tag,
            "enable_tag": self._enable_tag,
            "enable_category": self._enable_category,
            "downloaders": self._downloaders,
            "all_cat_rename": self._all_cat_rename,
            "all_downloaders": self._all_downloaders,
            "all_cat": self._all_cat,
            "onlyonce": False,  # 始终返回False
            "rename_type": self._rename_type,
            "path_rename": self._path_rename,
            "name": self.plugin_name,
            "catprefix": self._catprefix,
            "siteprefix": self._siteprefix
        }

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
                "enable_media_tag",
                "enable_tag",
                "enable_category",
                "downloaders",
                "onlyonce",
                "all_cat_rename",
                "rename_type",
                "path_rename",
                "catprefix",
                "siteprefix"
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
            "enable_media_tag": self._enable_media_tag,
            "enable_tag": self._enable_tag,
            "enable_category": self._enable_category,
            "downloaders": self._downloaders,
            "all_cat_rename": self._all_cat_rename,
            "all_downloaders": self._all_downloaders,
            "all_cat": self._all_cat,
            "onlyonce": False,  # 始终返回False
            "rename_type": self._rename_type,
            "path_rename": self._path_rename,
            "name": self.plugin_name,
            "catprefix": self._catprefix,
            "siteprefix": self._siteprefix
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
                "path": "/save_config",
                "endpoint": self._save_config,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存配置"
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
                            "func": self._complemented_history,
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
                            "func": self._complemented_history,
                            "kwargs": {
                                "minutes": self._interval_time
                            }
                        }]
                else:
                    return [{
                        "id": "DownloadSiteTag",
                        "name": "补全下载历史的标签与分类",
                        "trigger": CronTrigger.from_crontab(self._interval_cron),
                        "func": self._complemented_history,
                        "kwargs": {}
                    }]
        return []

    @staticmethod
    def str_to_number(s: str, i: int) -> int:
        try:
            return int(s)
        except ValueError:
            return i

    def _complemented_history(self):
        """
        补全下载历史的标签与分类
        """
        if not self.service_infos:
            return
        logger.info(f"{self.LOG_TAG}开始执行 ...")
        # 记录处理的种子, 供辅种(无下载历史)使用
        dispose_history = {}
        # 所有站点索引
        indexers = [indexer.get("name") for indexer in self.sites_helper.get_indexers()]
        # JackettIndexers索引器支持多个站点, 如果不存在历史记录, 则通过tracker会再次附加其他站点名称
        indexers.append("JackettIndexers")
        indexers = set(indexers)
        tracker_mappings = {
            "chdbits.xyz": "ptchdbits.co",
            "agsvpt.trackers.work": "agsvpt.com",
            "tracker.cinefiles.info": "audiences.me",
        }
        for service in self.service_infos.values():
            downloader = service.name
            downloader_obj = service.instance
            logger.info(f"{self.LOG_TAG}开始扫描下载器 {downloader} ...")
            if not downloader_obj:
                logger.error(f"{self.LOG_TAG} 获取下载器失败 {downloader}")
                continue
            # 获取下载器中的种子
            torrents, error = downloader_obj.get_torrents()
            # 如果下载器获取种子发生错误 或 没有种子 则跳过
            if error or not torrents:
                continue
            logger.info(f"{self.LOG_TAG}按时间重新排序 {downloader} 种子数：{len(torrents)}")
            # 按添加时间进行排序, 时间靠前的按大小和名称加入处理历史, 判定为原始种子, 其他为辅种
            torrents = self._torrents_sort(torrents=torrents, dl_type=service.type)
            logger.info(f"{self.LOG_TAG}下载器 {downloader} 分析种子信息中 ...")
            for torrent in torrents:
                try:
                    if self._event.is_set():
                        logger.info(
                            f"{self.LOG_TAG}停止服务")
                        return
                    # 获取已处理种子的key (size, name)
                    _key = self._torrent_key(torrent=torrent, dl_type=service.type)
                    # 获取种子hash
                    _hash = self._get_hash(torrent=torrent, dl_type=service.type)
                    if not _hash:
                        continue
                    # 获取种子当前标签
                    torrent_tags = self._get_label(torrent=torrent, dl_type=service.type)
                    torrent_cat = self._get_category(torrent=torrent, dl_type=service.type)

                    # 提取种子hash对应的下载历史
                    history: DownloadHistory = self.downloadhistory_oper.get_by_hash(_hash)
                    if not history:
                        # 如果找到已处理种子的历史, 表明当前种子是辅种, 否则创建一个空DownloadHistory
                        if _key and _key in dispose_history:
                            history = dispose_history[_key]
                            # 因为辅种站点必定不同, 所以需要更新站点名字 history.torrent_site
                            history.torrent_site = None
                        else:
                            history = DownloadHistory()
                    else:
                        # 加入历史记录
                        if _key:
                            dispose_history[_key] = history
                    logger.debug(f"history.title:{history.title} torrent_cat:{torrent_cat} history.type:{history.type}")
                    # 如果标签已经存在任意站点, 则不再添加站点标签
                    if indexers.intersection(set(torrent_tags)):
                        history.torrent_site = None
                    # 如果站点名称为空, 尝试通过trackers识别
                    elif not history.torrent_site:
                        trackers = self._get_trackers(torrent=torrent, dl_type=service.type)
                        for tracker in trackers:
                            # 检查tracker是否包含特定的关键字，并进行相应的映射
                            for key, mapped_domain in tracker_mappings.items():
                                if key in tracker:
                                    domain = mapped_domain
                                    break
                            else:
                                domain = StringUtils.get_url_domain(tracker)
                            site_info = self.sites_helper.get_indexer(domain)
                            # logger.debug(f"sites_helper.get_indexer domain:{domain} site_info:{site_info}")
                            if site_info:
                                if len(self._siteprefix) > 0:
                                    torrent_site = torrent_site + site_info.get("name")
                                else:
                                    torrent_site = site_info.get("name")
                                history.torrent_site = torrent_site
                                logger.debug(f"torrent_site: {torrent_site}")
                                break
                        # 如果通过tracker还是无法获取站点名称, 且tmdbid, type, title都是空的, 那么跳过当前种子
                        if not history.torrent_site and not history.tmdbid and not history.type and not history.title:
                            logger.debug(f"跳过 history.title:{history.title} torrent_cat:{torrent_cat} history.type:{history.type}")
                            continue
                    # 按设置生成需要写入的标签与分类
                    _tags = []
                    _cat = None
                    # 站点标签, 如果勾选开关的话 因允许torrent_site为空时运行到此, 因此需要判断torrent_site不为空
                    if self._enable_tag and history.torrent_site:
                        if len(self._siteprefix) > 0:
                            torrent_site = self._siteprefix + history.torrent_site
                        else:
                            torrent_site = history.torrent_site
                        _tags.append(torrent_site)
                    # 媒体标题标签, 如果勾选开关的话 因允许title为空时运行到此, 因此需要判断title不为空
                    if self._enable_media_tag and history.title:
                        _tags.append(history.title)
                    # 分类, 如果勾选开关的话 <tr暂不支持> 因允许mtype为空时运行到此, 因此需要判断mtype不为空。为防止不必要的识别, 种子已经存在分类torrent_cat时 也不执行
                    if service.type == "qbittorrent" and self._enable_category and not torrent_cat and history.type and not self._rename_type:
                        # 因允许tmdbid为空时运行到此, 因此需要判断tmdbid不为空
                        history_type = MediaType(history.type) if history.type else None
                        if history.tmdbid and history_type:
                            # tmdb_id获取tmdb信息
                            tmdb_info = self.chain.tmdb_info(mtype=history_type, tmdbid=history.tmdbid)
                            if tmdb_info:
                                # 确定二级分类
                                if tmdb_info.get('media_type') == MediaType.TV:
                                    cat = self.category_helper.get_tv_category(tmdb_info)
                                else:
                                    cat = self.category_helper.get_movie_category(tmdb_info)
                            else:
                                logger.warn(f'{history.title} 未获取到tmdb信息')

                            if cat:
                                logger.debug(f'{history.title} 本剧集类别:{cat}')
                                _cat = self._cat_rename_dict[str(cat)]
                                logger.debug(f'{history.title}本剧集映射后的类别:{_cat}')
                                if len(self._catprefix) > 0:
                                    logger.debug(f'增加自定义分类前缀:{self._catprefix}')
                                    _cat = self._catprefix + _cat
                            else:
                                logger.warn(f'{history.title} 未获取到二级分类信息')
                    # 按路径分类
                    if (service.type == "qbittorrent" and self._enable_category and not torrent_cat and history.path and
                            self._rename_type):
                        for key in self._cat_rename_dict:
                            if history.path in key:
                                print(f"{history.path} 命中路径关键字 {key}' 分类: '{self._cat_rename_dict[key]}'")
                                _cat = self._cat_rename_dict[key]
                                if len(self._catprefix) > 0:
                                    _cat = self._catprefix + _cat
                                break
                    # 去除种子已经存在的标签
                    if _tags and torrent_tags:
                        _tags = list(set(_tags) - set(torrent_tags))
                    # 如果分类一样, 那么不需要修改
                    if _cat == torrent_cat:
                        logger.debug(f"分类一样跳过处理")
                        _cat = None
                    # 判断当前种子是否不需要修改
                    if not _cat and not _tags:
                        logger.debug(f"判断当前种子是否不需要修改跳过 history.title:{history.title} torrent_cat:{torrent_cat} history.type:{history.type}")
                        continue
                    # 执行通用方法, 设置种子标签与分类
                    self._set_torrent_info(service=service, _hash=_hash, _torrent=torrent, _tags=_tags, _cat=_cat,
                                           _original_tags=torrent_tags)
                except Exception as e:
                    logger.error(
                        f"{self.LOG_TAG}分析种子信息时发生了错误: {str(e)}", exc_info=True)

        logger.info(f"{self.LOG_TAG}执行完成")

    def _genre_ids_get_cat(self, mtype, genre_ids=None):
        """
        根据genre_ids判断是否<动漫>分类
        """
        _cat = None
        if mtype == MediaType.MOVIE or mtype == MediaType.MOVIE.value:
            # 电影
            _cat = self._category_movie
        elif mtype:
            ANIME_GENREIDS = settings.ANIME_GENREIDS
            if genre_ids \
                    and set(genre_ids).intersection(set(ANIME_GENREIDS)):
                # 动漫
                _cat = self._category_anime
            else:
                # 电视剧
                _cat = self._category_tv
        return _cat

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
    def _torrents_sort(torrents: Any, dl_type: str):
        """
        按种子添加时间排序
        """
        if dl_type == "qbittorrent":
            torrents = sorted(torrents, key=lambda x: x.get("added_on"), reverse=False)
        else:
            torrents = sorted(torrents, key=lambda x: x.added_date, reverse=False)
        return torrents

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
    def _get_trackers(torrent: Any, dl_type: str):
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

    @staticmethod
    def _get_label(torrent: Any, dl_type: str):
        """
        获取种子标签
        """
        try:
            return [str(tag).strip() for tag in torrent.get("tags", "").split(',')] \
                if dl_type == "qbittorrent" else torrent.labels or []
        except Exception as e:
            print(str(e))
            return []

    @staticmethod
    def _get_category(torrent: Any, dl_type: str):
        """
        获取种子分类
        """
        try:
            return torrent.get("category") if dl_type == "qbittorrent" else None
        except Exception as e:
            print(str(e))
            return None

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
            _media = context.media_info
            _tags = []
            _cat = None
            # 站点标签, 如果勾选开关的话
            if self._enable_tag and _torrent.site_name:
                if len(self._siteprefix) > 0:
                    torrent_site = self._siteprefix + _torrent.site_name
                else:
                    torrent_site = _torrent.site_name
                _tags.append(torrent_site)
            # 媒体标题标签, 如果勾选开关的话
            if self._enable_media_tag and _media.title:
                _tags.append(_media.title)
            # 分类, 如果勾选开关的话 <tr暂不支持>
            logger.debug(f'_media.type:{_media.type}')
            if self._enable_category and _media.type and not self._rename_type:
                # tmdb_id获取tmdb信息
                tmdb_info = self.chain.tmdb_info(mtype=_media.type, tmdbid=_media.tmdb_id)
                if tmdb_info:
                    # 确定二级分类
                    if tmdb_info.get('media_type') == MediaType.TV:
                        cat = self.category_helper.get_tv_category(tmdb_info)
                    else:
                        cat = self.category_helper.get_movie_category(tmdb_info)
                else:
                    logger.warn(f'{_media.title} 未获取到tmdb信息')

                if cat:
                    logger.debug(f'{_media.title}本剧集类别:{cat}')
                    _cat = self._cat_rename_dict[str(cat)]
                    logger.debug(f'{_media.title}本剧集映射后的类别:{_cat}')
                    if len(self._catprefix) > 0:
                        logger.debug(f'增加自定义分类前缀:{self._catprefix}')
                        _cat = self._catprefix + _cat
                else:
                    logger.debug(f'本剧集类别未找到')
            # 按路径分类

            if self._enable_category and self._rename_type:
                # 提取种子hash对应的下载历史
                history: DownloadHistory = self.downloadhistory_oper.get_by_hash(_hash)
                if history is not None:
                    for key in self._cat_rename_dict:
                        if history.path in key:
                            print(f"{history.path} 命中路径关键字 {key}' 分类: '{self._cat_rename_dict[key]}'")
                            _cat = self._cat_rename_dict[key]
                            if len(self._catprefix) > 0:
                                _cat = self._catprefix + _cat
                            break
            if _hash and (_tags or _cat):
                # 执行通用方法, 设置种子标签与分类
                self._set_torrent_info(service=service, _hash=_hash, _tags=_tags, _cat=_cat)
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