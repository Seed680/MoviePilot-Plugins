# 基础库
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import Any, Dict, List, Optional, Tuple
import pytz

# 第三方库
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

# 项目库
from app.core.context import MediaInfo, TorrentInfo, Context
from app.core.event import eventmanager, Event
from app.core.meta.metabase import MetaBase
from app.core.metainfo import MetaInfo, MetaInfoPath
from app.db.downloadhistory_oper import DownloadHistoryOper, DownloadHistory, DownloadFiles
from app.db import db_update
from app.db.models.plugindata import PluginData
from app.db.systemconfig_oper import SystemConfigOper
from app.helper.downloader import DownloaderHelper
from app.log import logger
from app.modules.filemanager import FileManagerModule
from app.modules.qbittorrent import Qbittorrent
from app.modules.transmission import Transmission
from app.plugins import _PluginBase
from app.schemas.types import EventType, MediaType
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



class Downloader(metaclass=ABCMeta):
    @abstractmethod
    def torrents_rename(self, torrent_hash: str, new_torrent_name: str) -> None:
        """
        重命名种子
        """
        pass

    @abstractmethod
    def torrents_info(self, torrent_hash: str = None) -> List[TorrentInfo]:
        """
        获取种子信息
        """
        pass


class QbittorrentDownloader(Downloader):
    def __init__(self, qbc: Qbittorrent):
        self.qbc = qbc.qbc
    def torrents_rename(self, torrent_hash: str, new_torrent_name: str) -> None:
        self.qbc.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=new_torrent_name)

    def torrents_info(self, torrent_hash: str = None) -> List[TorrentInfo]:
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


