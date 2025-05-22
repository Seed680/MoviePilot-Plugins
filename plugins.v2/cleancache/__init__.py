# 基础库
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytz
# 第三方库
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.cache import cache_backend
from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase


# 项目库


class CleanCache(_PluginBase):
    # 插件名称
    plugin_name = "清除后端缓存"
    # 插件描述
    plugin_desc = "立即清除后端缓存"
    # 插件图标
    plugin_icon = "spider.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "cleancache_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None
    # 立即运行一次
    _onlyonce = False


    def init_plugin(self, config: dict = None):
        self.load_config(config)
        # 停止现有任务
        self.stop_service()
        if self._onlyonce:
            self._onlyonce = False
            config.update({"onlyonce": False})
            self.update_config(config=config)
            logger.info("立即运行一次任务")
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(self.main, 'date',
                                    run_date=datetime.now(
                                        tz=pytz.timezone(settings.TZ)
                                    ) + timedelta(seconds=2),
                                    name="立即清除缓存")
            self._scheduler.print_jobs()
            self._scheduler.start()

    def load_config(self, config: dict):
        """加载配置"""
        if config:
            # 遍历配置中的键并设置相应的属性
            for key in (
                "onlyonce",
            ):
                setattr(self, f"_{key}", config.get(key, getattr(self, f"_{key}")))

    def get_form(self):
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 6, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即运行一次',
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "onlyonce": False,
        }

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        pass

    def stop_service(self):
        """退出插件"""
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"退出插件失败：{str(e)}", exc_info=True)

    def get_api(self):
        pass

    def get_command(self):
        pass

    def get_page(self):
        pass

    def get_state(self):
        return self._onlyonce

    def main(self):
        logger.info("开始清理全部缓存")
        cache_backend.clear()
        logger.info("清理全部缓存结束")