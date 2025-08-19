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


class HanHanRescueSeeding(_PluginBase):
    # 插件名称
    plugin_name = "憨憨保种区"
    # 插件描述
    plugin_desc = "拯救憨憨保种区"
    # 插件图标
    plugin_icon = "hanhan.png"
    # 插件版本
    plugin_version = "1.1.5.2"
    # 插件作者
    plugin_author = "Seed"
    # 作者主页
    author_url = "Seed"
    # 插件配置项ID前缀
    plugin_config_prefix = "hanhanrescueseeding_"
    # 加载顺序
    plugin_order = 16
    # 可使用的用户级别
    auth_level = 99
    plugin_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzX5Ft4P2mFCBCOSLV65lXfoCQBIes1I6hUqGpAuHas39YkljTrK7Xyia3Ybt7ylqKJpYH8JocPubk3LZYaGRl6CKESk8ZN8t1drNonRrJtQK3f0O03M4iZCsM4EcIpkcXzL6Ox0yu9rXW+n7fnPPil6z6/tWEzAIpI9Zt1O429CRacGHvVt+S6lhtGpqON2pzGUEhNyfG+xzPo8wO/anrdR28lv3mhro2HxvpEQFXQwxdgXA/xy+CneamzB1B69n09YoRavrwswJtnEKZVHQ4MHqJxRrVOPot6HcG7CZxtDpNVJANTK0z69cz4t+SCqBk2wSz362iX9n5Tb1qCDG5wIDAQAB"
    domain = "hhanclub.top"
    # 私有属性
    downloader_helper = None
    _scheduler = None
    _enable = False
    _run_once = False
    _cron = None
    _downloader = None
    _seeding_count = None
    _save_path = None
    _custom_tag = None

    def init_plugin(self, config: dict = None):
        try: 

            self.downloader_helper = DownloaderHelper()
            # 获取站点信息
            self.site = SiteOper().get_by_domain(self.domain)
            if not self.site:
                self.domain = "hhan.club"
                self.site = SiteOper().get_by_domain(self.domain)
                if not self.site:
                    logger.error(f"憨憨站点未配置，请先在系统配置中添加站点")
                    return
            
            # 读取配置
            if config:
                logger.debug(f"读取配置：{config}")
                self._enable = config.get("enable", False)
                self._run_once = config.get("run_once", False)
                self._cron = config.get("cron")
                self._downloader = config.get("downloader", None)
                self._seeding_count = config.get("seeding_count", "1-5")
                self._save_path = config.get("save_path")
                self._custom_tag = config.get("custom_tag")

            # 停止现有任务
            self.stop_service()
            if self._run_once:
                self._run_once = False
                config.update({"run_once": False})
                self.update_config(config=config)
                logger.info("立即运行拯救憨憨保种区")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(self._check_seeding, 'date',
                                        run_date=datetime.datetime.now(
                                            tz=pytz.timezone(settings.TZ)
                                        ) + datetime.timedelta(seconds=3),
                                        name="拯救憨憨保种区")
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
        return None, {
            "enable": self._enable,
            "run_once": self._run_once,
            "cron": self._cron,
            "downloader": self._downloader,
            "seeding_count": self._seeding_count,
            "all_downloaders": self._all_downloaders,
            "save_path": self._save_path,
            "custom_tag": self._custom_tag
        }


    def load_config(self, config: dict):
        """加载配置"""
        if config:
            # 遍历配置中的键并设置相应的属性
            for key in (
                "enable",
                "run_once",
                "cron",
                "downloader",
                "seeding_count",
                "save_path",
                "custom_tag"
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
            "run_once": self._run_once,
            "cron": self._cron,
            "downloader": self._downloader,
            "seeding_count": self._seeding_count,
            "all_downloaders": self._all_downloaders,
            "save_path": self._save_path,
            "custom_tag": self._custom_tag
        }

    @property
    def service_infos(self) -> Optional[Dict[str, ServiceInfo]]:
        """
        服务信息
        """
        if not self._downloader:
            logger.warning("尚未配置下载器，请检查配置")
            return None

        services = self.downloader_helper.get_services(name_filters=self._downloader)
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
        if self._enable and self._cron:
            return [{
                "id": "HanHanRescueSeeding",
                "name": "憨憨保种区服务",
                "trigger": CronTrigger.from_crontab(self._cron),
                "func": self._check_seeding,
                "kwargs": {}
            }]
        return []

    def _check_seeding(self):
        try:
            if not self._enable:
                logger.info("憨憨保种区插件未启用，跳过检查")
                return

            if not self._downloader:
                logger.error("未配置下载器，无法执行保种任务")
                return
            
            for page in range(0, 11):
                torrent_detail_source = self._get_page_source(url=f"https://" + self.domain +"/rescue.php?page={page}", site=self.site)
                if not torrent_detail_source:
                    logger.error(f"请求憨憨保种区第{page}页失败")
                    break
                html = etree.HTML(torrent_detail_source)
                if html is None:
                    logger.error(f"憨憨保种区第{page}页页面解析失败")
                    break
                elements = html.xpath('//*[@id="mainContent"]/div[1]/div[2]/div[3]/div')
                if len(elements) == 0:
                    break
                for elem in elements:
                    # 在每个找到的元素中再次通过xpath搜索
                    seed = elem.xpath('div[3]/div/div[3]/a')
                    for sub_elem in seed:
                        # 打印子元素的文本内容和链接
                        logger.info("做种人数:", sub_elem.text)
                        # 检查做种人数是否在设定区间内
                        if sub_elem.text:
                            seeding_count_str = str(self._seeding_count)
                            if '-' in seeding_count_str:
                                # 分割范围字符串并转换为整数
                                range_parts = seeding_count_str.split('-')
                                if len(range_parts) == 2:
                                    try:
                                        lower_bound = int(range_parts[0])
                                        upper_bound = int(range_parts[1])
                                        # 检查做种人数是否在范围内
                                        if (lower_bound > int(sub_elem.text)) or (upper_bound < int(sub_elem.text)):
                                            return
                                    except ValueError:
                                        logger.error(f"无效的范围格式: {seeding_count_str}")
                                        continue
                            else:
                                # 不包含-号，判断sub_elem.text是否小于该数字
                                try:
                                    if int(sub_elem.text) > int(seeding_count_str):
                                        return
                                except ValueError:
                                    logger.error(f"无效的数字格式: {seeding_count_str}")
                                    continue
                            # 如果做种人数在设定区间内，则下载种子
                            download_element = elem.xpath('div[4]/div/a')
                            if download_element:
                                download_link = "https://" + self.domain+"/" + download_element[0].get('href')
                                if download_link:
                                    logger.info(f"下载种子链接: {download_link}")
                                    # 调用下载器下载种子
                                    for downloader in self._downloader:
                                        service_info = self.downloader_helper.get_service(downloader)
                                        if service_info and service_info.instance:
                                            try:
                                                # 准备下载参数
                                                download_kwargs = {
                                                    "content": download_link,
                                                    "cookie": self.site.cookie
                                                }
                                                if self._save_path:
                                                    download_kwargs["download_dir"] = self._save_path
                                                # 如果有自定义标签，则添加标签参数
                                                if self._custom_tag:
                                                    download_kwargs["tag"] = self._custom_tag
                                                
                                                # 下载种子文件
                                                service_info.instance.add_torrent(**download_kwargs)
                                                logger.info(f"成功下载种子: {download_link}")
                                            except Exception as e:
                                                logger.error(f"下载种子失败: {str(e)}")
                                        else:
                                            logger.error(f"下载器 {downloader} 未连接或不可用")
        except Exception as e:
            logger.error(f"检查保种区异常:{str(e)}", exc_info=True)

    def _get_page_source(self, url: str, site):
        """
        获取页面资源
        """
        ret = RequestUtils(
            cookies=site.cookie,
            timeout=30,
        ).get_res(url, allow_redirects=True)
        if ret is not None:
            # 使用chardet检测字符编码
            raw_data = ret.content
            if raw_data:
                try:
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    # 解码为字符串
                    page_source = raw_data.decode(encoding)
                except Exception as e:
                    # 探测utf-8解码
                    if re.search(r"charset=\"?utf-8\"?", ret.text, re.IGNORECASE):
                        ret.encoding = "utf-8"
                    else:
                        ret.encoding = ret.apparent_encoding
                    page_source = ret.text
            else:
                page_source = ret.text
        else:
            page_source = ""

        return page_source
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