import gc
import hashlib
from typing import Any, Dict, List, Tuple

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.application.image import WallpaperHelper
from app.chain import ChainBase
from app.chain.mediaserver import MediaServerChain
from app.chain.recommend import RecommendChain
from app.chain.site import SiteChain
from app.chain.subscribe import SubscribeChain
from app.chain.transfer import TransferChain
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.sdk.logging import logger
from app.sdk.plugins import PluginManager
from app.sdk.services import ServiceConfigHelper


class ServiceManagerMod(_PluginBase):
    plugin_name = "服务管理魔改版"
    plugin_desc = "通过插件服务契约自定义系统定时服务。"
    plugin_icon = "https://raw.githubusercontent.com/Seed680/MoviePilot-Plugins/main/icons/customplugin.png"
    plugin_version = "2.0.0"
    plugin_author = "Seed680"
    author_url = "https://github.com/Seed680"
    plugin_config_prefix = "servicemanagermod_"
    plugin_order = 29
    auth_level = 1
    LOG_TAG = "[ServiceManagerMod]"

    _enabled = False
    _reset_and_disable = False
    _cookiecloud_cron = ""
    _mediaserver_sync_cron = ""
    _sitedata_refresh = ""
    _subscribe_search = ""
    _new_subscribe_search_cron = ""
    _clear_cache = ""
    _random_wallpager = ""
    _subscribe_tmdb = ""
    _subscribe_refresh = ""
    _subscribe_follow_cron = ""
    _transfer_cron = ""
    _recommend_refresh_cron = ""
    _plugin_market_refresh_cron = ""
    _subscribe_calendar_cache_cron = ""
    _scheduler_job_cron = ""
    _full_gc_cron = ""

    _CONFIG_FIELDS = {
        "cookiecloud_cron": "_cookiecloud_cron",
        "mediaserver_sync_cron": "_mediaserver_sync_cron",
        "sitedata_refresh": "_sitedata_refresh",
        "subscribe_search": "_subscribe_search",
        "new_subscribe_search_cron": "_new_subscribe_search_cron",
        "clear_cache": "_clear_cache",
        "random_wallpager": "_random_wallpager",
        "subscribe_tmdb": "_subscribe_tmdb",
        "subscribe_refresh": "_subscribe_refresh",
        "subscribe_follow_cron": "_subscribe_follow_cron",
        "transfer_cron": "_transfer_cron",
        "recommend_refresh_cron": "_recommend_refresh_cron",
        "plugin_market_refresh_cron": "_plugin_market_refresh_cron",
        "subscribe_calendar_cache_cron": "_subscribe_calendar_cache_cron",
        "scheduler_job_cron": "_scheduler_job_cron",
        "full_gc_cron": "_full_gc_cron",
    }

    _DEFAULT_JOB_FIELDS = {
        "cookiecloud": "_cookiecloud_cron",
        "sitedata_refresh": "_sitedata_refresh",
        "subscribe_search": "_subscribe_search",
        "new_subscribe_search": "_new_subscribe_search_cron",
        "clear_cache": "_clear_cache",
        "random_wallpager": "_random_wallpager",
        "subscribe_tmdb": "_subscribe_tmdb",
        "subscribe_refresh": "_subscribe_refresh",
        "subscribe_follow": "_subscribe_follow_cron",
        "transfer": "_transfer_cron",
        "recommend_refresh": "_recommend_refresh_cron",
        "plugin_market_refresh": "_plugin_market_refresh_cron",
        "subscribe_calendar_cache": "_subscribe_calendar_cache_cron",
        "scheduler_job": "_scheduler_job_cron",
        "full_gc": "_full_gc_cron",
    }

    def init_plugin(self, config: dict = None):
        config = config or {}
        self._enabled = bool(config.get("enabled", False))
        self._reset_and_disable = bool(config.get("reset_and_disable", False))
        for key, attribute in self._CONFIG_FIELDS.items():
            setattr(self, attribute, config.get(key) or "")

        if self._reset_and_disable:
            self._enabled = False
            config.update({"enabled": False, "reset_and_disable": False})
            for key, attribute in self._CONFIG_FIELDS.items():
                config[key] = ""
                setattr(self, attribute, "")
            self.update_config(config=config)
            Scheduler().remove_plugin_job(pid=self.__class__.__name__)
            logger.warning(f"{self.LOG_TAG} 已停用并清理本插件任务；恢复宿主默认任务需重启 MoviePilot 生效")
            return

    def _remove_replaced_default_jobs(self):
        scheduler = Scheduler()
        pid = self.__class__.__name__
        for job_id, attribute in self._DEFAULT_JOB_FIELDS.items():
            if getattr(self, attribute):
                scheduler.remove_plugin_job(pid=pid, job_id=job_id)

        if self._mediaserver_sync_cron:
            for job_id in self._mediaserver_default_job_ids():
                scheduler.remove_plugin_job(pid=pid, job_id=job_id)

    @staticmethod
    def _mediaserver_default_job_ids() -> List[str]:
        job_ids = []
        seen = set()
        for mediaserver in ServiceConfigHelper.get_mediaserver_configs():
            if not mediaserver or not mediaserver.enabled or not mediaserver.name:
                continue
            digest = hashlib.sha256(mediaserver.name.encode("utf-8")).hexdigest()[:12]
            job_id = f"mediaserver_sync_{digest}"
            if job_id not in seen:
                seen.add(job_id)
                job_ids.append(job_id)
        return job_ids

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def _cron_service(job_id: str, name: str, expression: str, func, func_kwargs: dict = None) -> dict:
        return {
            "id": job_id,
            "name": name,
            "trigger": CronTrigger.from_crontab(expression),
            "func": func,
            "func_kwargs": func_kwargs or {},
            "kwargs": {},
        }

    def get_service(self) -> List[Dict[str, Any]]:
        if not self._enabled:
            return []

        site_chain = SiteChain()
        subscribe_chain = SubscribeChain()
        services = []
        cron_services = [
            ("cookiecloud", "同步 CookieCloud 站点", self._cookiecloud_cron, site_chain.sync_cookies, {}),
            ("mediaserver_sync", "同步媒体服务器", self._mediaserver_sync_cron, MediaServerChain().sync, {}),
            ("sitedata_refresh", "站点数据刷新", self._sitedata_refresh, site_chain.refresh_userdatas, {}),
            ("subscribe_search", "订阅搜索补全", self._subscribe_search, subscribe_chain.search, {"state": "R"}),
            ("new_subscribe_search", "新增订阅搜索", self._new_subscribe_search_cron, subscribe_chain.search, {"state": "N"}),
            ("clear_cache", "缓存清理", self._clear_cache, self.clear_cache, {}),
            ("random_wallpager", "壁纸缓存", self._random_wallpager, WallpaperHelper().get_wallpapers, {}),
            ("subscribe_refresh", "订阅刷新", self._subscribe_refresh, subscribe_chain.refresh, {}),
            ("subscribe_follow", "关注的订阅分享", self._subscribe_follow_cron, subscribe_chain.follow, {}),
            ("transfer", "下载文件整理", self._transfer_cron, TransferChain().process, {}),
            ("recommend_refresh", "推荐缓存", self._recommend_refresh_cron, RecommendChain().refresh_recommend, {}),
            ("plugin_market_refresh", "插件市场缓存", self._plugin_market_refresh_cron,
             PluginManager().async_get_online_plugins, {"force": True}),
            ("subscribe_calendar_cache", "订阅日历缓存", self._subscribe_calendar_cache_cron,
             subscribe_chain.cache_calendar, {}),
            ("scheduler_job", "公共定时服务", self._scheduler_job_cron, ChainBase().scheduler_job, {}),
            ("full_gc", "主动内存回收", self._full_gc_cron, self.full_gc, {}),
        ]
        for job_id, name, expression, func, func_kwargs in cron_services:
            if expression:
                services.append(self._cron_service(job_id, name, expression, func, func_kwargs))

        if self._subscribe_tmdb:
            try:
                hours = max(int(self._subscribe_tmdb), 1)
            except (TypeError, ValueError):
                hours = 1
            services.append({
                "id": "subscribe_tmdb",
                "name": "订阅元数据更新",
                "trigger": IntervalTrigger(hours=hours),
                "func": subscribe_chain.check,
                "func_kwargs": {},
                "kwargs": {},
            })

        # 所有表达式验证成功后再替换宿主任务，避免无效 cron 先移除默认任务。
        self._remove_replaced_default_jobs()
        return services

    @staticmethod
    def clear_cache():
        ChainBase().clear_cache()

    @staticmethod
    def full_gc():
        collected = gc.collect()
        logger.info(f"[ServiceManagerMod] 主动内存回收完成，回收对象数：{collected}")

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        labels = {
            "sitedata_refresh": "站点数据刷新",
            "subscribe_search": "订阅搜索补全",
            "clear_cache": "缓存清理",
            "random_wallpager": "壁纸缓存",
            "subscribe_tmdb": "订阅元数据更新（小时）",
            "subscribe_refresh": "订阅刷新",
            "cookiecloud_cron": "CookieCloud 同步",
            "mediaserver_sync_cron": "媒体服务器同步",
            "full_gc_cron": "主动内存回收",
            "new_subscribe_search_cron": "新增订阅搜索",
            "subscribe_follow_cron": "订阅分享",
            "transfer_cron": "文件整理",
            "recommend_refresh_cron": "推荐缓存",
            "plugin_market_refresh_cron": "插件市场缓存",
            "subscribe_calendar_cache_cron": "订阅日历缓存",
            "scheduler_job_cron": "公共定时服务",
        }
        controls = [{
            "component": "VSwitch",
            "props": {"model": "enabled", "label": "启用插件"},
        }, {
            "component": "VSwitch",
            "props": {"model": "reset_and_disable", "label": "恢复默认并停用"},
        }]
        for key, label in labels.items():
            component = "VTextField" if key == "subscribe_tmdb" else "VCronField"
            props = {"model": key, "label": label}
            if component == "VTextField":
                props.update({"type": "number", "min": "1"})
            controls.append({"component": component, "props": props})

        rows = []
        for index in range(0, len(controls), 4):
            rows.append({
                "component": "VRow",
                "content": [{
                    "component": "VCol",
                    "props": {"cols": 12, "md": 3},
                    "content": [control],
                } for control in controls[index:index + 4]],
            })
        rows.append({
            "component": "VAlert",
            "props": {
                "type": "warning",
                "variant": "tonal",
                "text": "停用或恢复默认后，宿主默认任务需重启 MoviePilot 才会重新注册。",
            },
        })
        defaults = {"enabled": False, "reset_and_disable": False}
        defaults.update({key: "" for key in labels})
        return [{"component": "VForm", "content": rows}], defaults

    def get_page(self) -> List[dict]:
        return []

    def stop_service(self):
        Scheduler().remove_plugin_job(pid=self.__class__.__name__)
        self._enabled = False
        logger.warning(f"{self.LOG_TAG} 已清理本插件任务；恢复宿主默认任务需重启 MoviePilot 生效")
