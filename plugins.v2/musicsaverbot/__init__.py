import os
import threading
import asyncio
from typing import List, Tuple, Dict, Any, Optional

from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import SystemConfigKey
import requests
# 检查是否安装了 python-telegram-bot
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
    from telegram.error import TelegramError
    from telegram.ext import ExtBot
    TELEGRAM_MODULE_AVAILABLE = True
except ImportError:
    TELEGRAM_MODULE_AVAILABLE = False
    logger.warning("未安装 python-telegram-bot，音乐保存机器人插件无法正常工作")


class MusicSaverBot(_PluginBase):
    # 插件名称
    plugin_name = "音乐保存机器人"
    # 插件描述
    plugin_desc = "接收Telegram机器人收到的音乐文件并保存到本地"
    # 插件图标
    plugin_icon = "music.png"
    # 插件版本
    plugin_version = "1.0.30"
    # 插件作者
    plugin_author = "Seed"
    # 作者主页
    author_url = "https://github.com/Seed"
    # 插件配置项ID前缀
    plugin_config_prefix = "musicsaverbot_"
    # 加载顺序
    plugin_order = 17
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enable = False
    _enable_custom_api = False
    _custom_api_url = None
    _bot_token = None
    _save_path = None
    _whitelist = None
    
    _bot_app = None
    _bot_thread = None
    _bot_running = False

    def init_plugin(self, config: dict = None):
        logger.debug(f"初始化音乐保存机器人插件，配置参数: {config}")
        # 读取配置
        if config:
            self._enable = config.get("enable", False)
            self._enable_custom_api = config.get("enable_custom_api", False)
            self._custom_api_url = config.get("custom_api_url") or None
            self._bot_token = config.get("bot_token")
            self._save_path = config.get("save_path")
            self._whitelist = config.get("whitelist")
            
        logger.debug(f"插件配置详情 - 启用: {self._enable}, 自定义API: {self._enable_custom_api}, Token设置: {bool(self._bot_token)}")
        self.stop_service()
        # 如果启用了插件并且配置了bot token，则启动机器人
        if self._enable and self._bot_token and TELEGRAM_MODULE_AVAILABLE:
            logger.info("插件已启用且配置完整，准备启动机器人")
            self._start_bot()
        elif self._bot_running:
            logger.info("插件未启用或配置不完整，停止机器人")
            self._stop_bot()

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        logger.debug("获取插件表单配置")
        return None, {
            "enable": self._enable,
            "enable_custom_api": self._enable_custom_api,
            "custom_api_url": self._custom_api_url,
            "bot_token": self._bot_token,
            "save_path": self._save_path,
            "whitelist": self._whitelist
        }

    def get_state(self) -> bool:
        logger.debug(f"获取插件状态: {self._enable}")
        return self._enable

    def get_api(self) -> List[Dict[str, Any]]:
        """
        注册插件API接口
        """
        logger.debug("注册插件API接口")
        return [
            {
                "path": "/config",
                "endpoint": self._get_config,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取当前配置"
            },
            {
                "path": "/status",
                "endpoint": self._get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取机器人运行状态"
            },
            {
                "path": "/restart",
                "endpoint": self._restart_bot,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "重启机器人服务"
            }
        ]

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """
        退出插件
        """
        logger.info("停止音乐保存机器人插件服务")
        self._stop_bot()

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify
        :return: 2、组件路径，默认 dist/assets
        """
        return "vue", "dist/assets"

    def _get_config(self) -> Dict[str, Any]:
        """
        API接口：获取当前配置
        """
        logger.debug("API调用：获取当前配置")
        return {
            "enable": self._enable,
            "enable_custom_api": self._enable_custom_api,
            "custom_api_url": self._custom_api_url,
            "bot_token": self._bot_token,
            "save_path": self._save_path,
            "whitelist": self._whitelist
        }

    def _get_status(self) -> Dict[str, Any]:
        """
        API接口：获取机器人运行状态
        """
        logger.debug("API调用：获取机器人运行状态")
        return {
            "running": self._bot_running,
            "enable": self._enable,
            "bot_token_set": bool(self._bot_token)
        }

    def _restart_bot(self) -> Dict[str, Any]:
        """
        API接口：重启机器人服务
        """
        logger.debug("API调用：重启机器人服务")
        try:
            if self._bot_running:
                self._stop_bot()
            
            if self._enable and self._bot_token:
                self._start_bot()
                return {"success": True, "message": "机器人服务已重启", "running": self._bot_running}
            else:
                return {"success": False, "message": "插件未启用或缺少必要配置", "running": self._bot_running}
        except Exception as e:
            logger.error(f"重启机器人服务失败: {str(e)}", exc_info=True)
            return {"success": False, "message": f"重启失败: {str(e)}", "running": self._bot_running}

    def _start_bot(self):
        """
        启动Telegram机器人服务
        """
        logger.debug("开始启动Telegram机器人服务")
        if not TELEGRAM_MODULE_AVAILABLE:
            logger.error("未安装 python-telegram-bot 库，无法启动机器人")
            return
            
        if self._bot_running:
            logger.debug("机器人已在运行中，无需重复启动")
            return
            
        try:
            logger.info("正在创建机器人应用")
            # 创建机器人应用
            if self._enable_custom_api and self._custom_api_url:
                logger.debug(f"使用自定义API地址: {self._custom_api_url}")
                # 根据Telegram官方文档，使用自定义API地址前需要先logout官方服务
                logger.debug("尝试注销机器人官方服务")
                try:
                    
                    # 使用GET请求手动完成logout
                    base_url = "https://api.telegram.org"
                    logout_url = f"{base_url}/bot{self._bot_token}/logOut"
                    response = requests.get(logout_url, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("ok"):
                            logger.debug("机器人已从官方服务注销")
                        else:
                            logger.warning(f"注销机器人失败: {result.get('description')}")
                    else:
                        logger.warning(f"注销机器人请求失败，状态码: {response.status_code}")
                except Exception as logout_err:
                    logger.warning(f"注销机器人时出现错误: {str(logout_err)}，将继续使用自定义API")
                
                # 使用自定义API地址
                logger.debug(f"使用自定义API地址: {self._custom_api_url}")
                self._bot_app = ApplicationBuilder().token(self._bot_token).base_url(f"{self._custom_api_url}/bot").base_file_url(f"{self._custom_api_url}/file/bot").build()
            else:
                logger.debug("使用默认API地址")
                #if self._custom_api_url:
                    # 当使用自定义API时，不需要执行log_out操作
                    # 因为log_out仅适用于官方API
                    # 如果需要切换到自定义API，只需直接构建应用即可
                self._bot_app = ApplicationBuilder().token(self._bot_token).build()
            
            # 添加消息处理器
            logger.debug("注册消息处理器")
            self._bot_app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.Category("audio"), self._handle_audio_message))
            
            # 在单独的线程中运行机器人
            logger.debug("启动机器人线程")
            self._bot_thread = threading.Thread(target=self._run_bot, daemon=True)
            self._bot_thread.start()
            
            self._bot_running = True
            logger.info("音乐保存机器人已启动")
        except Exception as e:
            logger.error(f"启动机器人失败: {str(e)}", exc_info=True)
            self._bot_running = False

    def _stop_bot(self):
        """
        停止Telegram机器人服务
        """
        logger.debug("开始停止Telegram机器人服务")
        if not self._bot_running:
            logger.debug("机器人未在运行中")
            return
            
        try:
            # 异步关闭机器人应用
            if self._bot_app:
                import asyncio
                loop = asyncio.get_event_loop()
                
                async def stop_app():
                    await self._bot_app.stop()
                    await self._bot_app.shutdown()
                
                loop.run_until_complete(stop_app())
            
            self._bot_running = False
            logger.info("音乐保存机器人已停止")
        except Exception as e:
            logger.error(f"停止机器人失败: {str(e)}", exc_info=True)

    def _run_bot(self):
        """
        在独立线程中运行机器人
        """
        logger.info("机器人轮询线程已启动")
        try:
            # 在新线程中设置事件循环并运行机器人
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            logger.debug("开始运行机器人轮询")
            # 直接运行轮询，禁用信号处理避免线程问题
            loop.run_until_complete(self._bot_app.run_polling(stop_signals=[]))
        except asyncio.TimeoutError as e:
            logger.error(f"机器人连接超时，请检查网络连接、Bot Token和API地址配置")
            logger.error(f"详细错误信息: {str(e)}")
        except Exception as e:
            logger.error(f"机器人运行出错: {str(e)}", exc_info=True)
        finally:
            self._bot_running = False
            logger.info("机器人轮询线程已结束")

    def _handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        处理音频消息
        """
        logger.debug(f"收到音频消息，更新ID: {update.update_id}")
        try:
            # 检查用户是否在白名单中
            user_id = update.effective_user.id
            user_name = update.effective_user.username or update.effective_user.full_name
            logger.debug(f"消息来源用户 - ID: {user_id}, 用户名: {user_name}")
            
            if self._whitelist:
                whitelist_ids = [uid.strip() for uid in self._whitelist.split('\n') if uid.strip()]
                logger.debug(f"白名单用户列表: {whitelist_ids}")
                if str(user_id) not in whitelist_ids:
                    logger.info(f"用户 {user_id} ({user_name}) 不在白名单中，拒绝处理")
                    return
                    
            message = update.message
            logger.debug(f"消息类型 - 音频: {bool(message.audio)}, 语音: {bool(message.voice)}, 文档: {bool(message.document)}")
            
            # 获取文件信息
            file_id = None
            file_name = None
            
            if message.audio:
                file_id = message.audio.file_id
                file_name = message.audio.file_name or f"audio_{file_id}.mp3"
                logger.debug(f"音频文件 - ID: {file_id}, 文件名: {file_name}, 大小: {message.audio.file_size}")
            elif message.voice:
                file_id = message.voice.file_id
                file_name = f"voice_{file_id}.ogg"
                logger.debug(f"语音文件 - ID: {file_id}, 大小: {message.voice.file_size}")
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
                logger.debug(f"文档文件 - ID: {file_id}, 文件名: {file_name}, 大小: {message.document.file_size}")
                
            if not file_id:
                logger.warning("无法获取文件ID")
                return
                
            # 确保保存目录存在
            save_path = self._save_path or "./music_files"
            logger.debug(f"目标保存路径: {save_path}")
            self._ensure_directory(save_path)
            
            # 下载文件
            logger.debug(f"开始下载文件，文件ID: {file_id}")
            
            # 异步获取文件信息并下载
            import asyncio
            loop = asyncio.get_event_loop()
            
            async def download_file():
                file = await context.bot.get_file(file_id)
                save_file_path = os.path.join(save_path, file_name)
                logger.debug(f"文件将保存至: {save_file_path}")
                await file.download_to_drive(save_file_path)
                return save_file_path
            
            # 在现有事件循环中执行异步操作
            save_file_path = loop.run_until_complete(download_file())
            
            logger.info(f"音乐文件已保存: {save_file_path}")
            
            # 发送确认消息
            async def send_reply():
                await message.reply_text(f"音乐文件已保存: {file_name}")
            
            loop.run_until_complete(send_reply())
        except TelegramError as e:
            logger.error(f"处理音频消息时发生Telegram错误: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"处理音频消息时发生错误: {str(e)}", exc_info=True)

    def _ensure_directory(self, path):
        """
        确保目录存在，并根据环境变量设置权限
        """
        logger.debug(f"检查目录是否存在: {path}")
        if not os.path.exists(path):
            logger.debug(f"目录不存在，创建目录: {path}")
            os.makedirs(path)
            
        # 如果存在PUID, PGID, UMASK环境变量，则设置目录权限
        puid = os.environ.get("PUID")
        pgid = os.environ.get("PGID")
        umask = os.environ.get("UMASK")
        
        logger.debug(f"环境变量 - PUID: {puid}, PGID: {pgid}, UMASK: {umask}")
        
        if puid and pgid:
            try:
                uid = int(puid)
                gid = int(pgid)
                logger.debug(f"设置目录用户/组权限: {path} - UID: {uid}, GID: {gid}")
                os.chown(path, uid, gid)
            except Exception as e:
                logger.warn(f"设置目录 {path} 的用户/组权限失败: {str(e)}")
                
        if umask:
            try:
                mask = int(umask, 8)  # 以八进制解析umask
                logger.debug(f"设置目录umask权限: {path} - mask: {mask:o}")
                os.chmod(path, 0o777 & ~mask)
            except Exception as e:
                logger.warn(f"设置目录 {path} 的umask权限失败: {str(e)}")