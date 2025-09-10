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
    plugin_version = "1.0.9"
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
    _bot_task = None
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
            if self._start_telegram_local_server():
                logger.debug("Telegram本地服务启动成功，启动Bot")
                self._start_bot()
            else:
                logger.error("Telegram本地服务启动失败，不启动Bot")
        else:
            logger.debug(f"插件未启用或Bot Token未设置，停止Bot - 启用: {self._enabled}, Token设置: {bool(self._bot_token)}")
            self._stop_bot()
            self._enabled = False

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

            # 使用 asyncio.create_task 运行bot
            logger.debug("启动Bot任务")
            try:
                # 尝试获取当前运行的事件循环
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # 如果没有正在运行的事件循环，则创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            self._bot_task = loop.create_task(self._run_bot())
            logger.debug(f"Bot任务已启动: {self._bot_task is not None}")

            logger.info("Music Saver Bot 启动成功")
        except Exception as e:
            self._enabled = False
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

            if self._bot_task and not self._bot_task.done():
                self._bot_task.cancel()
                self._bot_task = None

            logger.info("Music Saver Bot 已停止")
        except Exception as e:
            logger.error(f"停止Music Saver Bot失败: {str(e)}", exc_info=True)

    async def _run_bot(self):
        """
        运行bot的异步任务
        """
        try:
            logger.debug("开始运行Telegram Bot")
            logger.debug(f"Bot应用状态: {self._bot_app is not None}")
            
            # 在事件循环中运行bot
            await self._bot_app.run_polling()
        except asyncio.CancelledError:
            logger.info("Music Saver Bot 任务已被取消", exc_info=True)
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
                
                # 如果在Docker环境中运行，尝试使用PUID/PGID/UMASK环境变量设置权限
                puid = os.environ.get('PUID')
                pgid = os.environ.get('PGID')
                umask = os.environ.get('UMASK')
                
                if puid and pgid:
                    try:
                        uid = int(puid)
                        gid = int(pgid)
                        os.chown(str(save_dir), uid, gid)
                        logger.debug(f"设置目录 {save_dir} 的所有者为 UID:{uid}, GID:{gid}")
                    except Exception as e:
                        logger.warning(f"设置目录所有者失败: {str(e)}")
                
                if umask:
                    try:
                        # 应用umask设置
                        current_umask = os.umask(int(umask, 8))
                        os.umask(current_umask)  # 恢复原来的umask
                        # 重新设置目录权限
                        os.chmod(str(save_dir), 0o777 & ~int(umask, 8))
                        logger.debug(f"应用umask {umask} 到目录 {save_dir}")
                    except Exception as e:
                        logger.warning(f"应用umask设置失败: {str(e)}")

            # 构造完整文件路径
            full_path = save_dir / file_name
            logger.debug(f"完整文件路径: {full_path}")

            # 获取文件信息
            logger.debug("获取文件信息")
            try:
                file_obj = await context.bot.get_file(file_id)
                logger.debug(f"文件信息获取成功: {file_obj}")
                logger.debug(f"文件大小: {file_obj.file_size} bytes")
                # 异步下载文件（小文件）
                logger.debug("开始下载文件到磁盘")
                await file_obj.download_to_drive(full_path)
                logger.debug("文件下载完成")
                logger.info(f"文件下载完成: {full_path}")
                
                # 如果在Docker环境中运行，尝试使用PUID/PGID/UMASK环境变量设置权限
                puid = os.environ.get('PUID')
                pgid = os.environ.get('PGID')
                umask = os.environ.get('UMASK')
                
                if puid and pgid:
                    try:
                        uid = int(puid)
                        gid = int(pgid)
                        os.chown(str(full_path), uid, gid)
                        logger.debug(f"设置文件 {full_path} 的所有者为 UID:{uid}, GID:{gid}")
                    except Exception as e:
                        logger.warning(f"设置文件所有者失败: {str(e)}")
                
                if umask:
                    try:
                        # 应用umask设置到文件
                        os.chmod(str(full_path), 0o666 & ~int(umask, 8))
                        logger.debug(f"应用umask {umask} 到文件 {full_path}")
                    except Exception as e:
                        logger.warning(f"应用umask设置到文件失败: {str(e)}")
                
                return str(full_path)
            except Exception as file_info_error:
                logger.warning(f"通过Telegram Bot API获取文件信息失败: {str(file_info_error)}", exc_info=True)
                # 如果获取文件信息失败，假设是大文件，尝试直接构造URL下载
                file_url = f"http://127.0.0.1:{self._telegram_port}/file/bot{self._bot_token}/{file_id}"
                logger.debug(f"构造文件URL: {file_url}")
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
            logger.error(f"停止Telegram本地服务失败: {str(e)}", exc_info=True)
            self._enabled = False

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
                logger.warn(f"调用Telegram Bot logout接口失败: {str(e)}", exc_info=True)

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
                            # 应用umask设置
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
                        stderr=subprocess.PIPE
                    )
                    logger.debug(f"Telegram进程PID: {self._telegram_process.pid}")
                    self._telegram_process.wait()
                except Exception as e:
                    logger.error(f"Telegram本地服务运行异常: {str(e)}", exc_info=True)

            # 在新线程中运行
            self._telegram_process_thread = threading.Thread(target=run_telegram_server, daemon=True)
            self._telegram_process_thread.start()
            
            # 给一些时间让进程启动
            import time
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