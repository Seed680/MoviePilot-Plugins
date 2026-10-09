"""修复 V2 通知按用户/管理员隔离时的目标路由。"""
import copy
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.chain import ChainBase
from app.core.config import settings
from app.core.meta import MetaBase
from app.core.event import EventManager
from app.db.user_oper import UserOper
from app.helper.message import MessageTemplateHelper
from app.helper.service import ServiceConfigHelper
from app.log import logger
from app.modules.wechat import WechatModule
from app.plugins import _PluginBase
from app.schemas import Notification
from app.schemas.types import EventType


class NotificationTargetFix(_PluginBase):
    """修复 user,admin 通知中管理员目标被 userid 覆盖的问题。"""

    plugin_name = "通知目标修复"
    plugin_desc = "修复他人订阅影片时管理员无法收到通知的问题。"
    plugin_icon = "https://raw.githubusercontent.com/Seed680/MoviePilot-Plugins/main/icons/customplugin.png"
    plugin_version = "1.0.0"
    plugin_author = "Seed680"
    author_url = "https://github.com/Seed680"
    plugin_config_prefix = "notificationtargetfix_"
    plugin_order = 1
    auth_level = 1

    _enabled = False
    _patched = False
    _original_post = None
    _original_async_post = None
    _original_wechat_post = None

    def init_plugin(self, config: dict = None):
        """根据配置安装或卸载通知目标补丁。"""
        self._enabled = bool((config or {}).get("enabled", False))
        if self._enabled:
            self._install_patch()
        else:
            self._remove_patch()

    def _install_patch(self):
        if self._patched:
            return
        self._original_post = ChainBase.post_message
        self._original_async_post = ChainBase.async_post_message
        self._original_wechat_post = WechatModule.post_message
        ChainBase.post_message = _patched_post_message
        ChainBase.async_post_message = _patched_async_post_message
        WechatModule.post_message = _patched_wechat_post_message
        self._patched = True
        logger.info("通知目标修复插件已安装")

    def _remove_patch(self):
        if not self._patched:
            return
        if ChainBase.post_message is _patched_post_message:
            ChainBase.post_message = self._original_post
        if ChainBase.async_post_message is _patched_async_post_message:
            ChainBase.async_post_message = self._original_async_post
        if WechatModule.post_message is _patched_wechat_post_message:
            WechatModule.post_message = self._original_wechat_post
        self._patched = False
        logger.info("通知目标修复插件已卸载")

    def stop_service(self):
        """卸载补丁，避免插件停止后继续修改宿主行为。"""
        self._remove_patch()
        self._enabled = False

    def get_state(self) -> bool:
        return self._enabled

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [{
            "component": "VForm",
            "content": [{
                "component": "VSwitch",
                "props": {
                    "model": "enabled",
                    "label": "启用通知目标修复",
                    "hint": "启用后，user,admin 通知会分别发送到用户和管理员。",
                    "persistent-hint": True,
                },
            }],
        }], {"enabled": False}

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def get_page(self):
        return None

    @staticmethod
    def get_command():
        return []


def _render_message(self, message, meta, mediainfo, torrentinfo, transferinfo, kwargs):
    kwargs.setdefault("current_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = MessageTemplateHelper.render(
        message=message, meta=meta, mediainfo=mediainfo,
        torrentinfo=torrentinfo, transferinfo=transferinfo, **kwargs,
    )
    if not message:
        logger.warning("消息为空，跳过发送")
        return None
    if message.save_history:
        self.messageoper.add(**message.model_dump())
    return self._normalize_notification_for_dispatch(message)


async def _async_render_message(self, message, meta, mediainfo, torrentinfo, transferinfo, kwargs):
    kwargs.setdefault("current_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = MessageTemplateHelper.render(
        message=message, meta=meta, mediainfo=mediainfo,
        torrentinfo=torrentinfo, transferinfo=transferinfo, **kwargs,
    )
    if not message:
        logger.warning("消息为空，跳过发送")
        return None
    if message.save_history:
        await self.messageoper.async_add(**message.model_dump())
    return self._normalize_notification_for_dispatch(message)


def _notice_message_data(self, message):
    if hasattr(self, "_build_notice_message_data"):
        return self._build_notice_message_data(message)
    return {**message.model_dump(exclude={"save_history"}), "type": message.mtype}


