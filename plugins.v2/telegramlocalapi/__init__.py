import threading
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import requests
from app.log import logger
from app.plugins import _PluginBase
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor


class TelegramLocalApi(_PluginBase):
    # 插件名称
    plugin_name = "Telegram本地API服务"
    # 插件描述
    plugin_desc = "提供Telegram本地API服务支持"
    # 插件图标
    plugin_icon = "telegram.png"
    # 插件版本
    plugin_version = "1.0.12"
    # 插件作者
    plugin_author = "Seed"
    # 作者主页
    author_url = "https://github.com/Seed"
    # 插件配置项ID前缀
    plugin_config_prefix = "telegramlocalapi_"
    # 加载顺序
    plugin_order = 19
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _telegram_port = 8081
    _telegram_api_id = None
    _telegram_api_hash = None
    _telegram_data_path = None
    _telegram_proxy_type = None
    _telegram_proxy_server = None
    _telegram_proxy_port = None
    _telegram_proxy_username = None
    _telegram_proxy_password = None
    _telegram_enable_log = False
    _telegram_clean_cache_cron = None
    _telegram_bot_api_version = "1.0"
    _telegram_process = None
    _telegram_process_thread = None
    _scheduler = None

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        logger.debug(f"初始化TelegramLocalApi插件，配置: {config}")

        if config:

            self._enabled = config.get("enable", False)
            self._telegram_port = config.get("telegram_port", "")
            self._telegram_api_id = config.get("telegram_api_id", "")
            self._telegram_api_hash = config.get("telegram_api_hash", "")
            self._telegram_data_path = config.get("telegram_data_path", "")
            self._telegram_proxy_type = config.get("telegram_proxy_type", "")
            self._telegram_proxy_server = config.get("telegram_proxy_server", "")
            self._telegram_proxy_port = config.get("telegram_proxy_port", "")
            self._telegram_proxy_username = config.get("telegram_proxy_username", "")
            self._telegram_proxy_password = config.get("telegram_proxy_password", "")
            self._telegram_enable_log = config.get("telegram_enable_log", False)
            self._telegram_clean_cache_cron = config.get("telegram_clean_cache_cron", "")

            logger.debug(f"配置加载完成 - 启用: {self._enabled}, API ID设置: {bool(self._telegram_api_id)}, 数据目录: {self._telegram_data_path}")

        self.stop_service()
        # 如果插件启用且有必要的配置信息，则启动服务
        if self._enabled and self._telegram_api_id and self._telegram_api_hash and self._telegram_data_path:
            if self._start_telegram_local_server():
                logger.info("Telegram本地服务启动成功")
            else:
                logger.error("Telegram本地服务启动失败")
                self._enabled = False
        else:
            logger.debug(f"插件未启用或配置不完整 - 启用: {self._enabled}")
            self._stop_telegram_local_server()
            if config:
                self._enabled = False
        self.update_config(config=config)
        

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_command(self):
        pass
    
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
        if self._telegram_clean_cache_cron:
            try:
                from apscheduler.triggers.cron import CronTrigger
                return [{
                    "id": "TelegramLocalApiCacheCleanup",
                    "name": "Telegram本地API缓存清理服务",
                    "trigger": CronTrigger.from_crontab(self._telegram_clean_cache_cron),
                    "func": self._clean_cache,
                    "kwargs": {}
                }]
            except Exception as e:
                logger.error(f"注册定时清理缓存任务失败: {str(e)}")
        return []

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
                                            'model': 'telegram_port',
                                            'label': 'Telegram本地服务端口',
                                            'placeholder': '请输入Telegram本地服务端口',
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
                                            'model': 'telegram_api_id',
                                            'label': 'API ID',
                                            'placeholder': '请输入Telegram API ID',
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'telegram_api_hash',
                                            'label': 'API Hash',
                                            'placeholder': '请输入Telegram API Hash',
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'telegram_data_path',
                                            'label': 'Telegram数据目录',
                                            'placeholder': '请输入Telegram数据目录',
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
                                            'model': 'telegram_proxy_type',
                                            'label': '代理类型',
                                            'items': [
                                                {'title': 'HTTP', 'value': 'http'},
                                                {'title': 'SOCKS5', 'value': 'socks5'}
                                            ]
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
                                            'model': 'telegram_proxy_server',
                                            'label': '代理地址',
                                            'placeholder': '请输入代理服务器IP地址',
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
                                            'model': 'telegram_proxy_port',
                                            'label': '代理端口',
                                            'placeholder': '请输入代理端口',
                                            'type': 'number'
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
                                            'model': 'telegram_proxy_username',
                                            'label': '代理用户名',
                                            'placeholder': '请输入代理用户名（可选）',
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'telegram_proxy_password',
                                            'label': '代理密码',
                                            'placeholder': '请输入代理密码（可选）'
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'telegram_enable_log',
                                            'label': '启用服务日志',
                                            'hint': '开启后将在数据目录下生成log.txt日志文件'
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'telegram_clean_cache_cron',
                                            'label': '定时清理缓存',
                                            'placeholder': '请输入cron表达式，例如：0 2 * * *（每天凌晨2点清理）',
                                            'hint': '使用cron表达式设置定时清理缓存的时间，留空则不启用定时清理'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enable": self._enabled,
            "telegram_port": self._telegram_port,
            "telegram_api_id": self._telegram_api_id,
            "telegram_api_hash": self._telegram_api_hash,
            "telegram_data_path": self._telegram_data_path,
            "telegram_proxy_type": self._telegram_proxy_type,
            "telegram_proxy_server": self._telegram_proxy_server,
            "telegram_proxy_port": self._telegram_proxy_port,
            "telegram_proxy_username": self._telegram_proxy_username,
            "telegram_proxy_password": self._telegram_proxy_password,
            "telegram_enable_log": self._telegram_enable_log,
            "telegram_clean_cache_cron": self._telegram_clean_cache_cron
        }

    def get_page(self) -> List[dict]:
        """
        拼装插件配置页面
        """
        pass

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        return self._enabled

    def stop_service(self):
        """
        退出插件
        """
        self._stop_telegram_local_server()
        
        # 停止调度器
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"停止调度器失败: {str(e)}")

    def _stop_telegram_local_server(self):
        """
        停止Telegram本地服务
        """
        try:
            if self._telegram_process:
                # 终止进程
                self._telegram_process.terminate()
                self._telegram_process.wait(timeout=5)
                self._telegram_process = None
                logger.info("Telegram本地服务已停止")

            if self._telegram_process_thread and self._telegram_process_thread.is_alive():
                self._telegram_process_thread = None

        except Exception as e:
            logger.error(f"停止Telegram本地服务失败: {str(e)}", exc_info=True)

    def _start_telegram_local_server(self):
        """
        启动Telegram本地服务
        """
        try:
            import platform
            import subprocess
            import os
            import stat
            import shutil
            import urllib.request
            from pathlib import Path

            # 判断运行系统是否为Linux
            if platform.system() != "Linux":
                logger.warn(f"当前系统为{platform.system()}，仅支持在Linux系统上运行Telegram本地服务")
                return False

            # 获取系统架构
            architecture = platform.machine()
            logger.info(f"当前系统架构: {architecture}")

            # 判断是否是支持的架构
            if architecture not in ["x86_64", "aarch64", "arm64"]:
                logger.warn(f"不支持的系统架构: {architecture}，仅支持x86_64和arm64架构")
                return False

            # 处理arm64架构标记不一致的问题
            if architecture == "aarch64":
                architecture = "arm64"

            # 确定执行文件路径
            plugin_dir = Path(__file__).parent
            telegram_executable = plugin_dir / f"telegram-bot-api-linux-{architecture}"

            # 检查执行文件是否存在
            if not telegram_executable.exists():
                logger.info(f"Telegram本地服务执行文件不存在，正在下载: {telegram_executable}")
                # 构造下载URL
                download_url = f"https://github.com/Seed680/telegram-bot-api/releases/download/v{self._telegram_bot_api_version}/telegram-bot-api-linux-{architecture}"

                # 下载文件
                try:
                    urllib.request.urlretrieve(download_url, telegram_executable)
                    logger.info("Telegram本地服务执行文件下载完成")
                except Exception as e:
                    logger.error(f"下载Telegram本地服务执行文件失败: {str(e)}", exc_info=True)
                    return False

            # 赋予执行权限
            os.chmod(telegram_executable, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)
            logger.info("Telegram本地服务执行文件权限设置完成")
            
            # 检查并创建数据目录
            telegram_data_path = Path(self._telegram_data_path)
            logger.debug(f"检查Telegram数据目录: {telegram_data_path}")
            logger.debug(f"数据目录是否存在: {telegram_data_path.exists()}")
            
            if not telegram_data_path.exists():
                try:
                    logger.debug(f"尝试创建Telegram数据目录: {telegram_data_path}")
                    telegram_data_path.mkdir(parents=True, exist_ok=True)
                    
                    # 如果在Docker环境中运行，尝试使用PUID/PGID/UMASK环境变量设置权限
                    puid = os.environ.get('PUID')
                    pgid = os.environ.get('PGID')
                    umask = os.environ.get('UMASK')
                    
                    if puid and pgid:
                        try:
                            uid = int(puid)
                            gid = int(pgid)
                            os.chown(str(telegram_data_path), uid, gid)
                            # 递归设置目录及子文件的权限
                            for root, dirs, files in os.walk(telegram_data_path):
                                for d in dirs:
                                    os.chown(os.path.join(root, d), uid, gid)
                                for f in files:
                                    os.chown(os.path.join(root, f), uid, gid)
                            logger.debug(f"设置目录 {telegram_data_path} 及子文件的所有者为 UID:{uid}, GID:{gid}")
                        except Exception as e:
                            logger.warning(f"设置目录所有者失败: {str(e)}")
                    
                    if umask:
                        try:
                            mask = int(umask, 8)
                            # 设置目录权限
                            os.chmod(str(telegram_data_path), 0o777 & ~mask)
                            # 递归设置目录及子文件的权限
                            for root, dirs, files in os.walk(telegram_data_path):
                                for d in dirs:
                                    os.chmod(os.path.join(root, d), 0o777 & ~mask)
                                for f in files:
                                    os.chmod(os.path.join(root, f), 0o666 & ~mask)
                            logger.debug(f"应用umask {umask} 到目录 {telegram_data_path} 及子文件")
                        except Exception as e:
                            logger.warning(f"应用umask设置失败: {str(e)}")
                    
                    if telegram_data_path.exists():
                        logger.info(f"Telegram数据目录创建成功: {telegram_data_path}")
                    else:
                        logger.error(f"Telegram数据目录创建失败: {telegram_data_path}")
                        return False
                except Exception as e:
                    logger.error(f"创建Telegram数据目录时发生异常: {str(e)}", exc_info=True)
                    return False
            else:
                logger.info(f"Telegram数据目录已存在: {telegram_data_path}")
                # 即使目录已存在，也尝试应用权限设置
                puid = os.environ.get('PUID')
                pgid = os.environ.get('PGID')
                umask = os.environ.get('UMASK')
                
                if puid and pgid:
                    try:
                        uid = int(puid)
                        gid = int(pgid)
                        os.chown(str(telegram_data_path), uid, gid)
                        # 递归设置目录及子文件的权限
                        for root, dirs, files in os.walk(telegram_data_path):
                            for d in dirs:
                                os.chown(os.path.join(root, d), uid, gid)
                            for f in files:
                                os.chown(os.path.join(root, f), uid, gid)
                        logger.debug(f"设置现有目录 {telegram_data_path} 及子文件的所有者为 UID:{uid}, GID:{gid}")
                    except Exception as e:
                        logger.warning(f"设置现有目录所有者失败: {str(e)}")
                
                if umask:
                    try:
                        mask = int(umask, 8)
                        # 设置目录权限
                        os.chmod(str(telegram_data_path), 0o777 & ~mask)
                        # 递归设置目录及子文件的权限
                        for root, dirs, files in os.walk(telegram_data_path):
                            for d in dirs:
                                os.chmod(os.path.join(root, d), 0o777 & ~mask)
                            for f in files:
                                os.chmod(os.path.join(root, f), 0o666 & ~mask)
                        logger.debug(f"应用umask {umask} 到现有目录 {telegram_data_path} 及子文件")
                    except Exception as e:
                        logger.warning(f"应用umask设置到现有目录失败: {str(e)}")
            
            # 构造启动命令
            cmd = [
                str(telegram_executable),
                "--api-id=" + str(self._telegram_api_id),
                "--api-hash=" + str(self._telegram_api_hash),
                "--local",
                "--http-ip-address=127.0.0.1",
                "--http-port=" + str(self._telegram_port),
                "--dir=" + str(self._telegram_data_path)
            ]
            
            # 如果配置了代理，则添加代理相关参数
            if self._telegram_proxy_type and self._telegram_proxy_server and self._telegram_proxy_port:
                logger.info(f"使用{self._telegram_proxy_type.upper()}代理: {self._telegram_proxy_server}:{self._telegram_proxy_port}")
                cmd.append("--proxy-server=" + str(self._telegram_proxy_server))
                cmd.append("--proxy-port=" + str(self._telegram_proxy_port))
                cmd.append("--tdlib-proxy-type=" + str(self._telegram_proxy_type))
                
                # 如果配置了代理用户名和密码，则添加认证信息
                if self._telegram_proxy_username:
                    cmd.append("--proxy-login=" + str(self._telegram_proxy_username))
                    
                if self._telegram_proxy_password:
                    cmd.append("--proxy-password=" + str(self._telegram_proxy_password))
            
            # 如果启用了服务日志，则添加日志相关参数
            if self._telegram_enable_log:
                import os
                log_file_path = os.path.join(str(self._telegram_data_path), "log.txt")
                cmd.append(f"--log={log_file_path}")
                cmd.append("--verbosity=4")
                logger.info(f"已启用服务日志，日志文件路径: {log_file_path}")

            logger.info(f"启动Telegram本地服务: {' '.join(cmd)}")

            # 启动进程
            def run_telegram_server():
                try:
                    # 设置子进程的工作目录和环境变量
                    env = os.environ.copy()
                    env['HOME'] = str(plugin_dir)
                    
                    self._telegram_process = subprocess.Popen(
                        cmd,
                        cwd=str(plugin_dir),  # 设置工作目录
                        env=env,  # 传递环境变量
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        bufsize=1,  # 行缓冲
                        universal_newlines=True  # 文本模式
                    )
                    logger.debug(f"Telegram进程PID: {self._telegram_process.pid}")
                    
                    # 实时读取并打印日志
                    def log_output(pipe, log_level):
                        for line in iter(pipe.readline, ''):
                            if line:
                                logger.info(f"[telegram-bot-api {log_level}] {line.rstrip()}")
                        pipe.close()
                    
                    # 启动线程读取stdout和stderr
                    stdout_thread = threading.Thread(target=log_output, args=(self._telegram_process.stdout, "stdout"), daemon=True)
                    stderr_thread = threading.Thread(target=log_output, args=(self._telegram_process.stderr, "stderr"), daemon=True)
                    stdout_thread.start()
                    stderr_thread.start()
                    
                    self._telegram_process.wait()
                    
                    # 等待日志线程结束
                    stdout_thread.join(timeout=1)
                    stderr_thread.join(timeout=1)
                except Exception as e:
                    logger.error(f"Telegram本地服务运行异常: {str(e)}", exc_info=True)

            # 在新线程中运行
            self._telegram_process_thread = threading.Thread(target=run_telegram_server, daemon=True)
            self._telegram_process_thread.start()
            
            # 给一些时间让进程启动
            time.sleep(3)  # 增加等待时间到3秒
            
            # 检查进程是否成功启动
            # 方法1: 检查线程是否仍在运行
            # 方法2: 检查_telegram_process是否已创建且仍在运行
            logger.debug(f"检查Telegram服务启动状态:")
            logger.debug(f"  线程是否存活: {self._telegram_process_thread.is_alive()}")
            logger.debug(f"  进程对象是否存在: {self._telegram_process is not None}")
            
            if self._telegram_process is not None:
                poll_result = self._telegram_process.poll()
                logger.debug(f"  进程poll结果: {poll_result}")
                logger.debug(f"  进程是否仍在运行: {poll_result is None}")
                
                # 如果poll()返回None，表示进程仍在运行
                if poll_result is None:
                    logger.info("Telegram本地服务启动成功")
                    return True
                else:
                    # 进程已结束，尝试获取退出码和错误信息
                    logger.error(f"Telegram本地服务启动失败，进程已退出，退出码: {poll_result}")
                    try:
                        stdout, stderr = self._telegram_process.communicate(timeout=2)
                        if stdout:
                            logger.debug(f"Telegram本地服务标准输出: {stdout.decode('utf-8')}")
                        if stderr:
                            logger.error(f"Telegram本地服务错误输出: {stderr.decode('utf-8')}")
                    except Exception as e:
                        logger.warning(f"获取Telegram本地服务输出信息时发生异常: {str(e)}")
                    return False
            elif self._telegram_process_thread.is_alive():
                # 如果进程对象还未创建但线程仍在运行，给更多时间
                logger.debug("进程对象尚未创建但线程仍在运行，可能是启动较慢")
                logger.info("Telegram本地服务启动成功")
                return True
            else:
                logger.error("Telegram本地服务启动失败")
                return False

        except Exception as e:
            logger.error(f"启动Telegram本地服务失败: {str(e)}", exc_info=True)
            return False


    def _shutdown_scheduler(self):
        """
        关闭调度器
        """
        try:
            if self._scheduler:
                self._scheduler.shutdown()
                logger.info("调度器已关闭")
                self._scheduler = None
        except Exception as e:
            logger.error(f"关闭调度器失败: {str(e)}")


    def _clean_cache(self):
        """
        清理缓存文件
        """
        try:
            import os
            import shutil
            from pathlib import Path
            
            if not self._telegram_data_path:
                logger.warn("未设置Telegram数据目录，无法清理缓存")
                return
                
            telegram_data_path = Path(self._telegram_data_path)
            if not telegram_data_path.exists():
                logger.warn(f"Telegram数据目录不存在: {telegram_data_path}")
                return
                
            logger.info(f"开始清理Telegram缓存目录: {telegram_data_path}")
            cleaned_count = 0
            
            # 遍历数据目录下的所有bot token目录
            for bot_dir in telegram_data_path.iterdir():
                if bot_dir.is_dir():
                    # 遍历bot目录下的所有缓存文件夹
                    for cache_dir in bot_dir.iterdir():
                        if cache_dir.is_dir() and cache_dir.name not in ["log.txt"]:  # 排除日志文件
                            try:
                                # 清理缓存目录中的所有文件
                                for cache_file in cache_dir.iterdir():
                                    if cache_file.is_file():
                                        cache_file.unlink()
                                        cleaned_count += 1
                                logger.debug(f"已清理缓存文件夹: {cache_dir}")
                            except Exception as e:
                                logger.error(f"清理缓存文件夹 {cache_dir} 失败: {str(e)}")
            
            logger.info(f"Telegram缓存清理完成，共清理 {cleaned_count} 个缓存文件")
        except Exception as e:
            logger.error(f"清理Telegram缓存时发生错误: {str(e)}")
