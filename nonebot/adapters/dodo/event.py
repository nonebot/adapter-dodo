from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import override

from nonebot.adapters import Event as BaseEvent
from nonebot.utils import escape_tag

from pydantic import BaseModel, Field, validator

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
    event_id: str = Field(alias="eventId")
    event_type: EventType = Field(alias="eventType")
    timestamp: datetime

    dodo_source_id: str = Field(alias="dodoSourceId")

    class Config:
        extra = "allow"

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
        return escape_tag(str(self.dict()))

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
    island_source_id: Optional[str] = Field(default=None, alias="islandSourceId")
    personal: Personal
    message_id: str = Field(alias="messageId")
    message_type: MessageType = Field(alias="messageType")
    message_body: MessageBody = Field(alias="messageBody")

    to_me: bool = Field(default=False, alias="toMe")

    @property
    def message(self) -> Message:
        return self.get_message()

    @property
    def origin_message(self) -> Message:
        if not hasattr(self, "_origin_message"):
            return self.get_message()
        return getattr(self, "_origin_message")

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
                "_origin_message",
                Message.from_message_body(
                    self.message_body, getattr(self, "reference", None)
                ),
            )
        return getattr(self, "_message")

    @override
    def is_tome(self) -> bool:
        return self.to_me


class ChannelMessageEvent(MessageEvent):
    event_type: Literal[EventType.MESSAGE] = Field(
        default=EventType.MESSAGE, alias="eventType"
    )

    member: Member
    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    reference: Optional[Reference] = Field(default=None)


class MessageReactionEvent(NoticeEvent):
    event_type: Literal[EventType.MESSAGE_REACTION] = Field(
        default=EventType.MESSAGE_REACTION, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    message_id: str = Field(alias="messageId")
    personal: Personal
    member: Member

    reaction_target: ReactionTarget = Field(alias="reactionTarget")
    reaction_emoji: Emoji = Field(alias="reactionEmoji")
    reaction_type: ReactionType = Field(alias="reactionType")


class CardMessageButtonClickEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_BUTTON_CLICK] = Field(
        default=EventType.CARD_MESSAGE_BUTTON_CLICK, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    message_id: str = Field(alias="messageId")
    personal: Personal
    member: Member
    interact_custom_id: str = Field(alias="interactCustomId")
    value: str


class CardMessageFormSubmitEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_FORM_SUBMIT] = Field(
        default=EventType.CARD_MESSAGE_FORM_SUBMIT, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    message_id: str = Field(alias="messageId")
    personal: Personal
    member: Member
    interact_custom_id: str = Field(alias="interactCustomId")
    form_data: List[FormData] = Field(alias="formData")


class CardMessageListSubmitEvent(NoticeEvent):
    event_type: Literal[EventType.CARD_MESSAGE_LIST_SUBMIT] = Field(
        default=EventType.CARD_MESSAGE_LIST_SUBMIT, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    message_id: str = Field(alias="messageId")
    personal: Personal
    member: Member
    interact_custom_id: str = Field(alias="interactCustomId")
    list_data: List[ListData] = Field(alias="listData")


class ChannelVoiceMemberJoinEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_VOICE_MEMBER_JOIN] = Field(
        default=EventType.CHANNEL_VOICE_MEMBER_JOIN, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    personal: Personal
    member: Member


class ChannelVoiceMemberLeaveEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_VOICE_MEMBER_LEAVE] = Field(
        default=EventType.CHANNEL_VOICE_MEMBER_LEAVE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    personal: Personal
    member: Member


class ChannelArticleEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_ARTICLE] = Field(
        default=EventType.CHANNEL_ARTICLE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    personal: Personal
    member: Member
    artical_id: str = Field(alias="articalId")
    title: str
    image_list: List[str] = Field(alias="imageList")
    content: str


class ChannelArticleCommentEvent(NoticeEvent):
    event_type: Literal[EventType.CHANNEL_ARTICLE_COMMENT] = Field(
        default=EventType.CHANNEL_ARTICLE_COMMENT, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    personal: Personal
    member: Member
    artical_id: str = Field(alias="articalId")
    comment_id: str = Field(alias="commentId")
    reply_id: str = Field(alias="replyId")
    image_list: List[str] = Field(alias="imageList")
    content: str


class MemberJoinEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_JOIN] = Field(
        default=EventType.MEMBER_JOIN, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    personal: Personal
    modify_time: datetime = Field(alias="modifyTime")


class MemberLeaveEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_LEAVE] = Field(
        default=EventType.MEMBER_LEAVE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    personal: Personal
    leave_type: LeaveType = Field(alias="leaveType")
    operate_dodo_source_id: str = Field(alias="operateDodoSourceId")
    modify_time: datetime = Field(alias="modifyTime")


class MemberInviteEvent(NoticeEvent):
    event_type: Literal[EventType.MEMBER_INVITE] = Field(
        default=EventType.MEMBER_INVITE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    dodo_island_nick_name: str = Field(alias="dodoIslandNickName")
    to_dodo_source_id: str = Field(alias="toDodoSourceId")
    to_dodo_island_nick_name: str = Field(alias="toDodoIslandNickName")


class GiftSendEvent(NoticeEvent):
    event_type: Literal[EventType.GIFT_SEND] = Field(
        default=EventType.GIFT_SEND, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    channel_id: str = Field(alias="channelId")
    order_no: str = Field(alias="orderNo")
    target_type: TargetType = Field(alias="targetType")
    target_id: str = Field(alias="targetId")
    total_amount: float = Field(alias="totalAmount")
    gift: Gift
    island_ratio: float = Field(alias="islandRatio")
    island_income: float = Field(alias="islandIncome")
    dodo_island_nick_name: str = Field(alias="dodoIslandNickName")
    to_dodo_source_id: str = Field(alias="toDodoSourceId")
    to_dodo_island_nick_name: str = Field(alias="toDodoIslandNickName")
    to_dodo_ratio: float = Field(alias="toDodoRatio")
    to_dodo_income: float = Field(alias="toDodoIncome")


class IntegralChangeEvent(NoticeEvent):
    event_type: Literal[EventType.INTEGRAL_CHANGE] = Field(
        default=EventType.INTEGRAL_CHANGE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    operate_type: OperateType = Field(alias="operateType")
    integral: int


class GoodsPurchaseEvent(NoticeEvent):
    event_type: Literal[EventType.GOODS_PURCHASE] = Field(
        default=EventType.GOODS_PURCHASE, alias="eventType"
    )

    island_source_id: str = Field(alias="islandSourceId")
    order_no: str = Field(alias="orderNo")
    goods_type: GoodsType = Field(alias="goodsType")
    goods_id: str = Field(alias="goodsId")
    goods_name: str = Field(alias="goodsName")
    goods_image_list: List[str] = Field(alias="goodsImageList")


class PersonalMessageEvent(MessageEvent):
    event_type: Literal[EventType.PERSONAL_MESSAGE] = Field(
        default=EventType.PERSONAL_MESSAGE, alias="eventType"
    )

    to_me: bool = Field(default=True, alias="toMe")


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

    @validator("data", pre=True)
    def pre_handle_data(cls, v: Dict[str, Any]):
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
