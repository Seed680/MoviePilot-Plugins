import threading
import datetime
from typing import Any, Dict, List, Tuple

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.chain.site import SiteChain
from app.chain.subscribe import SubscribeChain
from app.chain.tmdb import TmdbChain
from app.chain.subscribe import SubscribeChain
from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler

lock = threading.Lock()


class ServiceManagerMod(_PluginBase):
    # 插件名称
    plugin_name = "服务管理魔改版"
    # 插件描述
    plugin_desc = "实现自定义服务管理。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/Seed680/MoviePilot-Plugins/main/icons/customplugin.png"
    # 插件版本
    plugin_version = "1.9"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "servicemanagermod_"
    # 加载顺序
    plugin_order = 29
    # 可使用的用户级别
    auth_level = 1
    # 日志前缀
    LOG_TAG = "[ServiceManagerMod]"

    # region 私有属性
    # 是否开启
    _enabled = False
    # 恢复默认并停用
    _reset_and_disable = False
    # 站点数据刷新（cron 表达式）
    _sitedata_refresh = ""
    # 订阅搜索补全（cron 表达式）
    _subscribe_search = ""
    # 缓存清理（cron 表达式）
    _clear_cache = ""
    # 壁纸缓存（cron 表达式）
    _random_wallpager = ""
    # 订阅元数据更新（小时）
    _subscribe_tmdb = ""
    # 订阅刷新（cron 表达式）
    _subscribe_refresh = ""
    _scheduler = None
    # endregion

    def init_plugin(self, config: dict = None):
        if not config:
            return

        self._enabled = config.get("enabled", False)
        self._reset_and_disable = config.get("reset_and_disable", False)
        self._sitedata_refresh = config.get("sitedata_refresh")
        self._subscribe_search = config.get("subscribe_search")
        self._clear_cache = config.get("clear_cache")
        self._random_wallpager = config.get("random_wallpager")
        self._subscribe_tmdb = config.get("subscribe_tmdb")
        self._subscribe_refresh = config.get("subscribe_refresh")
        if self._enabled:
            # 延迟清除系统服务并添加自定义服务
            logger.info("插件已启用，30秒后清除系统服务并添加自定义服务")
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(func=self.update_services, trigger='date',
                                        run_date=datetime.datetime.now(
                                            tz=pytz.timezone(settings.TZ)) + datetime.timedelta(seconds=30)
                                        )
            if self._scheduler and self._scheduler.get_jobs():
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()
        
        if self._reset_and_disable:
            self._enabled = False
            self._reset_and_disable = False
            config["enabled"] = False
            config["reset_and_disable"] = False
            self.update_config(config=config)
            Scheduler().init()
            logger.info("已恢复默认配置并停用插件")


    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                            'hint': '开启后插件将处于激活状态',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'reset_and_disable',
                                            'label': '恢复默认并停用',
                                            'hint': '启用此选项将恢复默认配置并停用插件',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'sitedata_refresh',
                                            'label': '站点数据刷新',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置站点数据刷新的周期，如 0 8 * * * 表示每天 8:00',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'subscribe_search',
                                            'label': '订阅搜索补全',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置订阅搜索补全的周期，如 0 12 * * * 表示每天中午 12:00',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'clear_cache',
                                            'label': '缓存清理',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置缓存清理任务的周期，如 0 3 * * * 表示每天凌晨 3:00',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'random_wallpager',
                                            'label': '壁纸缓存',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置壁纸缓存更新的周期，如 0 6 * * * 表示每天早晨 6:00',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'subscribe_tmdb',
                                            'label': '订阅元数据更新',
                                            'type': 'number',
                                            "min": "1",
                                            'placeholder': '最低不能小于1',
                                            'hint': '设置订阅元数据更新的周期，如 1/3/6/12，最低为 1',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VCronField',
                                        'props': {
                                            'model': 'subscribe_refresh',
                                            'label': '订阅刷新',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置订阅刷新的周期，如 0 */6 * * * 表示每6小时执行一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '注意：启用本插件后，默认的系统服务将失效，仅以本插件设置为准'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '注意：系统服务正在运行时，请慎重启停用，否则可能导致死锁等一系列问题'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'error',
                                            'variant': 'tonal',
                                            'text': '注意：请勿随意调整服务频率，否则可能导致站点警告、封禁等后果，相关风险请自行评估与承担'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "reset_and_disable": False
        }

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """
        退出插件，恢复系统默认的定时任务
        """
        logger.info("正在停止服务管理魔改版插件，恢复系统默认定时任务...")
        
        # 获取Scheduler实例
        scheduler_instance = Scheduler()
        
        # 移除插件添加的所有自定义服务
        job_ids = ["sitedata_refresh", "subscribe_search", "clear_cache", "random_wallpager", "subscribe_tmdb", "subscribe_refresh"]
        for job_id in job_ids:
            try:
                scheduler_instance.remove_plugin_job(pid=self.__class__.__name__, job_id=job_id)
            except Exception as e:
                logger.debug(f"移除任务 {job_id} 时出错: {str(e)}")
        
        # 重新初始化系统默认任务
        scheduler_instance.init()
        logger.info("已恢复系统默认定时任务")

    @staticmethod
    def clear_cache():
        """
        清理缓存
        """
        Scheduler().clear_cache()

    def update_services(self):
        """
        更新服务，直接操作Scheduler的_jobs和_scheduler
        """
        # 获取Scheduler实例
        scheduler_instance = Scheduler()
        
        # 移除默认服务
        if self._sitedata_refresh:
            scheduler_instance.remove_plugin_job(pid="None", job_id="sitedata_refresh")
        if settings.SUBSCRIBE_SEARCH and self._subscribe_search:
            scheduler_instance.remove_plugin_job(pid="None", job_id="subscribe_search")
        if self._clear_cache:
            scheduler_instance.remove_plugin_job(pid="None", job_id="clear_cache")
        if self._random_wallpager:
            scheduler_instance.remove_plugin_job(pid="None", job_id="random_wallpager")
        if self._subscribe_tmdb:
            scheduler_instance.remove_plugin_job(pid="None", job_id="subscribe_tmdb")
        
        # 移除订阅刷新服务
        if self._subscribe_refresh:
            # 在spider模式下，需要移除所有以subscribe_refresh开头的任务
            if settings.SUBSCRIBE_MODE == "spider":
                # 获取所有任务并移除subscribe_refresh相关的任务
                jobs = scheduler_instance._scheduler.get_jobs()
                for job in jobs:
                    if job.id.startswith("subscribe_refresh|"):
                        try:
                            scheduler_instance.remove_plugin_job(pid="None", job_id=job.id)
                        except Exception as e:
                            logger.debug(f"移除任务 {job.id} 时出错: {str(e)}")
            else:
                # RSS模式下直接移除subscribe_refresh任务
                try:
                    scheduler_instance.remove_plugin_job(pid="None", job_id="subscribe_refresh")
                except Exception as e:
                    logger.debug(f"移除任务 subscribe_refresh 时出错: {str(e)}")
        
        # 添加自定义服务
        self.add_custom_services(scheduler_instance)
        logger.info("插件重新注册服务")

    def add_custom_services(self, scheduler_instance):
        """
        添加自定义服务到Scheduler
        """
        # 站点数据刷新服务
        if self._sitedata_refresh:
            job_id = "sitedata_refresh"
            scheduler_instance._jobs[job_id] = {
                "func": SiteChain().refresh_userdatas,
                "name": "站点数据刷新",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                CronTrigger.from_crontab(self._sitedata_refresh),
                id=job_id,
                name="站点数据刷新",
                kwargs={"job_id": job_id},
                replace_existing=True
            )

        # 订阅搜索补全服务
        if settings.SUBSCRIBE_SEARCH and self._subscribe_search:
            job_id = "subscribe_search"
            scheduler_instance._jobs[job_id] = {
                "func": SubscribeChain().search,
                "name": "订阅搜索补全",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {"state": "R"},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                CronTrigger.from_crontab(self._subscribe_search),
                id=job_id,
                name="订阅搜索补全",
                kwargs={"job_id": job_id, "state": "R"},
                replace_existing=True
            )

        # 缓存清理服务
        if self._clear_cache:
            job_id = "clear_cache"
            scheduler_instance._jobs[job_id] = {
                "func": self.clear_cache,
                "name": "缓存清理",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                CronTrigger.from_crontab(self._clear_cache),
                id=job_id,
                name="缓存清理",
                kwargs={"job_id": job_id},
                replace_existing=True
            )

        # 壁纸缓存更新服务
        if self._random_wallpager:
            job_id = "random_wallpager"
            scheduler_instance._jobs[job_id] = {
                "func": TmdbChain().get_trending_wallpapers,
                "name": "壁纸缓存",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                CronTrigger.from_crontab(self._random_wallpager),
                id=job_id,
                name="壁纸缓存",
                kwargs={"job_id": job_id},
                replace_existing=True
            )

        # 订阅元数据更新服务
        if self._subscribe_tmdb:
            try:
                subscribe_tmdb = max(int(self._subscribe_tmdb or 1), 1)
            except (ValueError, TypeError):
                subscribe_tmdb = 1
                
            job_id = "subscribe_tmdb"
            scheduler_instance._jobs[job_id] = {
                "func": SubscribeChain().check,
                "name": "订阅元数据更新",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                "interval",
                id=job_id,
                name="订阅元数据更新",
                hours=subscribe_tmdb,
                kwargs={"job_id": job_id},
                replace_existing=True
            )

        # 订阅刷新服务
        if self._subscribe_refresh:
            job_id = "subscribe_refresh"
            scheduler_instance._jobs[job_id] = {
                "func": SubscribeChain().refresh,
                "name": "订阅刷新",
                "pid": self.__class__.__name__,
                "provider_name": self.plugin_name,
                "kwargs": {},
                "running": False,
            }
            scheduler_instance._scheduler.add_job(
                scheduler_instance.start,
                CronTrigger.from_crontab(self._subscribe_refresh),
                id=job_id,
                name="订阅刷新",
                kwargs={"job_id": job_id},
                replace_existing=True
            )

        logger.info("自定义服务添加完成")