class RenameTorrent(_PluginBase):
    # 插件名称
    plugin_name = "重命名种子(基于wikrin修改)"
    # 插件描述
    plugin_desc = "根据自定义格式修改MP下载种子的种子名称"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/wikrin/MoviePilot-Plugins/main/icons/alter_1.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "qiaoyun680"
    # 作者主页
    author_url = "https://github.com/qiaoyun680"
    # 插件配置项ID前缀
    plugin_config_prefix = "renametorrent_"
    # 加载顺序
    plugin_order = 33
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None

    # 配置属性
    # cron表达式
    _cron: str = ""
    # 启用定时任务
    _cron_enabled: bool = False
    # 启用事件监听
    _event_enabled: bool = False
    # 格式化字符
    _format_torrent_name: str = ""
    # 下载器
    _downloader: list = []
    # 排除标签
    _exclude_tags: str = ""
    # 排除目录
    _exclude_dirs: str = ""
    # 立即运行一次
    _onlyonce = False
    # 恢复记录
    _recovery = False

    def init_plugin(self, config: dict = None):
        self.load_config(config)
        self.downloader_helper = DownloaderHelper()
        self.downloadhis = DownloadHistoryOper()
        # 停止现有任务
        self.stop_service()
        if self._onlyonce:
            self._onlyonce = False
            config.update({"onlyonce": False})
            self.update_config(config=config)

            if self._recovery:
                config.update({"recovery": False})
                logger.info("立即恢复重命名下载器种子任务")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(self.recoveryTorrent, 'date',
                                        run_date=datetime.now(
                                            tz=pytz.timezone(settings.TZ)
                                        ) + timedelta(seconds=3),
                                        name="恢复重命名下载器种子")
            else:
                logger.info("立即运行一次重命名下载器种子任务")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(self.cron_process_main, 'date',
                                        run_date=datetime.now(
                                            tz=pytz.timezone(settings.TZ)
                                        ) + timedelta(seconds=3),
                                        name="重命名下载器种子")

            if self._scheduler.get_jobs():
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()


    def load_config(self, config: dict):
        """加载配置"""
        if config:
            # 遍历配置中的键并设置相应的属性
            for key in (
                "cron",
                "cron_enabled",
                "event_enabled",
                "downloader",
                "exclude_dirs",
                "exclude_tags",
                "format_torrent_name",
                "onlyonce",
                "recovery"
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
                                'props': {'cols': 6, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'event_enabled',
                                            'label': '启用事件监听',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 6, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'cron_enabled',
                                            'label': '启用定时任务',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 6, 'md': 3},
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
                            {
                                'component': 'VCol',
                                'props': {'cols': 6, 'md': 3},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'recovery',
                                            'label': '恢复重命名',
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
                                    'cols': 6,
                                    'md': 3,
                                    'style': {
                                        'margin-top': '12px'    # 设置上边距, 确保`label`不被遮挡
                                    }
                                },
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
                                'props': {
                                    'cols': 6,
                                    'md': 3,
                                    'style': {
                                        'margin-top': '12px'    # 设置上边距, 确保`label`不被遮挡
                                    }
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '执行周期',
                                            'placeholder': '0 8 * * *',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 5,
                                    'md': 3,
                                    'style': {
                                        'margin-top': '12px'    # 设置上边距, 确保`label`不被遮挡
                                    },
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'exclude_tags',
                                            'label': '排除标签',
                                            'placeholder': '注意: 空白字符会排除所有未设置标签的种子',
                                            'hint': '多个标签用, 分割',
                                            'clearable': True,
                                            'persistent-hint': True,
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
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'rows': 3,
                                            'auto-grow': True,
                                            'model': 'exclude_dirs',
                                            'label': '排除目录',
                                            'hint': '排除目录, 一行一个, 路径深度不能超过保存路径',
                                            'placeholder': r' 例如:\n /mnt/download \n E:\download',
                                            'clearable': True,
                                            'persistent-hint': True,
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
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'rows': 2,
                                            'auto-grow': True,
                                            'model': 'format_torrent_name',
                                            'label': '种子标题重命名格式',
                                            'hint': '使用Jinja2语法, 所用变量与主程序相同',
                                            'clearable': True,
                                            'persistent-hint': True,
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
                                            'text': '种子重命名: 重命名种子在下载器显示的名称,qBittorrent 不会影响保存路径和种子内容布局; Transmission 不支持'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "cron_enabled": False,
            "downloader": [],
            "exclude_dirs": "",
            "exclude_tags": "",
            "cron": "",
            "event_enabled": False,
            "rename_torrent": False,
            "format_torrent_name": "{{ title }}{% if year %} ({{ year }}){% endif %}{% if season_episode %} - {{season_episode}}{% endif %}.{{original_name}}",
        }

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        if self._cron_enabled:
            return [
                {
                    "id": "RenameTorrent",
                    "name": "种子重命名格式化",
                    "trigger": CronTrigger.from_crontab(self._cron or "0 8 * * *"),
                    "func": self.cron_process_main,
                    "kwargs": {},
                }
            ]
        return []

    def stop_service(self):
        """退出插件"""
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"退出插件失败：{str(e)}")

    def get_api(self):
        pass

    def get_command(self):
        pass

    def get_page(self):
        pass

    def get_state(self):
        return self._event_enabled or self._cron_enabled

    @eventmanager.register(EventType.DownloadAdded)
    def event_process_main(self, event: Event):
        """
        处理事件
        """
        if not self._event_enabled \
            and not event:
            return
        event_data = event.event_data or {}
        hash = event_data.get("hash")
        downloader = event_data.get("downloader")
        # 获取待处理数据
        if self._event_enabled and downloader in self._downloader:
            context: Context = event_data.get("context")
            if self.main(downloader=downloader, hash=hash, meta=context.meta_info, media_info=context.media_info):
                # 获取已处理数据
                processed: dict[str, str] = self.get_data(key="processed") or {}
                # 添加到已处理数据库
                processed[hash] = downloader
                # 保存已处理数据
                self.update_data(key="processed", value=processed)
            else:
                # 保存未完成数据
                pending = self.get_data(key="pending") or {}
                pending[hash] = downloader
                self.update_data("pending", pending)

    def cron_process_main(self):
        """
        定时任务处理下载器中的种子
        """
        # 失败数据列表
        _failures: dict[str, str] = {}
        # 获取待处理数据
        pending: dict[str, str] = self.get_data(key="pending") or {}
        # 获取已处理数据
        processed: dict[str, str] = self.get_data(key="processed") or {}
        _processed_num = 0

        def create_hash_mapping() -> Dict[str, List[str]]:
            """
            生成源种子hash表
            """
            # 辅种插件数据
            assist: List[PluginData] = self.get_data(key=None, plugin_id="IYUUAutoSeed") or []
            # 辅种数据映射表 key: 源种hash, value: 辅种hash列表
            _mapping: dict[str, List[str]] = {}

            if assist:
                for seed_data in assist:
                    hashes = []
                    for a in seed_data.value:
                        hashes.extend(a.get("torrents", []))
                    if seed_data.key in _mapping:
                        # 辅种插件中使用的源种子hash是下载的, 将辅种hash列表合并
                        _mapping[seed_data.key].extend(hashes)
                    else:
                        # 辅种插件中使用的源种子hash不是字典的键, 需要再次判断是不是辅种产生的种子
                        for _current_hash, _hashes in _mapping.items():
                            if seed_data.key in _hashes:
                                _mapping[_current_hash].extend(hashes)
                                break
                        # 不是辅种产生的种子, 作为源种子添加
                        _mapping[seed_data.key] = hashes
            return _mapping

        # 从下载器获取种子信息
        for d in self._downloader:
            self.set_downloader(d)
            if self.downloader is None:
                logger.warn(f"下载器: {d} 不存在或未启用")
                continue
            torrents_info = [torrent_info for torrent_info in self.downloader.torrents_info() if torrent_info.hash not in processed or torrent_info.hash in pending]
            if torrents_info:
                # 先生成源种子hash表
                assist_mapping = create_hash_mapping()
                for torrent_info in torrents_info:
                    _hash = ""
                    if assist_mapping:
                        for source_hash, seeds in assist_mapping.items():
                            if torrent_info.hash in seeds:
                                # 使用源下载种子识别
                                _hash = source_hash
                                break
                    # 通过hash查询下载历史记录
                    downloadhis = DownloadHistoryOper().get_by_hash(_hash or torrent_info.hash)
                    # 执行处理
                    if self.main(torrent_info=torrent_info, downloadhis=downloadhis):
                        # 添加到已处理数据库
                        processed[torrent_info.hash] = d
                        # 本次处理成功计数
                        _processed_num += 1
                    else:
                        # 添加到失败数据库
                        _failures[torrent_info.hash] = d
        # 更新数据库
        if _failures:
            self.update_data("pending", _failures)
            logger.info(f"失败 {len(_failures)} 个")
        if processed:
            self.update_data("processed", processed)
            logger.info(f"成功 {_processed_num} 个, 合计 {len(processed)} 个种子已保存至历史")
        # 保存已处理数据库

    def main(self, downloader: str = None, downloadhis: DownloadHistory = None,
             hash: str =None, torrent_info: TorrentInfo = None, 
             meta: MetaBase = None, media_info: MediaInfo = None) -> bool:
        """
        处理单个种子
        :param downloader: 下载器名称
        :param hash: 种子哈希
        :param torrent_info: 种子信息
        :param meta: 文件元数据
        :param media_info: 媒体信息
        :return: 处理结果
        """
        success = True
        if downloader:
            # 设置下载器
            self.set_downloader(downloader)
        if self.downloader is None:
            success = False
            logger.warn(f"未连接下载器")
        if success and not torrent_info:
            if hash:
                torrent_info = self.downloader.torrents_info(hash)
                # 种子被手动删除或转移
                if not torrent_info:
                    success = False
                    logger.warn(f"下载器 {downloader} 不存在该种子: {hash}")
                    return True
                # 取第一个种子
                torrent_info = torrent_info[0]
        # 保存目录排除
        if success and self._exclude_dirs:
            for exclude_dir in self._exclude_dirs.split("\n"):
                if exclude_dir and exclude_dir in str(torrent_info.save_path):
                    success = False
                    logger.info(f"{torrent_info.name} 保存路径: {torrent_info.save_path} 命中排除目录：{exclude_dir}")
                    return True
        # 标签排除
        if success and self._exclude_tags and \
            (common_tags := {tag.strip() for tag in self._exclude_tags.split(",") if tag} & set(torrent_info.tags)):
            success = False
            logger.info(f"{torrent_info.tags} 命中排除标签：{common_tags}")
            return True
        if success and downloadhis:
            # 使用历史记录的识别信息
            # 因为mp默认RSS信息带有副标题，所以对舍弃副标题
            left_index = downloadhis.torrent_name.find('[')
            if left_index != -1:
                downloadhis.torrent_name = downloadhis.torrent_name[:left_index].strip()

            meta = MetaInfo(title=downloadhis.torrent_name, subtitle=downloadhis.torrent_description)
            media_info = self.chain.recognize_media(meta=meta, mtype=MediaType(downloadhis.type),
                                                    tmdbid=downloadhis.tmdbid, doubanid=downloadhis.doubanid)
        if success and not meta:
            logger.warn(f"未找到与之关联的下载种子 hash: {torrent_info.hash} 种子名称：{torrent_info.name} 元数据识别可能不准确")
            meta = MetaInfo(torrent_info.name)
            if not meta:
                logger.error(f"元数据获取失败，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                success = False
        if success and not media_info:
            media_info = self.chain.recognize_media(meta=meta)
            if not media_info:
                logger.error(f"识别媒体信息失败，hash: {torrent_info.hash} 种子名称：{torrent_info.name}")
                success = False
        if success:
            if self.format_torrent(torrent_info=torrent_info, meta=meta, media_info=media_info):
                logger.info(f"种子 hash: {torrent_info.hash}  名称：{torrent_info.name} 处理完成")
                return True
        # 处理失败
        return False

    def set_downloader(self, downloader: str):
        """
        获取下载器
        """
        if service := self.downloader_helper.get_service(name=downloader):
            is_qbittorrent = self.downloader_helper.is_downloader("qbittorrent", service.config)
            if is_qbittorrent:
                self.downloader: Downloader = QbittorrentDownloader(qbc=service.instance)
            else:
                self.downloader: None
                logger.info("只支持QB下载器")
        else:
            # 暂时设为None, 跳过
            self.downloader = None

    def update_data(self, key: str, value: dict = None):
        """
        更新插件数据
        """
        if not value:
            return
        plugin_data: dict = self.get_data(key=key)
        if plugin_data:
            plugin_data.update(value)
            self.save_data(key=key, value=plugin_data)
        else:
            self.save_data(key=key, value=value)

    def format_torrent(self, torrent_info: TorrentInfo, meta: MetaBase, media_info: MediaInfo) -> bool:
        _torrent_hash = torrent_info.hash
        _torrent_name = torrent_info.name
        success = True
        
        # 重命名种子名称
        new_name = self.format_path(
                template_string=self._format_torrent_name,
                meta=meta,
                mediainfo=media_info)
        try:
            if str(new_name) != _torrent_name:
                self.downloader.torrents_rename(torrent_hash=_torrent_hash, new_torrent_name=str(new_name))
                logger.info(f"种子重命名成功 hash: {_torrent_hash} {_torrent_name} ==> {new_name}")
                self.update_data(_torrent_hash, _torrent_name);
                # 更改记录写入数据库
        except Exception as e:
            logger.error(f"种子重命名失败 hash: {_torrent_hash} {str(e)}")
            success = False
        return success

    def recoveryTorrent(self):
        """
        恢复下载器中的种子名称
        """
        # 从下载器获取种子信息
        for d in self._downloader:
            self.set_downloader(d)
            if self.downloader is None:
                logger.warn(f"下载器: {d} 不存在或未启用")
                continue
            for torrent_info in self.downloader.torrents_info():
                if torrent_info:
                    torrent_hash = torrent_info.hash
                    torrent_name = torrent_info.name
                    torrent_oldName = self.get_data(torrent_hash)
                    if torrent_oldName != None:
                        self.downloader.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=str(torrent_oldName))
                        logger.info(f"种子恢复成功 hash: {torrent_hash} {torrent_oldName} ==> {torrent_name}")
                        self.del_data(torrent_hash)
