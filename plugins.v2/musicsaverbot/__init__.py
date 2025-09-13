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
    plugin_version = "1.0.41"
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
            
        # 强制停止任何可能正在运行的机器人实例
        if self._bot_running or self._bot_app:
            logger.warning("检测到可能正在运行的机器人实例，尝试强制停止")
            self._stop_bot()
            
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
            self._bot_app.add_handler(MessageHandler(
                filters.AUDIO | 
                filters.VOICE | 
                filters.Document.Category("audio") |
                filters.Document.MimeType("text/plain") |
                filters.Document.FileExtension("lrc") |
                filters.Document.FileExtension("txt"), 
                self._handle_audio_message))
            
            # 在单独的线程中运行机器人
            logger.debug("启动机器人线程")
            self._bot_thread = threading.Thread(target=self._run_bot, daemon=True)
            self._bot_thread.start()
            
            # 等待一小段时间确保线程启动
            import time
            time.sleep(0.1)
            
            self._bot_running = True
            logger.info("音乐保存机器人已启动")
        except Exception as e:
            logger.error(f"启动机器人失败: {str(e)}", exc_info=True)
            self._bot_running = False
            self._bot_app = None

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
                
                async def stop_app():
                    try:
                        if hasattr(self._bot_app, 'stop'):
                            await self._bot_app.stop()
                        else:
                            logger.debug("机器人应用没有stop方法或尚未初始化")
                    except Exception as stop_err:
                        logger.debug(f"停止机器人应用时出现错误（可能是应用未运行）: {str(stop_err)}")
                    
                    try:
                        if hasattr(self._bot_app, 'shutdown'):
                            await self._bot_app.shutdown()
                        else:
                            logger.debug("机器人应用没有shutdown方法或尚未初始化")
                    except Exception as shutdown_err:
                        logger.debug(f"关闭机器人应用时出现错误（可能是应用未运行）: {str(shutdown_err)}")
                
                # 检查是否有正在运行的事件循环
                try:
                    loop = asyncio.get_running_loop()
                    # 如果在事件循环中，创建任务而不是运行直到完成
                    task = loop.create_task(stop_app())
                    # 等待任务完成，最多等待5秒
                    async def wait_for_task():
                        try:
                            await asyncio.wait_for(task, timeout=5.0)
                        except asyncio.TimeoutError:
                            logger.warning("等待机器人停止超时")
                    
                    loop.create_task(wait_for_task())
                except RuntimeError:
                    # 没有正在运行的事件循环，可以安全使用run_until_complete
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(asyncio.wait_for(stop_app(), timeout=5.0))
                    except asyncio.TimeoutError:
                        logger.warning("等待机器人停止超时")
                    finally:
                        loop.close()
            
            # 无论停止操作是否成功，都标记机器人未运行以避免冲突
            self._bot_running = False
            self._bot_app = None  # 清理应用引用
            logger.info("音乐保存机器人已停止")
        except Exception as e:
            # 即使出现异常，也要确保状态被重置以避免冲突
            self._bot_running = False
            self._bot_app = None
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
            # 确保在任何情况下都正确清理状态
            try:
                if 'loop' in locals():
                    loop.close()
            except Exception as e:
                logger.warning(f"关闭事件循环时出错: {str(e)}")
                
            self._bot_running = False
            self._bot_app = None
            logger.info("机器人轮询线程已结束")

    async def _handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                    await update.message.reply_text("您没有权限使用此功能。")
                    return
                    
            message = update.message
            logger.debug(f"消息类型 - 音频: {bool(message.audio)}, 语音: {bool(message.voice)}, 文档: {bool(message.document)}")
            
            # 获取文件信息
            file_id = None
            file_name = None
            thumbnail = None
            
            if message.audio:
                file_id = message.audio.file_id
                thumbnail = message.audio.thumbnail
                # 根据title和performer生成文件名
                file_name = self._generate_filename(
                    title=message.audio.title,
                    performer=message.audio.performer,
                    original_filename=message.audio.file_name
                )
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
                await message.reply_text("无法获取文件信息，请稍后重试。")
                return
                
            # 确保保存目录存在
            save_path = self._save_path or "./music_files"
            logger.debug(f"目标保存路径: {save_path}")
            
            # 检查是否为歌词文件（.lrc 或 .txt）
            is_lyric_file = False
            if message.document and file_name:
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext in ['.lrc', '.txt']:
                    is_lyric_file = True
                    logger.debug(f"检测到歌词文件: {file_name}")
            
            # 如果是歌词文件，特殊处理
            if is_lyric_file:
                # 解析歌词文件名获取歌曲名和歌手名
                song_name, artist_name = self._parse_lyric_filename(file_name)
                
                if song_name and artist_name:
                    # 查找对应的歌曲目录
                    song_directory = self._find_song_directory(save_path, song_name, artist_name)
                    
                    if song_directory:
                        # 找到对应目录，保存歌词文件
                        lyric_save_path = os.path.join(song_directory, file_name)
                        logger.debug(f"歌词文件将保存至: {lyric_save_path}")
                    else:
                        # 未找到对应歌曲目录，保存到默认目录
                        logger.info(f"未找到歌曲 {song_name} by {artist_name} 的目录，将保存到默认目录")
                        await message.reply_text(f"未找到歌曲 {song_name} by {artist_name}，将保存到默认目录。")
                        self._ensure_directory(save_path)
                        lyric_save_path = os.path.join(save_path, file_name)
                else:
                    # 无法解析文件名，保存到默认目录
                    logger.info(f"无法从文件名 {file_name} 解析出歌曲名和歌手名，将保存到默认目录")
                    self._ensure_directory(save_path)
                    lyric_save_path = os.path.join(save_path, file_name)
            
            # 如果是音频文件，构建新的目录结构
            album_name = None
            performer = None
            title = None
            
            if message.audio:
                # 提取专辑名
                album_name = self._extract_album_name(message.caption)
                if not album_name:
                    album_name = "Unknown Album"
                
                # 获取表演者和标题
                performer = message.audio.performer or "Unknown Artist"
                title = message.audio.title
                
                # 构建新的保存路径: save_path/performer/专辑名/
                album_path = os.path.join(save_path, performer, album_name)
                self._ensure_directory(album_path)
                
                # 更新文件保存路径
                save_file_path = os.path.join(album_path, file_name)
                logger.debug(f"音频文件将保存至: {save_file_path}")
                
                # 检查并保存封面图片
                cover_path = self._save_cover_image(thumbnail, album_path)
            elif is_lyric_file and 'lyric_save_path' in locals():
                # 使用之前确定的歌词保存路径
                save_file_path = lyric_save_path
            else:
                # 非音频文件保持原有逻辑
                self._ensure_directory(save_path)
                save_file_path = os.path.join(save_path, file_name)
                logger.debug(f"文件将保存至: {save_file_path}")
                cover_path = None
            
            # 下载文件
            logger.debug(f"开始下载文件，文件ID: {file_id}")
            
            # 直接使用await调用异步方法，避免手动处理事件循环
            # 添加重试机制，最多重试3次
            max_retries = 3
            download_success = False
            for attempt in range(max_retries):
                try:
                    file = await context.bot.get_file(file_id)
                    await file.download_to_drive(save_file_path)
                    download_success = True
                    break  # 成功下载则跳出循环
                except Exception as e:
                    if attempt < max_retries - 1:  # 如果不是最后一次尝试
                        logger.debug(f"第{attempt + 1}次下载文件失败，准备重试: {str(e)}")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)  # 指数退避策略
                    else:
                        # 最后一次尝试仍然失败
                        logger.error(f"文件下载失败: {str(e)}")
                        await message.reply_text(f"文件下载失败，请稍后重试。\n错误信息: {str(e)}")
                        raise e
            
            # 如果是音频文件且需要保存封面图片
            if message.audio and cover_path and thumbnail:
                try:
                    logger.debug(f"开始下载封面图片，文件ID: {thumbnail.file_id}")
                    # 添加重试机制，最多重试3次
                    cover_success = False
                    for attempt in range(max_retries):
                        try:
                            thumb_file = await context.bot.get_file(thumbnail.file_id)
                            await thumb_file.download_to_drive(cover_path)
                            logger.info(f"封面图片已保存: {cover_path}")
                            cover_success = True
                            break  # 成功下载则跳出循环
                        except Exception as e:
                            if attempt < max_retries - 1:  # 如果不是最后一次尝试
                                logger.debug(f"第{attempt + 1}次下载封面图片失败，准备重试: {str(e)}")
                                import asyncio
                                await asyncio.sleep(2 ** attempt)  # 指数退避策略
                            else:
                                # 最后一次尝试仍然失败
                                logger.error(f"下载封面图片失败: {str(e)}")
                                await message.reply_text(f"封面图片下载失败。\n错误信息: {str(e)}")
                                break
                    
                    # 如果封面下载成功，记录日志
                    if cover_success:
                        logger.info(f"封面图片已保存: {cover_path}")
                except Exception as e:
                    logger.error(f"保存封面图片时发生错误: {str(e)}")
                    await message.reply_text(f"保存封面图片时发生错误。\n错误信息: {str(e)}")
            
            # 如果文件下载成功，发送成功消息
            if download_success:
                logger.info(f"文件已保存: {save_file_path}")
                # 构建回复消息，复用之前提取的信息
                if message.audio:
                    # 构建详细的音频文件回复消息
                    reply_msg = f"🎵 文件已保存:\n"
                    if performer:
                        reply_msg += f"歌手: {performer}\n"
                    if album_name and album_name != "Unknown Album":
                        reply_msg += f"专辑: {album_name}\n"
                    if title:
                        reply_msg += f"歌曲: {title}\n"
                    reply_msg += f"文件名: {file_name}"
                    await message.reply_text(reply_msg)
                else:
                    # 非音频文件使用简单的回复消息
                    await message.reply_text(f"文件已保存: {file_name}")
        except TelegramError as e:
            logger.error(f"处理消息时发生Telegram错误: {str(e)}", exc_info=True)
            try:
                await message.reply_text(f"处理文件时发生Telegram错误，请稍后重试。\n错误信息: {str(e)}")
            except:
                pass
        except Exception as e:
            logger.error(f"处理消息时发生错误: {str(e)}", exc_info=True)
            try:
                await message.reply_text(f"处理文件时发生错误，请稍后重试。\n错误信息: {str(e)}")
            except:
                pass

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

    def _generate_filename(self, title=None, performer=None, original_filename=None):
        """
        根据title和performer生成文件名，保持原有文件后缀
        
        Args:
            title: 音频标题
            performer: 表演者
            original_filename: 原始文件名
            
        Returns:
            生成的文件名
        """
        try:
            # 如果title和performer都存在，则使用"title - performer"格式
            if title and performer:
                # 获取原始文件的后缀
                file_extension = ""
                if original_filename:
                    file_extension = os.path.splitext(original_filename)[1]
                
                # 生成新文件名并保持后缀
                new_filename = f"{title}-{performer}{file_extension}"
                logger.debug(f"使用title和performer生成文件名: {new_filename}")
                return new_filename
            
            # 如果只有title，则使用title作为文件名
            if title:
                # 获取原始文件的后缀
                file_extension = ""
                if original_filename:
                    file_extension = os.path.splitext(original_filename)[1]
                
                # 生成新文件名并保持后缀
                new_filename = f"{title}{file_extension}"
                logger.debug(f"使用title生成文件名: {new_filename}")
                return new_filename
                
            # 如果无法根据title和performer生成文件名，则使用原始文件名
            if original_filename:
                logger.debug(f"使用原始文件名: {original_filename}")
                return original_filename
            
            # 如果都没有，则生成默认文件名
            default_filename = f"audio_{int(time.time())}.mp3"
            logger.debug(f"使用默认文件名: {default_filename}")
            return default_filename
        except Exception as e:
            logger.error(f"生成文件名时发生错误: {str(e)}")
            # 出现异常时返回原始文件名或默认文件名
            if original_filename:
                return original_filename
            return f"audio_{int(time.time())}.mp3"

    def _extract_album_name(self, caption):
        """
        从消息caption中提取专辑名
        
        Args:
            caption: 消息的caption文本
            
        Returns:
            提取到的专辑名，如果未找到则返回None
        """
        if not caption:
            return None
            
        try:
            # 查找"专辑："和"\n"之间的内容
            import re
            album_pattern = r'专辑：(.*?)\n'
            match = re.search(album_pattern, caption)
            if match:
                album_name = match.group(1).strip()
                logger.debug(f"提取到专辑名: {album_name}")
                return album_name
            else:
                logger.debug("未在caption中找到专辑名")
                return None
        except Exception as e:
            logger.error(f"提取专辑名时发生错误: {str(e)}")
            return None

    def _save_cover_image(self, thumbnail, album_path):
        """
        保存封面图片到专辑目录
        
        Args:
            thumbnail: 音频文件的缩略图对象
            album_path: 专辑目录路径
        """
        if not thumbnail:
            logger.debug("没有缩略图可保存")
            return
            
        try:
            # 检查专辑目录下是否已存在cover.jpg
            cover_path = os.path.join(album_path, "cover.jpg")
            if os.path.exists(cover_path):
                logger.debug(f"封面图片已存在: {cover_path}")
                return
                
            # 确保专辑目录存在
            self._ensure_directory(album_path)
            
            # 注意：这里只是记录需要保存封面图片，实际保存操作需要在_handle_audio_message中进行
            # 因为需要context.bot来获取和下载文件
            logger.debug(f"需要保存封面图片到: {cover_path}")
            return cover_path
        except Exception as e:
            logger.error(f"保存封面图片时发生错误: {str(e)}")

    def _parse_lyric_filename(self, filename):
        """
        解析歌词文件名，提取歌曲名和歌手名
        
        Args:
            filename: 歌词文件名
            
        Returns:
            tuple: (歌曲名, 歌手名) 或 (None, None) 如果解析失败
        """
        try:
            # 移除文件扩展名
            name_without_ext = os.path.splitext(filename)[0]
            
            # 按照"-"分割文件名
            parts = name_without_ext.split('-')
            if len(parts) >= 2:
                # 第一部分是歌曲名，第二部分是歌手名
                song_name = parts[0].strip()
                artist_name = parts[1].strip()
                
                if song_name and artist_name:
                    logger.debug(f"从文件名解析出歌曲名: {song_name}, 歌手名: {artist_name}")
                    return song_name, artist_name
                    
            logger.debug(f"无法从文件名 {filename} 解析出歌曲名和歌手名")
            return None, None
        except Exception as e:
            logger.error(f"解析歌词文件名时发生错误: {str(e)}")
            return None, None

    def _find_song_directory(self, save_path, song_name, artist_name):
        """
        查找歌曲对应的目录
        
        Args:
            save_path: 音乐保存根目录
            song_name: 歌曲名
            artist_name: 歌手名
            
        Returns:
            str: 歌曲所在目录路径，如果未找到则返回None
        """
        try:
            # 检查歌手目录是否存在
            artist_path = os.path.join(save_path, artist_name)
            if not os.path.exists(artist_path):
                logger.debug(f"歌手目录不存在: {artist_path}")
                return None
                
            # 遍历歌手目录下的所有专辑目录
            for album_dir in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album_dir)
                if os.path.isdir(album_path):
                    # 检查专辑目录中是否存在对应的歌曲文件
                    try:
                        for file in os.listdir(album_path):
                            # 检查文件名是否包含歌曲名（忽略扩展名）
                            file_name_without_ext = os.path.splitext(file)[0]
                            if song_name in file_name_without_ext or file_name_without_ext.startswith(song_name):
                                logger.debug(f"找到匹配的歌曲目录: {album_path}")
                                return album_path
                    except Exception as e:
                        logger.warning(f"检查专辑目录 {album_path} 时发生错误: {str(e)}")
                        continue
                        
            logger.debug(f"未找到歌曲 {song_name} by {artist_name} 的目录")
            return None
        except Exception as e:
            logger.error(f"查找歌曲目录时发生错误: {str(e)}")
            return None
