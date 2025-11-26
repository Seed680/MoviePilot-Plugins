import re
import datetime
import pytz
from typing import List, Tuple, Dict, Any, Optional

import chardet
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from lxml import etree

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import ServiceInfo
from app.schemas.types import SystemConfigKey
from app.utils.http import RequestUtils


class Test(_PluginBase):
    # 插件名称
    plugin_name = "测试插件"
    # 插件描述
    plugin_desc = "这是一个测试插件"
    # 插件图标
    plugin_icon = "test.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "Your Name"
    # 作者主页
    author_url = "https://github.com/yourname"
    # 插件配置项ID前缀
    plugin_config_prefix = "test_"
    # 加载顺序
    plugin_order = 17
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    downloader_helper = None
    _scheduler = None
    _enable = False
    _run_once = False
    _cron = None
    _downloader = None
    _test_value = None

    def init_plugin(self, config: dict = None):
        try:
            self.downloader_helper = DownloaderHelper()
            
            # 读取配置
            if config:
                logger.debug(f"读取配置：{config}")
                self._enable = config.get("enable", False)
                self._run_once = config.get("run_once", False)
                self._cron = config.get("cron")
                self._downloader = config.get("downloader", None)
                self._test_value = config.get("test_value")

            # 停止现有任务
            self.stop_service()
            if self._run_once:
                self._run_once = False
                config.update({"run_once": False})
                self.update_config(config=config)
                logger.info("立即运行测试插件")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(self._test_job, 'date',
                                        run_date=datetime.datetime.now(
                                            tz=pytz.timezone(settings.TZ)
                                        ) + datetime.timedelta(seconds=3),
                                        name="测试插件")
                if self._scheduler.get_jobs():
                    # 启动服务
                    self._scheduler.print_jobs()
                    self._scheduler.start()
        except Exception as e:
            logger.error(f"初始化失败：{str(e)}", exc_info=True)

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
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
                                            'model': 'enable',
                                            'label': '启用插件',
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
                                            'model': 'run_once',
                                            'label': '立即运行一次',
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'downloader',
                                            'label': '下载器',
                                            'items': self._all_downloaders
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
                                            'model': 'cron',
                                            'label': '执行周期',
                                            'placeholder': '0 2 * * *'
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'test_value',
                                            'label': '测试值',
                                            'placeholder': '请输入测试值'
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
                                            'variant': 'tonal'
                                        },
                                        'content': [
                                            {
                                                'component': 'span',
                                                'text': '这是一个测试插件，用于演示插件的基本结构和功能。'
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enable": self._enable,
            "run_once": self._run_once,
            "cron": self._cron,
            "downloader": self._downloader,
            "test_value": self._test_value,
            "all_downloaders": self._all_downloaders
        }

    def get_page(self) -> List[dict]:
        """
        获取插件页面
        """
        return [
            {
                'component': 'div',
                'props': {
                    'class': 'text-center'
                },
                'content': [
                    {
                        'component': 'h1',
                        'text': '测试插件'
                    },
                    {
                        'component': 'p',
                        'text': '这是一个测试插件页面'
                    }
                ]
            }
        ]

    def get_dashboard(self, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any], List[dict]]:
        """
        获取仪表板
        """
        return None, None, []

    def get_state(self) -> bool:
        return self._enable

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return []

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
        if self._enable and self._cron:
            return [{
                "id": "Test",
                "name": "测试插件服务",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self._test_job,
                "kwargs": {}
            }]
        return []

    def _test_job(self):
        """
        测试任务
        """
        try:
            if not self._enable:
                logger.info("测试插件未启用，跳过执行")
                return

            logger.info("测试插件任务执行成功")
        except Exception as e:
            logger.error(f"测试插件任务执行异常:{str(e)}", exc_info=True)

    @property
    def _all_downloaders(self) -> List[dict]:
        """
        获取全部下载器
        """
        sys_downloaders = SystemConfigOper().get(SystemConfigKey.Downloaders)
        if sys_downloaders:
            all_downloaders = [
                {"title": d.get("name"), "value": d.get("name")}
                for d in sys_downloaders
                if d.get("enabled")
            ]
        else:
            all_downloaders = []
        return all_downloaders

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            print(str(e))