from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import override

from nonebot.adapters import Event as BaseEvent
from nonebot.compat import PYDANTIC_V2, ConfigDict
from nonebot.utils import escape_tag

from pydantic import BaseModel, Field

from .compat import field_validator, model_dump
from .message import Message
from .models import (
    Emoji,
    FormData,
    Gift,
    GoodsType,
    LeaveType,
    ListData,
    Member,
    MessageBody,
    MessageType,
    OperateType,
    Personal,
    ReactionTarget,
    ReactionType,
    Reference,
    TargetType,
)
from .utils import to_lower_camel


class EventType(str, Enum):
    MESSAGE = "2001"
    """消息事件"""
    MESSAGE_REACTION = "3001"
    """消息表情反应事件"""
    CARD_MESSAGE_BUTTON_CLICK = "3002"
    """卡片消息按钮事件"""
    CARD_MESSAGE_FORM_SUBMIT = "3003"
    """卡片消息表单回传事件"""
    CARD_MESSAGE_LIST_SUBMIT = "3004"
    """卡片消息列表回传事件"""
    CHANNEL_VOICE_MEMBER_JOIN = "5001"
    """成员加入语音频道事件"""
    CHANNEL_VOICE_MEMBER_LEAVE = "5002"
    """成员退出语音频道事件"""
    CHANNEL_ARTICLE = "6001"
    """帖子发布事件"""
    CHANNEL_ARTICLE_COMMENT = "6002"
    """帖子评论回复事件"""
    MEMBER_JOIN = "4001"
    """成员加入事件"""
    MEMBER_LEAVE = "4002"
    """成员退出事件"""
    MEMBER_INVITE = "4003"
    """成员邀请事件"""
    GIFT_SEND = "7001"
    """赠礼成功事件"""
    INTEGRAL_CHANGE = "8001"
    """积分变更事件"""
    GOODS_PURCHASE = "9001"
    """商品购买成功事件"""
    PERSONAL_MESSAGE = "1001"
    """私信事件"""


class Event(BaseEvent):
    event_id: str
    event_type: EventType
    timestamp: datetime

    dodo_source_id: str

    if PYDANTIC_V2:
        model_config = ConfigDict(
            extra="allow",
            populate_by_name=True,
            alias_generator=to_lower_camel,
        )
    else:

        class Config(ConfigDict):
            extra = "allow"
            allow_population_by_field_name = True
            alias_generator = to_lower_camel

    @property
    def user_id(self) -> str:
        return self.dodo_source_id

    @property
    def time(self) -> datetime:
        return self.timestamp

    @override
    def get_event_name(self) -> str:
        return self.__class__.__name__

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(model_dump(self)))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        return self.dodo_source_id

    @override
    def get_session_id(self) -> str:
        return self.dodo_source_id

    @override
    def is_tome(self) -> bool:
        return False


class NoticeEvent(Event):
    @override
    def get_type(self) -> str:
        return "notice"


class MessageEvent(Event):
    island_source_id: Optional[str] = None
    personal: Personal
    message_id: str
    message_type: MessageType
    message_body: MessageBody

    to_me: bool = False

    @property
    def message(self) -> Message:
        return self.get_message()

    @property
    def original_message(self) -> Message:
        return getattr(self, "_original_message", self.get_message())

    @property
    def reply(self) -> Optional[Reference]:
        return getattr(self, "reference", None)

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(
                self,
                "_message",
                Message.from_message_body(
                    self.message_body, getattr(self, "reference", None)
                ),
            )
            setattr(
                self,
                "_original_message",
                Message.from_message_body(
                    self.message_body, getattr(self, "reference", None)
                ),
            )
        return getattr(self, "_message")

    @override
    def is_tome(self) -> bool:
        return self.to_me


class ChannelMessageEvent(MessageEvent):
    event_type: Literal[EventType.MESSAGE]

    member: Member
    island_source_id: str
    channel_id: str
    reference: Optional[Reference] = None


class MessageReactionEvent(NoticeEvent):
    event_type: Literal[EventType.MESSAGE_REACTION]

    island_source_id: str
    channel_id: str
    message_id: str
    personal: Personal
    member: Member

    reaction_target: ReactionTarget
    reaction_emoji: Emoji
    reaction_type: ReactionType


class CardMessageButtonClickEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_BUTTON_CLICK]

    island_source_id: str
    channel_id: str
    message_id: str
    personal: Personal
    member: Member
    interact_custom_id: Optional[str] = None
    value: str


class CardMessageFormSubmitEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_FORM_SUBMIT]

    island_source_id: str
    channel_id: str
    message_id: str
    personal: Personal
    member: Member
    interact_custom_id: Optional[str] = None
    form_data: List[FormData]


class CardMessageListSubmitEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_LIST_SUBMIT]

    island_source_id: str
    channel_id: str
    message_id: str
    personal: Personal
    member: Member
    interact_custom_id: Optional[str] = None
    list_data: List[ListData]


class ChannelVoiceMemberJoinEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_VOICE_MEMBER_JOIN]

    island_source_id: str
    channel_id: str
    personal: Personal
    member: Member


class ChannelVoiceMemberLeaveEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_VOICE_MEMBER_LEAVE]

    island_source_id: str
    channel_id: str
    personal: Personal
    member: Member


class ChannelArticleEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_ARTICLE]

    island_source_id: str
    channel_id: str
    personal: Personal
    member: Member
    artical_id: str
    title: str
    image_list: List[str]
    content: str


class ChannelArticleCommentEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_ARTICLE_COMMENT]

    island_source_id: str
    channel_id: str
    personal: Personal
    member: Member
    artical_id: str
    comment_id: str
    reply_id: str
    image_list: List[str]
    content: str


class MemberJoinEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_JOIN]

    island_source_id: str
    personal: Personal
    modify_time: datetime


class MemberLeaveEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_LEAVE]

    island_source_id: str
    personal: Personal
    leave_type: LeaveType
    operate_dodo_source_id: str
    modify_time: datetime


class MemberInviteEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_INVITE]

    island_source_id: str
    dodo_island_nick_name: str
    to_dodo_source_id: str
    to_dodo_island_nick_name: str


class GiftSendEvent(NoticeEvent):
    event_type: Literal[EventType.GIFT_SEND]

    island_source_id: str
    channel_id: str
    order_no: str
    target_type: TargetType
    target_id: str
    total_amount: float
    gift: Gift
    island_ratio: float
    island_income: float
    dodo_island_nick_name: str
    to_dodo_source_id: str
    to_dodo_island_nick_name: str
    to_dodo_ratio: float
    to_dodo_income: float


class IntegralChangeEvent(NoticeEvent):
    event_type: Literal[EventType.INTEGRAL_CHANGE]

    island_source_id: str
    operate_type: OperateType
    integral: int


class GoodsPurchaseEvent(NoticeEvent):
    event_type: Literal[EventType.GOODS_PURCHASE]

    island_source_id: str
    order_no: str
    goods_type: GoodsType
    goods_id: str
    goods_name: str
    goods_image_list: List[str]


class PersonalMessageEvent(MessageEvent):
    event_type: Literal[EventType.PERSONAL_MESSAGE]

    to_me: bool = True


EventClass = Union[
    ChannelMessageEvent,
    MessageReactionEvent,
    CardMessageButtonClickEvent,
    CardMessageFormSubmitEvent,
    CardMessageListSubmitEvent,
    ChannelVoiceMemberJoinEvent,
    ChannelVoiceMemberLeaveEvent,
    ChannelArticleEvent,
    ChannelArticleCommentEvent,
    MemberJoinEvent,
    MemberLeaveEvent,
    MemberInviteEvent,
    GiftSendEvent,
    IntegralChangeEvent,
    GoodsPurchaseEvent,
    PersonalMessageEvent,
]


class EventSubject(BaseModel):
    type: int
    data: EventClass = Field(discriminator="event_type")
    version: str

    @field_validator("data", mode="before")
    def pre_handle_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        v.update(v.pop("eventBody"))
        return v


__all__ = [
    "Event",
    "EventType",
    "NoticeEvent",
    "MessageEvent",
    "ChannelMessageEvent",
    "MessageReactionEvent",
    "CardMessageButtonClickEvent",
    "CardMessageFormSubmitEvent",
    "CardMessageListSubmitEvent",
    "ChannelVoiceMemberJoinEvent",
    "ChannelVoiceMemberLeaveEvent",
    "ChannelArticleEvent",
    "ChannelArticleCommentEvent",
    "MemberJoinEvent",
    "MemberLeaveEvent",
    "MemberInviteEvent",
    "GiftSendEvent",
    "IntegralChangeEvent",
    "GoodsPurchaseEvent",
    "PersonalMessageEvent",
]
