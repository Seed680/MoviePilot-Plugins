import re
import datetime
import pytz
from typing import List, Tuple, Dict, Any, Optional

import chardet
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from lxml import etree

from app.schemas import NotificationType
from app.core.config import settings
from app.db.site_oper import SiteOper
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import ServiceInfo
from app.schemas.types import SystemConfigKey
from app.utils.http import RequestUtils
from torrentool.torrent import Torrent


class HanHanRescueSeeding(_PluginBase):
    # 插件名称
    plugin_name = "憨憨保种区"
    # 插件描述
    plugin_desc = "拯救憨憨保种区"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "1.2.5"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "hanhanrescueseeding_"
    # 加载顺序
    plugin_order = 16
    # 可使用的用户级别
    auth_level = 2

    domain = "hhanclub.top"
    # 私有属性
    downloader_helper = None
    _scheduler = None
    _enable = False
    _run_once = False
    _cron = None
    _downloader = None
    _seeding_count = None
    _download_limit = None
    _save_path = None
    _custom_tag = None
    _enable_notification = None
    _notify_on_zero_torrents = None

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
                self._seeding_count = config.get("seeding_count", "1-3")
                self._download_limit = config.get("download_limit", 5)
                self._save_path = config.get("save_path")
                self._custom_tag = config.get("custom_tag")
                self._enable_notification = config.get("enable_notification", False)
                self._notify_on_zero_torrents = config.get("notify_on_zero_torrents", True)

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
            "download_limit": self._download_limit,
            "all_downloaders": self._all_downloaders,
            "save_path": self._save_path,
            "custom_tag": self._custom_tag,
            "enable_notification": self._enable_notification,
            "notify_on_zero_torrents": self._notify_on_zero_torrents
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
                    "download_limit",
                    "save_path",
                    "custom_tag",
                    "enable_notification",
                    "notify_on_zero_torrents"
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
            "download_limit": self._download_limit,
            "all_downloaders": self._all_downloaders,
            "save_path": self._save_path,
            "custom_tag": self._custom_tag,
            "enable_notification": self._enable_notification,
            "notify_on_zero_torrents": self._notify_on_zero_torrents
        }


    def _get_download_records(self) -> List[Dict[str, Any]]:
        """API Endpoint: Returns download records."""
        records = self.get_data("download_records") or []
        records.reverse()
        return records

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
            },
            {
                "path": "/download_records",
                "endpoint": self._get_download_records,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取下载记录"
            },

            {
                "path": "/delete_torrents",
                "endpoint": self._delete_torrents,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "批量删除下载器中的种子"
            },
            {
                "path": "/delete_download_records",
                "endpoint": self._delete_download_records,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "批量删除下载记录"
            }
        ]


    def _delete_torrents(self, torrent_hashes: List[str] = None):
        """
        API端点：批量删除指定hashes的种子
        """
        if not torrent_hashes:
            return {"success": False, "message": "种子hash列表不能为空"}
        
        results = []
        for torrent_hash in torrent_hashes:
            success = self._delete_torrent_by_hash(torrent_hash)
            results.append({
                "hash": torrent_hash,
                "success": success
            })
        
        # 统计成功和失败的数量
        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count
        
        return {
            "success": True,
            "message": f"批量删除完成: 成功 {success_count}, 失败 {fail_count}",
            "results": results
        }

    def _delete_download_records(self, titles: List[str] = None):
        """
        API端点：批量删除指定标题的下载记录
        """
        if not titles:
            return {"success": False, "message": "标题列表不能为空"}
        
        try:
            # 获取所有下载记录
            download_records = self.get_data("download_records") or []
            
            # 过滤掉要删除的记录（基于标题）
            updated_records = [record for record in download_records if record.get("title") not in titles]
            
            # 保存更新后的记录
            self.save_data(key="download_records", value=updated_records)
            
            return {
                "success": True,
                "message": f"成功删除 {len(titles)} 条下载记录"
            }
        except Exception as e:
            logger.error(f"批量删除下载记录失败: {str(e)}")
            return {"success": False, "message": f"批量删除下载记录失败: {str(e)}"}

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
            downloaded_count = 0
            success_downloaded_count = 0
            failed_downloaded_count = 0
            # 先获取现有的下载记录列表
            download_records = self.get_data("download_records") or []
            for page in range(0, 11):
                url = "https://" + self.domain + f"/rescue.php?page={page}"
                logger.info(f"憨憨保种区第{page + 1}页:{url}")
                torrent_detail_source = self._get_page_source(url=url, site=self.site)
                if not torrent_detail_source:
                    logger.error(f"请求憨憨保种区第{page}页失败")
                    break
                # logger.debug(f"憨憨保种区第{page + 1}页详情：" +torrent_detail_source)
                html = etree.HTML(torrent_detail_source)
                if html is None:
                    logger.error(f"憨憨保种区第{page}页页面解析失败")
                    break
                elements = html.xpath('//*[@id="mainContent"]/div[1]/div[2]/div[3]/div')
                logger.info(f"第{page + 1}页数据获取{len(elements)}条数据")
                if len(elements) == 0:
                    break
                for elem in elements:
                    # 在每个找到的元素中再次通过xpath搜索
                    # 做种人数
                    seed = elem.xpath('div[3]/div/div[3]/a')
                    # 英文标题
                    title = elem.xpath('div[2]/div/a')
                    # 中文标题
                    zh_title = elem.xpath('div[2]/div/div[1]/div')
                    # 种子大小
                    size = elem.xpath('div[3]/div/div[1]')
                    sub_elem = seed[0] if len(seed) > 0 else None
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
                                        continue
                                except ValueError:
                                    logger.error(f"无效的范围格式: {seeding_count_str}")
                                    continue
                        else:
                            # 不包含-号，判断sub_elem.text是否小于该数字
                            try:
                                if int(sub_elem.text) > int(seeding_count_str):
                                    continue
                            except ValueError:
                                logger.error(f"无效的数字格式: {seeding_count_str}")
                                continue
                        # 检查下载数量限制
                        if self._download_limit > 0 and downloaded_count >= self._download_limit:
                            logger.info(f"已达到单次下载数量限制 ({self._download_limit})，停止下载")
                            return
                        # 如果做种人数在设定区间内，则下载种子
                        download_element = elem.xpath('div[4]/div/a')
                        if download_element:
                            # 下载链接
                            download_link = "https://" + self.domain + "/" + download_element[0].get('href')
                            if download_link:
                                logger.info(f"下载种子链接: {download_link}")
                                # 先下载种子文件获取hash
                                torrent_content, torrent_hash = self._download_torrent(download_link, self.site)
                                if not torrent_content:
                                    logger.error(f"下载种子文件失败: {download_link}")
                                    failed_downloaded_count += 1
                                    continue
                                
                                # 调用下载器下载种子
                                downloader = self._downloader
                                service_info = self.downloader_helper.get_service(downloader)
                                if service_info and service_info.instance:
                                    try:
                                        logger.debug(f"获取下载器实例成功: {downloader}")
                                        # 准备下载参数
                                        download_kwargs = {
                                            "content": torrent_content,  # 使用下载的种子内容而不是URL
                                            "cookie": self.site.cookie
                                        }
                                        if self._save_path:
                                            download_kwargs["download_dir"] = self._save_path
                                        # 如果有自定义标签，则添加标签参数
                                        if self._custom_tag:
                                            if service_info.type == "qbittorrent":
                                                download_kwargs["tag"] = self._custom_tag.split(',')
                                            elif service_info.type == "transmission":
                                                download_kwargs["labels"] = self._custom_tag.split(',')
                                        logger.debug(f"下载种子参数: {download_kwargs}")
                                        # 下载种子文件
                                        result = service_info.instance.add_torrent(**download_kwargs)
                                        logger.debug(f"下载结果: {result}")
                                        if result:
                                            logger.info(f"成功下载种子: {download_link}")
                                            downloaded_count += 1
                                            success_downloaded_count += 1
                                            # 获取种子信息
                                            title_text = title[0].text.strip() if title else "未知标题"
                                            zh_title_text = zh_title[0].text.strip() if zh_title else "无中文标题"
                                            size_text = size[0].text.strip() if size else "未知大小"
                                            seed_count = sub_elem.text.strip() if sub_elem is not None else "0"

                                            # 保存下载记录
                                            download_record = {
                                                "title": title_text,
                                                "zh_title": zh_title_text,
                                                "size": size_text,
                                                "seeders": seed_count,
                                                "download_link": download_link,
                                                "torrent_hash": torrent_hash,  # 使用下载时计算的种子hash
                                                "download_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            }

                                            # 使用self.save_data保存数据，以列表形式保存所有下载记录
                                            # 将新记录添加到列表中
                                            download_records.append(download_record)
                                            # 保存更新后的列表
                                            self.save_data(key="download_records", value=download_records)


                                        else:
                                            logger.error(f"下载种子失败: {download_link}")
                                            failed_downloaded_count += 1

                                    except Exception as e:
                                        logger.error(f"下载种子失败: {str(e)}")
                                        failed_downloaded_count += 1
                                else:
                                    logger.error(f"下载器 {downloader} 未连接或不可用")
                                    failed_downloaded_count += 1

            # 发送通知
            if self._enable_notification:
                # 检查是否需要在种子数为0时发送通知
                if self._notify_on_zero_torrents or success_downloaded_count > 0:
                    self.post_message(
                        mtype=NotificationType.Plugin,
                        title="【憨憨保种区】",
                        text=f"成功拯救了 {success_downloaded_count} 个种子"
                    )
        except Exception as e:
            logger.error(f"检查保种区异常:{str(e)}", exc_info=True)
            # 发送异常通知
            if self._enable_notification:
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title="【憨憨保种区】",
                    text=f"保种任务执行异常，请查看日志了解详情"
                )

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

    def _download_torrent(self, url: str, site) -> Tuple[Optional[bytes], Optional[str]]:
        """
        根据url下载种子文件，返回种子内容bytes和种子对应的hash
        """
        ret = RequestUtils(
            cookies=site.cookie,
            timeout=30,
        ).get_res(url, allow_redirects=True)
        
        if ret is not None and ret.content:
            try:
                # 使用torrentool解析种子内容并计算info hash
                torrent = Torrent.from_string(ret.content)
                torrent_hash = torrent.info_hash
                return ret.content, torrent_hash
            except Exception as e:
                logger.error(f"解析种子文件失败: {str(e)}")
                # 如果解析失败，仍然返回内容但hash为None
                return ret.content, None
        else:
            logger.error(f"下载种子失败: {url}")
            return None, None

    def _delete_torrent_by_hash(self, torrent_hash: str) -> bool:
        """
        根据hash删除下载器中的种子
        """
        if not self._downloader:
            logger.error("未配置下载器")
            return False

        service_info = self.downloader_helper.get_service(self._downloader)
        if not service_info or not service_info.instance:
            logger.error(f"下载器 {self._downloader} 未连接或不可用")
            return False

        try:
            # 根据下载器类型调用相应的删除方法
            if service_info.type == "qbittorrent":
                # Qbittorrent 删除种子
                result = service_info.instance.delete_torrents(ids=torrent_hash, delete_file=True)
                return result
            elif service_info.type == "transmission":
                # Transmission 删除种子
                result = service_info.instance.remove_torrents(ids=torrent_hash, delete_file=True)
                return result
            else:
                logger.error(f"不支持的下载器类型: {service_info.type}")
                return False
        except Exception as e:
            logger.error(f"删除种子失败 (hash: {torrent_hash}): {str(e)}")
            return False


    def get_page(self) -> List[dict]:
        return None

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