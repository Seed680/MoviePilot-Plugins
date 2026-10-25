"""
企业微信用户会话消息按通知发送范围分发的修复插件。

宿主对任何带有用户标识的消息都直接返回无路由结果，使「通知发送范围」
（NotificationSwitchs）对微信渠道内用户触发的消息完全失效。本插件在通知路由
状态机入口补回原会话回复，并按发送范围追加管理员或全体投递，不修改宿主源码；
宿主后续自行支持该行为时，插件会自动让位给宿主实现。

实现说明：宿主没有公开的通知路由扩展点，因此本插件在启用时才包装
`app.chain._messaging._notification_route_steps`，停用时立即还原；其它数据
一律通过稳定 SDK 读取（`app.sdk.services.ServiceConfigHelper`）。
"""
import copy
import importlib
from collections.abc import Generator, Mapping
from typing import Any

from app.schemas.types import NotificationChannel
from app.sdk.logging import logger
from app.sdk.plugin import _PluginBase
from app.sdk.services import ServiceConfigHelper

# 补丁标记挂在被替换的宿主函数上，插件重载后仍能找回原始实现
_PATCH_MARKER = "__wechat_notification_target_fix_original__"
# 宿主通知路由模块名
_MESSAGING_MODULE = "app.chain._messaging"
# 宿主通知路由状态机函数名
_ROUTE_STEPS_ATTR = "_notification_route_steps"


def _is_wechat_conversation(message: Any) -> bool:
    """
    判断消息是否为企业微信渠道内由用户直接发起的会话消息。

    :param message: 待判断的通知消息
    :return: 带用户标识且渠道为企业微信时返回 True
    """
    return bool(getattr(message, "userid", None)) and (
        getattr(message, "channel", None) == NotificationChannel.Wechat
    )


def _scope_tokens(scope: str | None) -> list[str]:
    """
    把通知发送范围拆成路由令牌，空白项按管理员处理。

    :param scope: 宿主读取到的发送范围配置
    :return: 去除空白后的路由令牌列表
    """
    return [token.strip() or "admin" for token in (scope or "admin").split(",")]


def _resolve_scope(message: Any) -> str | None:
    """
    读取消息场景对应的通知发送范围。

    读取失败时返回 None，调用方据此保持宿主原有的原样直发行为。

    :param message: 待投递的通知消息
    :return: 发送范围字符串，读取失败时返回 None
    """
    mtype = getattr(message, "mtype", None)
    if not mtype:
        return "admin"
    try:
        return ServiceConfigHelper.get_notification_switch(mtype) or "admin"
    except Exception as error:  # noqa: BLE001 - 宿主异常时不影响通知发送
        logger.error(f"企业微信通知范围修复：读取发送范围失败：{error}")
        return None


def _detach_conversation(message: Any) -> Any:
    """
    复制消息并清除用户会话标识，使副本按收件人自己的渠道设置投递。

    :param message: 需要脱离原会话的通知消息
    :return: 已清除用户标识、原消息标识和既有目标的副本
    """
    detached = copy.deepcopy(message)
    detached.userid = None
    detached.original_message_id = None
    detached.original_chat_id = None
    detached.targets = None
    return detached


def _build_patched_steps(messaging_module: Any, original: Any) -> Any | None:
    """
    基于宿主原路由状态机构造带企业微信支持的替代实现。

    :param messaging_module: 宿主通知路由模块
    :param original: 宿主现有的通知路由状态机生成器函数
    :return: 可替换宿主的生成器函数，宿主结构不匹配时返回 None
    """
    delivery_type = getattr(messaging_module, "_NotificationRouteDelivery", None)
    if delivery_type is None:
        return None

    def patched_steps(
        message: Any,
        *,
        action: str | None,
        superuser: str,
    ) -> Generator[Any, Mapping[str, object] | None, None]:
        """
        在企业微信用户会话上叠加原会话回复与发送范围投递。

        宿主已经产出路由范围时直接沿用，避免与宿主新实现重复投递。
        """
        if action is not None or not _is_wechat_conversation(message):
            yield from original(message, action=action, superuser=superuser)
            return
        scope = _resolve_scope(message)
        if scope is None:
            yield from original(message, action=action, superuser=superuser)
            return
        # 原消息直接回到用户所在会话，保持微信交互的立即回复
        yield delivery_type(message=message, immediately=True)
        extra_tokens = [
            token for token in _scope_tokens(scope) if token != "user"
        ]
        if not extra_tokens:
            return
        yield from original(
            _detach_conversation(message),
            action=",".join(extra_tokens),
            superuser=superuser,
        )

    return patched_steps


