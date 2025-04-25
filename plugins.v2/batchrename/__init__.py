# 基础库
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from typing import Any, Dict, List,Optional, Union, List
import pytz
# 第三方库
from apscheduler.schedulers.background import BackgroundScheduler

# 项目库
from app.core.context import TorrentInfo

from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger

from app.modules.qbittorrent import Qbittorrent
from app.plugins import _PluginBase

from app.schemas.types import SystemConfigKey
from app.core.config import settings

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
class TorrentInfo:
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

class QbittorrentDownloader():
    def __init__(self, qbc: Qbittorrent):
        self.qbc = qbc.qbc
    def torrents_rename(self, torrent_hash: str, new_torrent_name: str) -> None:
        self.qbc.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=new_torrent_name)

    def torrents_info(self, torrent_hash: Optional[Union[str, list]] = None) -> List[TorrentInfo]:
        """
        获取种子信息
        """
        torrents = []
        torrents_info = self.qbc.torrents_info(torrent_hashes=torrent_hash) if torrent_hash else self.qbc.torrents_info()
        if torrents_info:
            for torrent_info in torrents_info:
                torrents.append(TorrentInfo(
                    name = torrent_info.get('name'),
                    save_path = torrent_info.get('save_path'),
                    total_size = torrent_info.get('total_size'),
                    hash=torrent_info.get('hash'),
                    auto_tmm=torrent_info.get('auto_tmm'),
                    category=torrent_info.get('category'),
                    tags=torrent_info.get('tags').split(","),
                    files= [
                        TorrentFile(
                            name=file.get('name'),
                            size=file.get('size'),
                            priority=file.get('priority'))
                        for file in torrent_info.files
                    ]
                ))
            return torrents


class BatchRename(_PluginBase):
    # 插件名称
    plugin_name = "批量重命名"
    # 插件描述
    plugin_desc = "根据规则批量重命名QB种子名称"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "batchrename_"
    # 加载顺序
    plugin_order = 33
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None

    # 配置属性
    # 格式化字符
    _format_torrent_name: str = ""
    # 下载器
    _downloader: list = []
    # 立即运行一次
    _onlyonce = False


    def init_plugin(self, config: dict = None):
        self.load_config(config)
        self.downloader_helper = DownloaderHelper()
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
                                    ) + timedelta(seconds=3),
                                    name="批量替换下载器种子")


    def load_config(self, config: dict):
        """加载配置"""
        if config:
            # 遍历配置中的键并设置相应的属性
            for key in (
                "downloader",
                "format_torrent_name",
                "onlyonce"
            ):
                setattr(self, f"_{key}", config.get(key, getattr(self, f"_{key}")))

    def get_form(self):
        _downloaders = [{"title": d.get("name"), "value": [d.get("name")]} for d in SystemConfigOper().get(SystemConfigKey.Downloaders) if d.get("enabled")]
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'downloader',
                                            'label': '启用下载器',
                                            # 'chips': True,
                                            'multiple': False,
                                            'clearable': True,
                                            'items': _downloaders,
                                        }
                                    }
                                ]
                            },
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
                            },
                            
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'rows': 4,
                                            'auto-grow': True,
                                            'model': 'format_torrent_name',
                                            'label': '替换配置',
                                            'placeholder': '每一行一个配置，中间以|分隔\n'
                                                           '待替换文本|替换的文本',
                                            'clearable': True,
                                            'persistent-hint': True,
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
            "downloader": [],
            "format_torrent_name": "",
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
        """
        处理下载器中的种子
        """
        try:
            name_dict: dict[str : str] = {}
            if len(self._downloader) == 0:
                logger.info("下载器为空")
                return
            if self._format_torrent_name:
                formate_rule_list = self._format_torrent_name.strip().split("\n")
                if len(formate_rule_list) < 1:
                     logger.info("替换规则为空")
                for rule in formate_rule_list:
                    if '|' not in rule:
                        logger.info(f"{rule}未包含|")
                        return
                    name_list = rule.split("|")
                    if len(name_list) < 2 or len(name_list) > 2:
                        logger.info(f"{name_list}不符合规则")
                        return
                    name_dict[name_list[0]] = name_list[1]
                    
                # 从下载器获取种子信息
                for d in self._downloader:
                    self.set_downloader(d)
                    if self.downloader is None:
                        logger.info(f"下载器: {d} 不存在或未启用")
                        continue
                    # 遍历所有种子
                    for torrent_info in self.downloader.torrents_info():
                        if torrent_info:
                            torrent_hash = torrent_info.hash
                            torrent_name = torrent_info.name
                            for old_name in name_dict.keys():
                                torrent_name = torrent_name.replace(old_name, name_dict[old_name])
                            self.downloader.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=str(torrent_name))
        except Exception as e:
            logger.error(f"种子重命名失败 {str(e)}", exc_info=True)