def _patched_post_message(self, message=None, meta: Optional[MetaBase] = None,
                          mediainfo=None, torrentinfo=None, transferinfo=None, **kwargs) -> None:
    message = _render_message(self, message, meta, mediainfo, torrentinfo, transferinfo, kwargs)
    if not message:
        return
    if message.userid and message.mtype and message.username != settings.SUPERUSER:
        notify_action = ServiceConfigHelper.get_notification_switch(message.mtype)
        if notify_action and "admin" in notify_action.split(","):
            self.eventmanager.send_event(
                etype=EventType.NoticeMessage,
                data=_notice_message_data(self, message),
            )
            user_kwargs = dict(kwargs)
            user_kwargs.setdefault("immediately", True)
            self.messagequeue.send_message(
                "post_message", message=message, **user_kwargs,
            )
            admin_message = copy.deepcopy(message)
            admin_message.targets = UserOper().get_settings(settings.SUPERUSER)
            if admin_message.targets is not None:
                self.eventmanager.send_event(
                    etype=EventType.NoticeMessage,
                    data=_notice_message_data(self, admin_message),
                )
                admin_kwargs = dict(kwargs)
                admin_kwargs.setdefault("immediately", True)
                self.messagequeue.send_message(
                    "post_message", message=admin_message, **admin_kwargs,
                )
            return
    if not message.userid and message.mtype:
        notify_action = ServiceConfigHelper.get_notification_switch(message.mtype)
        if notify_action:
            admin_sent = False
            send_original = False
            useroper = UserOper()
            for action in notify_action.split(","):
                send_message = copy.deepcopy(message)
                if action == "admin" and not admin_sent:
                    send_message.targets = useroper.get_settings(settings.SUPERUSER)
                    admin_sent = True
                elif action == "user" and send_message.username:
                    send_message.targets = useroper.get_settings(send_message.username)
                    if send_message.targets is None:
                        if not admin_sent:
                            send_message.targets = useroper.get_settings(settings.SUPERUSER)
                            admin_sent = True
                        else:
                            continue
                    elif send_message.username == settings.SUPERUSER:
                        admin_sent = True
                else:
                    if not admin_sent:
                        send_original = True
                    break
                self.eventmanager.send_event(
                    etype=EventType.NoticeMessage,
                    data=_notice_message_data(self, send_message),
                )
                self.messagequeue.send_message("post_message", message=send_message, **kwargs)
            if not send_original:
                return
    self.eventmanager.send_event(
        etype=EventType.NoticeMessage,
        data=_notice_message_data(self, message),
    )
    self.messagequeue.send_message(
        "post_message", message=message,
        immediately=True if message.userid else False, **kwargs,
    )


async def _patched_async_post_message(self, message=None, meta: Optional[MetaBase] = None,
                                      mediainfo=None, torrentinfo=None, transferinfo=None,
                                      **kwargs) -> None:
    message = await _async_render_message(self, message, meta, mediainfo, torrentinfo, transferinfo, kwargs)
    if not message:
        return
    if message.userid and message.mtype and message.username != settings.SUPERUSER:
        notify_action = ServiceConfigHelper.get_notification_switch(message.mtype)
        if notify_action and "admin" in notify_action.split(","):
            await self.eventmanager.async_send_event(
                etype=EventType.NoticeMessage,
                data=_notice_message_data(self, message),
            )
            user_kwargs = dict(kwargs)
            user_kwargs.setdefault("immediately", True)
            await self.messagequeue.async_send_message(
                "post_message", message=message, **user_kwargs,
            )
            admin_message = copy.deepcopy(message)
            admin_message.targets = UserOper().get_settings(settings.SUPERUSER)
            if admin_message.targets is not None:
                await self.eventmanager.async_send_event(
                    etype=EventType.NoticeMessage,
                    data=_notice_message_data(self, admin_message),
                )
                admin_kwargs = dict(kwargs)
                admin_kwargs.setdefault("immediately", True)
                await self.messagequeue.async_send_message(
                    "post_message", message=admin_message, **admin_kwargs,
                )
            return
    if not message.userid and message.mtype:
        notify_action = ServiceConfigHelper.get_notification_switch(message.mtype)
        if notify_action:
            admin_sent = False
            send_original = False
            useroper = UserOper()
            for action in notify_action.split(","):
                send_message = copy.deepcopy(message)
                if action == "admin" and not admin_sent:
                    send_message.targets = useroper.get_settings(settings.SUPERUSER)
                    admin_sent = True
                elif action == "user" and send_message.username:
                    send_message.targets = useroper.get_settings(send_message.username)
                    if send_message.targets is None:
                        if not admin_sent:
                            send_message.targets = useroper.get_settings(settings.SUPERUSER)
                            admin_sent = True
                        else:
                            continue
                    elif send_message.username == settings.SUPERUSER:
                        admin_sent = True
                else:
                    if not admin_sent:
                        send_original = True
                    break
                await self.eventmanager.async_send_event(
                    etype=EventType.NoticeMessage,
                    data=_notice_message_data(self, send_message),
                )
                await self.messagequeue.async_send_message("post_message", message=send_message, **kwargs)
            if not send_original:
                return
    await self.eventmanager.async_send_event(
        etype=EventType.NoticeMessage,
        data=_notice_message_data(self, message),
    )
    await self.messagequeue.async_send_message(
        "post_message", message=message,
        immediately=True if message.userid else False, **kwargs,
    )


def _patched_wechat_post_message(self, message: Notification, **kwargs) -> None:
    for conf in self.get_configs().values():
        if not self.check_message(message, conf.name):
            continue
        # targets 优先于 userid；否则管理员分支会沿用订阅用户的 userid。
        userid = message.userid
        if message.targets is not None:
            userid = message.targets.get("wechat_userid")
            if not userid:
                logger.warning("用户没有指定微信用户ID，消息无法发送")
                continue
        client = self.get_instance(conf.name)
        if client:
            if message.voice_path and hasattr(client, "send_voice"):
                sent = client.send_voice(voice_path=message.voice_path, userid=userid)
                if not sent:
                    client.send_msg(title=message.title, text=message.text,
                                    image=message.image, userid=userid, link=message.link)
            else:
                client.send_msg(title=message.title, text=message.text,
                                image=message.image, userid=userid, link=message.link)