def _load_messaging_module() -> Any | None:
    """
    导入宿主通知路由模块。

    :return: 宿主模块对象，导入失败时返回 None
    """
    try:
        return importlib.import_module(_MESSAGING_MODULE)
    except Exception as error:  # noqa: BLE001 - 导入失败时由调用方降级
        logger.error(f"企业微信通知范围修复：无法导入宿主通知路由模块：{error}")
        return None


def _current_steps() -> Any | None:
    """
    读取宿主当前使用的通知路由状态机函数。

    :return: 宿主路由函数，模块或属性缺失时返回 None
    """
    module = _load_messaging_module()
    if module is None:
        return None
    return getattr(module, _ROUTE_STEPS_ATTR, None)


def _install_patch() -> bool:
    """
    安装通知路由补丁，重复调用不会重复包装。

    :return: 补丁处于生效状态时返回 True
    """
    module = _load_messaging_module()
    if module is None:
        return False
    current = getattr(module, _ROUTE_STEPS_ATTR, None)
    if current is None:
        logger.error("企业微信通知范围修复：宿主缺少通知路由状态机，插件未生效")
        return False
    if getattr(current, _PATCH_MARKER, None) is not None:
        return True
    patched = _build_patched_steps(module, current)
    if patched is None:
        logger.error("企业微信通知范围修复：宿主路由结构不匹配，插件未生效")
        return False
    setattr(patched, _PATCH_MARKER, current)
    setattr(module, _ROUTE_STEPS_ATTR, patched)
    logger.info("企业微信通知范围修复：已启用")
    return True


def _remove_patch() -> None:
    """卸载通知路由补丁，恢复宿主原始实现。"""
    module = _load_messaging_module()
    if module is None:
        return
    current = getattr(module, _ROUTE_STEPS_ATTR, None)
    original = getattr(current, _PATCH_MARKER, None)
    if original is None:
        return
    setattr(module, _ROUTE_STEPS_ATTR, original)
    logger.info("企业微信通知范围修复：已停用")


def _is_patched() -> bool:
    """
    判断补丁当前是否生效。

    :return: 宿主路由函数带有本插件标记时返回 True
    """
    current = _current_steps()
    return getattr(current, _PATCH_MARKER, None) is not None


class WechatNotificationTargetFix(_PluginBase):
    """
    企业微信通知发送范围修复插件。

    宿主对已绑定用户的消息原样直发，使「通知发送范围」中的管理员、全体范围在
    企业微信渠道失效；启用本插件后，微信用户触发的消息会先回复原会话，再按范围
    追加管理员或全体投递。其它渠道的消息分发行为保持不变。
    """

    # 插件名称
    plugin_name = "企业微信通知范围修复"
    # 插件描述
    plugin_desc = "让企业微信渠道的用户消息也按通知发送范围追加管理员或全体投递。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/Seed680/MoviePilot-Plugins/main/icons/customplugin.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "Seed680"
    # 作者主页
    author_url = "https://github.com/Seed680"
    # 插件配置项ID前缀
    plugin_config_prefix = "wechatnotificationtargetfix_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 1

    # 是否启用修复
    _enabled = False

    def init_plugin(self, config: dict[str, Any] | None = None) -> None:
        """
        根据配置安装或卸载通知路由补丁。

        :param config: 插件配置字典
        """
        self._enabled = bool((config or {}).get("enabled", False))
        if self._enabled:
            _install_patch()
        else:
            _remove_patch()

    def stop_service(self) -> None:
        """停止插件时卸载补丁，避免继续改写宿主通知分发行为。"""
        _remove_patch()
        self._enabled = False

    def get_state(self) -> bool:
        """
        返回修复是否处于生效状态。

        :return: 宿主通知路由已由本插件接管时返回 True
        """
        return _is_patched()

    def get_form(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        构造插件配置表单与默认配置。

        :return: Vuetify 表单配置与默认配置字典
        """
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用企业微信通知范围修复",
                                            "hint": "启用后，微信用户触发的消息会先回复原会话，再按「通知发送范围」追加管理员或全体投递。",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "text": "发送范围中的「全部」在企业微信应用模式下会向应用全体成员广播，请确认后再启用；其它渠道的消息分发行为保持不变。",
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        ], {"enabled": False}

    def get_api(self) -> list[dict[str, Any]]:
        """
        本插件不注册插件 API。

        :return: 空列表
        """
        return []

    @staticmethod
    def get_command() -> list[dict[str, Any]]:
        """
        本插件不注册远程命令。

        :return: 空列表
        """
        return []

    def get_page(self) -> list[dict[str, Any]] | None:
        """
        本插件没有详情页面。

        :return: None
        """
        return None
