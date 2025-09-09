import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from telegram import Update, Document, Audio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
from app.log import logger
from app.plugins import _PluginBase


class MusicSaverBot(_PluginBase):
    # 插件名称
    plugin_name = "TG Music Saver Bot"
    # 插件描述
    plugin_desc = "接收Telegram发送的音乐文件并保存到本地"
    # 插件图标
    plugin_icon = "music.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "Your Name"
    # 作者主页
    author_url = "https://github.com/yourname"
    # 插件配置项ID前缀
    plugin_config_prefix = "musicsaverbot_"
    # 加载顺序
    plugin_order = 20
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _bot_token = None
    _save_path = None
    _whitelist_ids = None
    _telegram_port = 8081
    _telegram_api_id = None
    _telegram_api_hash = None
    _telegram_data_path = None
    _telegram_bot_api_version = "1.0"
    _bot_app = None
    _bot_thread = None
    _executor = None
    _telegram_process = None
    _telegram_process_thread = None


    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        logger.debug(f"初始化MusicSaverBot插件，配置: {config}")
        
        if config:
            self._enabled = config.get("enable", False)
            self._bot_token = config.get("bot_token", "")
            self._save_path = config.get("save_path", "")
            self._whitelist_ids = config.get("whitelist_ids", "")
            self._telegram_port = config.get("telegram_port", "")
            self._telegram_api_id = config.get("telegram_api_id", "")
            self._telegram_api_hash = config.get("telegram_api_hash", "")
            self._telegram_data_path = config.get("telegram_data_path", "")
            
            logger.debug(f"配置加载完成 - 启用: {self._enabled}, Token设置: {bool(self._bot_token)}, 保存路径: {self._save_path}, 白名单: {self._whitelist_ids}")

        # 如果插件启用且有bot token，则启动bot
        if self._enabled and self._bot_token and self._telegram_api_id and self._telegram_api_hash and self._telegram_data_path:
            # 启动Telegram本地服务
            self._start_telegram_local_server()
            logger.debug("插件已启用且Bot Token已设置，启动Bot")
            self._start_bot()

        else:
            logger.debug(f"插件未启用或Bot Token未设置，停止Bot - 启用: {self._enabled}, Token设置: {bool(self._bot_token)}")
            self._stop_bot()

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify
        :return: 2、组件路径，默认 dist/assets
        """
        return "vue", "dist/assets"
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
    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return None, {
            "enable": self._enabled,
            "bot_token": self._bot_token,
            "save_path": self._save_path,
            "whitelist_ids": self._whitelist_ids,
            "telegram_port": self._telegram_port,
            "telegram_api_id": self._telegram_api_id,
            "telegram_api_hash": self._telegram_api_hash,
            "telegram_data_path": self._telegram_data_path
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
        self._stop_bot()
        self._stop_telegram_local_server()

    def _start_bot(self):
        """
        启动Telegram Bot
        """
        try:
            logger.debug("开始启动Telegram Bot")
            logger.debug(f"插件启用状态: {self._enabled}")
            logger.debug(f"Bot Token是否设置: {bool(self._bot_token)}")
            base_url = f"http://127.0.0.1:{self._telegram_port}/bot{self._bot_token}"
            base_file = f"http://127.0.0.1:{self._telegram_port}/file/bot{self._bot_token}"
            # 停止现有bot
            self._stop_bot()

            # 创建bot应用
            logger.debug("创建Bot应用")
            self._bot_app = (ApplicationBuilder().token(self._bot_token)
                             .base_url(base_url)
                             .base_file_url(base_file)
                             .local_mode(True)
                             .build())
            logger.debug(f"Bot应用创建成功: {self._bot_app is not None}")

            # 添加消息处理器
            logger.debug("添加消息处理器")
            self._bot_app.add_handler(MessageHandler(
                filters.AUDIO | filters.Document.Category("audio"), 
                self._handle_audio_message
            ))
            logger.debug("消息处理器添加完成")

            # 创建线程池执行器用于异步下载
            self._executor = ThreadPoolExecutor(max_workers=3)

            # 在新线程中运行bot
            logger.debug("启动Bot线程")
            self._bot_thread = threading.Thread(target=self._run_bot, daemon=True)
            self._bot_thread.start()
            logger.debug(f"Bot线程已启动: {self._bot_thread is not None}")

            logger.info("Music Saver Bot 启动成功")
        except Exception as e:
            logger.error(f"启动Music Saver Bot失败: {str(e)}", exc_info=True)
            self._stop_bot()

    def _stop_bot(self):
        """
        停止Telegram Bot
        """
        try:
            if self._bot_app:
                # 停止bot应用
                # 注意：由于ApplicationBuilder创建的应用没有直接的停止方法，我们通过其他方式管理
                self._bot_app = None

            if self._executor:
                self._executor.shutdown(wait=False)
                self._executor = None

            if self._bot_thread and self._bot_thread.is_alive():
                self._bot_thread = None

            logger.info("Music Saver Bot 已停止")
        except Exception as e:
            logger.error(f"停止Music Saver Bot失败: {str(e)}")

    def _run_bot(self):
        """
        在独立线程中运行bot
        """
        try:
            logger.debug("开始运行Telegram Bot")
            logger.debug(f"Bot应用状态: {self._bot_app is not None}")
            # 使用 asyncio 运行 bot
            asyncio.run(self._bot_app.run_polling())
        except Exception as e:
            logger.error(f"运行Music Saver Bot时出错: {str(e)}", exc_info=True)

    async def _handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        处理接收到的音频消息
        """
        try:
            logger.debug(f"收到更新消息: {update}")
            
            if not update.message:
                logger.debug("更新消息中没有message字段")
                return
                
            message = update.message
            logger.debug(f"收到消息: {message}")
            
            chat_id = message.chat_id
            logger.debug(f"消息来自聊天ID: {chat_id}")
            
            if not message.from_user:
                logger.debug("消息中没有发送者信息")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="无法识别发送者信息。"
                )
                return
                
            user_id = message.from_user.id
            logger.debug(f"消息来自用户ID: {user_id}")
            logger.debug(f"消息发送者详细信息: {message.from_user}")

            # 检查白名单
            logger.debug(f"当前白名单设置: {self._whitelist_ids}")
            if self._whitelist_ids:
                # 解析白名单ID列表
                whitelist_ids = [wid.strip() for wid in self._whitelist_ids.split(",") if wid.strip()]
                logger.debug(f"解析后的白名单ID列表: {whitelist_ids}")
                # 如果设置了白名单，则检查用户ID是否在白名单中
                if whitelist_ids and str(user_id) not in whitelist_ids:
                    # 用户不在白名单中，拒绝下载
                    logger.info(f"用户 {user_id} 不在白名单中，拒绝下载文件")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="您没有权限使用此功能。"
                    )
                    return

            # 检查消息类型
            logger.debug(f"消息包含音频: {message.audio is not None}")
            logger.debug(f"消息包含文档: {message.document is not None}")
            logger.debug(f"消息包含媒体组: {message.media_group_id is not None}")
            
            if message.audio:
                logger.debug(f"音频文件信息: {message.audio}")
            if message.document:
                logger.debug(f"文档文件信息: {message.document}")
            if message.media_group_id:
                logger.debug(f"媒体组ID: {message.media_group_id}")

            # 发送接收确认消息
            await context.bot.send_message(
                chat_id=chat_id,
                text="正在处理您发送的音乐文件..."
            )

            # 处理单个或多个音乐文件
            if message.audio:
                # 单个音频文件
                logger.debug("处理Audio类型的音频文件")
                await self._process_audio_file(context, chat_id, message.audio)
            elif message.document:
                # 文档形式的音频文件
                logger.debug("处理Document类型的音频文件")
                await self._process_document_file(context, chat_id, message.document)
            elif message.media_group_id:
                # 多个文件组
                logger.debug("处理媒体组文件")
                media_group = message.media_group_id
                # 这里需要处理媒体组，但简化处理，逐个处理
                if message.audio:
                    await self._process_audio_file(context, chat_id, message.audio)
                elif message.document and message.document.mime_type and "audio" in message.document.mime_type:
                    await self._process_document_file(context, chat_id, message.document)
            else:
                logger.debug("消息中没有识别到音频文件")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="未识别到音频文件。"
                )
                return

            # 发送完成消息
            await context.bot.send_message(
                chat_id=chat_id,
                text="音乐文件处理完成！"
            )

        except Exception as e:
            logger.error(f"处理音频消息时出错: {str(e)}", exc_info=True)
            if update.message:
                await update.message.reply_text("处理您的音乐文件时出现错误，请稍后重试。")

    async def _process_audio_file(self, context, chat_id, audio: Audio):
        """
        处理Audio类型的音频文件
        """
        try:
            logger.debug(f"开始处理Audio类型文件: {audio}")
            file_name = audio.file_name if audio.file_name else f"{audio.file_id}.mp3"
            file_size = audio.file_size

            logger.info(f"开始处理音频文件: {file_name} (大小: {file_size} bytes)")

            # 获取文件路径
            file_path = await self._download_file(context, audio.file_id, file_name)
            
            logger.debug(f"文件下载结果: {file_path}")

            if file_path:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"音频文件 {file_name} 已保存到: {file_path}"
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"音频文件 {file_name} 下载失败"
                )

        except Exception as e:
            logger.error(f"处理音频文件时出错: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="处理音频文件时出现错误"
            )

    async def _process_document_file(self, context, chat_id, document: Document):
        """
        处理Document类型的音频文件
        """
        try:
            logger.debug(f"开始处理Document类型文件: {document}")
            file_name = document.file_name if document.file_name else f"{document.file_id}.mp3"
            file_size = document.file_size
            
            # 检查是否为音频文件
            is_audio = document.mime_type and "audio" in document.mime_type
            logger.debug(f"文档MIME类型: {document.mime_type}, 是否为音频: {is_audio}")

            logger.info(f"开始处理文档类型音频文件: {file_name} (大小: {file_size} bytes)")

            # 获取文件路径
            file_path = await self._download_file(context, document.file_id, file_name)
            
            logger.debug(f"文件下载结果: {file_path}")

            if file_path:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"音频文件 {file_name} 已保存到: {file_path}"
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"音频文件 {file_name} 下载失败"
                )

        except Exception as e:
            logger.error(f"处理文档类型音频文件时出错: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="处理音频文件时出现错误"
            )

    async def _download_file(self, context, file_id, file_name):
        """
        异步下载文件
        """

        try:
            logger.debug(f"开始下载文件 - ID: {file_id}, 名称: {file_name}")
            
            # 确保保存目录存在
            save_dir = Path(self._save_path)
            logger.debug(f"保存目录: {save_dir}")
            
            if not save_dir.exists():
                logger.debug("保存目录不存在，正在创建")
                save_dir.mkdir(parents=True, exist_ok=True)

            # 构造完整文件路径
            full_path = save_dir / file_name
            logger.debug(f"完整文件路径: {full_path}")

            # 获取文件信息
            logger.debug("获取文件信息")
            try:
                file_obj = await context.bot.get_file(file_id)
                logger.debug(f"文件信息获取成功: {file_obj}")
                logger.debug(f"文件大小: {file_obj.file_size} bytes")
                
                # 检查文件大小是否超过Telegram Bot API限制(20MB)
                if file_obj.file_size and file_obj.file_size > 20 * 1024 * 1024:  # 20MB
                    logger.warning(f"文件 {file_name} 大小为 {file_obj.file_size} bytes，超过20MB限制，将使用替代方法下载")
                    
                    # 获取文件URL
                    file_url = file_obj.file_path
                    if not file_url.startswith('http'):
                        # 构造完整的文件URL
                        file_url = f"https://api.telegram.org/file/bot{self._bot_token}/{file_obj.file_path}"
                    
                    logger.debug(f"文件URL: {file_url}")
                else:
                    # 异步下载文件（小文件）
                    logger.debug("开始下载文件到磁盘")
                    await file_obj.download_to_drive(full_path)
                    logger.debug("文件下载完成")
                    logger.info(f"文件下载完成: {full_path}")
                    return str(full_path)
            except Exception as file_info_error:
                logger.warning(f"通过Telegram Bot API获取文件信息失败: {str(file_info_error)}")
                # 如果获取文件信息失败，假设是大文件，尝试直接构造URL下载
                file_url = f"https://api.telegram.org/file/bot{self._bot_token}/{file_id}"
                logger.debug(f"构造文件URL: {file_url}")

            # 如果上面的方法失败或者确定是大文件，使用requests直接下载
            response = requests.get(file_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 获取文件总大小
            total_size = int(response.headers.get('content-length', 0))
            logger.debug(f"文件总大小: {total_size} bytes")
            
            # 写入文件并显示进度
            downloaded_size = 0
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # 记录下载进度（每5MB记录一次）
                        if downloaded_size % (5 * 1024 * 1024) == 0:
                            progress_percent = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            logger.debug(f"已下载: {downloaded_size}/{total_size} bytes ({progress_percent:.2f}%)")
                    
            logger.info(f"大文件下载完成: {full_path} (总大小: {downloaded_size} bytes)")
            return str(full_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"使用requests下载文件时出错: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"下载文件时出错: {str(e)}", exc_info=True)
            return None

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件服务
        """
        pass

    def _get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        """
        return {
            "enabled": self._enabled,
            "bot_token": self._bot_token,
            "save_path": self._save_path,
            "whitelist_ids": self._whitelist_ids,
            "telegram_port": self._telegram_port,
            "telegram_api_id": self._telegram_api_id,
            "telegram_api_hash": self._telegram_api_hash,
            "telegram_data_path": self._telegram_data_path
        }

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
            logger.error(f"停止Telegram本地服务失败: {str(e)}")

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
            
            # 在启动前先调用Telegram Bot的logout方法，确保之前的会话已断开
            try:
                import requests
                logout_url = f"https://api.telegram.org/bot{self._bot_token}/logOut"
                requests.post(logout_url, timeout=5)
                logger.info("已调用Telegram Bot的logout方法，清理之前的会话")
            except Exception as e:
                logger.warn(f"调用Telegram Bot logout接口失败: {str(e)}")
            
            # 判断运行系统是否为Linux
            if platform.system() != "Linux":
                logger.warn(f"当前系统为{platform.system()}，仅支持在Linux系统上运行Telegram本地服务")
                return
            
            # 获取系统架构
            architecture = platform.machine()
            logger.info(f"当前系统架构: {architecture}")
            
            # 判断是否是支持的架构
            if architecture not in ["x86_64", "aarch64", "arm64"]:
                logger.warn(f"不支持的系统架构: {architecture}，仅支持x86_64和arm64架构")
                return
            
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
                    logger.error(f"下载Telegram本地服务执行文件失败: {str(e)}")
                    return
            
            # 赋予执行权限
            os.chmod(telegram_executable, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)
            logger.info("Telegram本地服务执行文件权限设置完成")
            
            # 构造启动命令
            cmd = [
                str(telegram_executable),
                "--api-id=" + str(self._telegram_api_id),
                "--api-hash=" + str(self._telegram_api_hash),
                "--local",
                "--http-ip=0.0.0.0",
                "--http-port=" + str(self._telegram_port),
                "--dir=" + str(self._telegram_data_path)
            ]
            
            logger.info(f"启动Telegram本地服务: {' '.join(cmd)}")
            
            # 启动进程
            def run_telegram_server():
                try:
                    self._telegram_process = subprocess.Popen(cmd)
                    self._telegram_process.wait()
                except Exception as e:
                    logger.error(f"Telegram本地服务运行异常: {str(e)}")
            
            # 在新线程中运行
            self._telegram_process_thread = threading.Thread(target=run_telegram_server, daemon=True)
            self._telegram_process_thread.start()
            logger.info("Telegram本地服务启动成功")
            
        except Exception as e:
            logger.error(f"启动Telegram本地服务失败: {str(e)}", exc_info=True)
