from datetime import datetime
from enum import IntEnum
from typing import Any, ClassVar, Generic, List, Literal, Optional, TypeVar, Union

from pydantic import (
    BaseModel,
    Field,
)
from pydantic.generics import GenericModel

T = TypeVar("T")


# API #
class ListResult(GenericModel, Generic[T]):
    max_id: int = Field(alias="maxId")
    list: List[T]


class ApiReturn(BaseModel):
    status: int
    message: str
    data: Any


## 机器人API ##


class BotInfo(BaseModel):
    client_id: str = Field(alias="clientId")
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    avatar_url: str = Field(alias="avatarUrl")


class BotInviteData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    avatar_url: str = Field(alias="avatarUrl")


GetBotInviteListReturn = ListResult[BotInviteData]


## 群API ##
class IslandData(BaseModel):
    island_source_id: str = Field(alias="islandSourceId")
    island_id: Optional[str] = Field(default=None, alias="islandId")
    island_name: str = Field(alias="islandName")
    cover_url: str = Field(alias="coverUrl")
    member_count: int = Field(alias="memberCount")
    online_member_count: int = Field(alias="onlineMemberCount")
    description: Optional[str] = Field(default=None)
    default_channel_id: str = Field(alias="defaultChannelId")
    system_channel_id: str = Field(alias="systemChannelId")
    owner_dodo_source_id: Optional[str] = Field(default=None, alias="ownerDodoSourceId")


GetIslandListReturn = List[IslandData]
GetIslandInfoReturn = IslandData


class IslandLevelRankData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    level: int
    rank: int


GetIslandLevelRankListReturn = List[IslandLevelRankData]


class IslandMuteOrBanData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")


GetIslandMuteOrBanListReturn = ListResult[IslandMuteOrBanData]


## 频道API ##
class ChannelType(IntEnum):
    TEXT = 1
    VOICE = 2
    ARTICLE = 4
    LINK = 5
    PROFILE = 6


class ChannelData(BaseModel):
    channel_id: str = Field(alias="channelId")
    channel_name: str = Field(alias="channelName")
    channel_type: ChannelType = Field(alias="channelType")
    island_source_id: Optional[str] = Field(default=None, alias="islandSourceId")
    default_flag: bool = Field(alias="defaultFlag")
    group_id: str = Field(alias="groupId")
    group_name: str = Field(alias="groupName")


GetChannelListReturn = List[ChannelData]
GetChannelInfoReturn = ChannelData


class SetChannelAddReturn(BaseModel):
    channel_id: str = Field(alias="channelId")


## 频道消息API ##
class SetChannelMessageSendReturn(BaseModel):
    message_id: str = Field(alias="messageId")


class MessageReactionData(BaseModel):
    emoji: "Emoji"
    count: int


GetChannelMessageReactionListReturn = List[MessageReactionData]


class MessageReactionMemberData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")


GetChannelMessageReactionMemberListReturn = ListResult[MessageReactionMemberData]


## 语音频道API ##
class MicSortStatus(IntEnum):
    UNDER_MIC = 1
    REQUEST_MIC = 2
    ON_MIC = 3


class ManageOperateType(IntEnum):
    DOWN = 0
    UP = 1
    CLOSE = 2
    REMOVE = 3


class GetChannelVoiceMemberStatusReturn(BaseModel):
    channel_id: str = Field(alias="channelId")
    spk_status: bool = Field(alias="spkStatus")
    mic_status: bool = Field(alias="micStatus")
    mic_sort_status: MicSortStatus = Field(alias="micSortStatus")


## 帖子频道API ##
class SetChannelArticleAddReturn(BaseModel):
    article_id: str = Field(alias="articleId")


class BussinessType(IntEnum):
    ARTICLE = 1
    COMMENT = 2
    REPLY = 3


## 身份组API ##
class RoleData(BaseModel):
    role_id: str = Field(alias="roleId")
    role_name: str = Field(alias="roleName")
    role_color: str = Field(alias="roleColor")
    position: int
    permission: str
    member_count: int = Field(alias="memberCount")


GetRoleListReturn = List[RoleData]


class SetRoleAddReturn(BaseModel):
    role_id: str = Field(alias="roleId")


class RoleMemberData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")


GetRoleMemberListReturn = ListResult[RoleMemberData]


## 成员API ##
class OnlineDevice(IntEnum):
    OFFLINE = 0
    PC_ONLINE = 1
    MOBILE_ONLINE = 2


class OnlineStatus(IntEnum):
    OFFLINE = 0
    ONLINE = 1
    NOT_DISTURB = 2
    LEAVE = 3


class MemberData(BaseModel):
    island_source_id: Optional[str] = Field(default=None, alias="islandSourceId")
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    personal_nick_name: str = Field(alias="personalNickName")
    avatar_url: str = Field(alias="avatarUrl")
    join_time: datetime = Field(alias="joinTime")
    sex: "Sex"
    level: int
    is_bot: bool = Field(alias="isBot")
    online_device: OnlineDevice = Field(alias="onlineDevice")
    online_status: OnlineStatus = Field(alias="onlineStatus")
    inviter_dodo_source_id: Optional[str] = Field(
        default=None, alias="inviterDodoSourceId"
    )


GetMemberListReturn = ListResult[MemberData]
GetMemberInfoReturn = MemberData


class MemberRoleData(BaseModel):
    role_id: str = Field(alias="roleId")
    role_name: str = Field(alias="roleName")
    role_color: str = Field(alias="roleColor")
    position: int
    permission: str


GetMemberRoleListReturn = List[MemberRoleData]


class GetMemberInvitationInfoReturn(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    invitation_count: int = Field(alias="invitationCount")


class DoDoIDMappingData(BaseModel):
    dodo_id: str = Field(alias="dodoId")
    dodo_source_id: str = Field(alias="dodoSourceId")


GetMemberDodoIdMapListReturn = List[DoDoIDMappingData]


## 赠礼系统API ##
class GetGiftAccountReturn(BaseModel):
    total_income: float = Field(alias="totalIncome")
    settlable_income: float = Field(alias="settlableIncome")
    transferable_income: float = Field(alias="transferableIncome")


class DefaultRatio(BaseModel):
    island_ratio: float = Field(alias="islandRatio")
    user_ratio: float = Field(alias="userRatio")
    platform_ratio: float = Field(alias="platformRatio")


class RoleRatio(BaseModel):
    role_id: str = Field(alias="roleId")
    role_name: str = Field(alias="roleName")
    island_ratio: float = Field(alias="islandRatio")
    user_ratio: float = Field(alias="userRatio")
    platform_ratio: float = Field(alias="platformRatio")


class GetGiftShareRatioInfoReturn(BaseModel):
    default_ratio: DefaultRatio = Field(alias="defaultRatio")
    role_ratio_list: List[RoleRatio] = Field(alias="roleRatioList")


class GiftData(BaseModel):
    gift_id: str = Field(alias="giftId")
    gift_count: int = Field(alias="giftCount")
    gift_total_amount: float = Field(alias="giftTotalAmount")


GetGiftListReturn = List[GiftData]


class GiftMemberData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    gift_count: int = Field(alias="giftCount")


GetGiftMemberListReturn = ListResult[GiftMemberData]


class GiftGrossValueData(BaseModel):
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")
    gift_total_amount: float = Field(alias="giftTotalAmount")


GetGiftGrossValueListReturn = ListResult[GiftGrossValueData]


## 积分系统API ##
class GetIntegralInfoReturn(BaseModel):
    integral_balance: int = Field(alias="integralBalance")


class SetIntegralEditReturn(BaseModel):
    integral_balance: int = Field(alias="integralBalance")


## 私信API ##
class SetPersonalMessageSendReturn(BaseModel):
    message_id: str = Field(alias="messageId")


## 资源API ##
class SetResourcePictureUploadReturn(BaseModel):
    url: str
    width: int
    height: int


## 事件API ##


class GetWebSocketConnectionReturn(BaseModel):
    endpoint: str


# 消息 #

## 消息内容 ##


class MessageType(IntEnum):
    TEXT = 1
    PICTURE = 2
    VIDEO = 3
    SHARE = 4
    FILE = 5
    CARD = 6
    RED_PACKET = 7


class OriginType(IntEnum):
    COMPRESSED = 0
    RAW = 1


class RedPacketType(IntEnum):
    LUCKY = 1
    NORMAL = 2


class ReceiverType(IntEnum):
    ALL_MEMBER = 1
    ROLE = 2


class TextMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.TEXT]] = MessageType.TEXT
    content: str


class PictureMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.PICTURE]] = MessageType.PICTURE
    url: str
    width: int
    height: int
    is_original: Optional[OriginType] = Field(default=None, alias="isOriginal")


class VideoMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.VIDEO]] = MessageType.VIDEO
    url: str
    cover_url: Optional[str] = Field(default=None, alias="coverUrl")
    duration: Optional[int] = Field(default=None)
    size: Optional[int] = Field(default=None)


class ShareMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.SHARE]] = MessageType.SHARE
    jump_url: str = Field(alias="jumpUrl")


class FileMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.FILE]] = MessageType.FILE
    url: str
    name: str
    size: int


class CardMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.CARD]] = MessageType.CARD
    content: Optional[str] = Field(default=None)
    card: "Card"


class RedPacketMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.RED_PACKET]] = MessageType.RED_PACKET
    type: RedPacketType
    count: int
    total_amount: float = Field(alias="totalAmount")
    receiver_type: ReceiverType = Field(alias="receiverType")
    role_id_list: Optional[List[str]] = Field(default=None, alias="roleIdList")


MessageBody = Union[
    TextMessage,
    PictureMessage,
    VideoMessage,
    ShareMessage,
    FileMessage,
    CardMessage,
    RedPacketMessage,
]

## 消息模型 ##


class Sex(IntEnum):
    PRIVACY = -1
    FEMALE = 0
    MALE = 1


class Personal(BaseModel):
    nick_name: str = Field(alias="nickName")
    avatar_url: str = Field(alias="avatarUrl")
    sex: Sex


class Member(BaseModel):
    nick_name: str = Field(alias="nickName")
    join_time: datetime = Field(alias="joinTime")


class Reference(BaseModel):
    message_id: str = Field(alias="messageId")
    dodo_source_id: str = Field(alias="dodoSourceId")
    nick_name: str = Field(alias="nickName")


class ReactionTarget(BaseModel):
    type: int
    id: str


class ReactionType(IntEnum):
    DELETE = 0
    ADD = 1


class Gift(BaseModel):
    id: str
    name: str
    count: int


## 消息表情 ##


class Emoji(BaseModel):
    type: int
    id: str


## 事件相关 ##


class FormData(BaseModel):
    key: str
    value: str


class ListData(BaseModel):
    name: str


class LeaveType(IntEnum):
    VOLUNTARY = 1
    KICKED = 2


class TargetType(IntEnum):
    MESSAGE = 1
    ARTICLE = 2


class OperateType(IntEnum):
    SIGN = 1
    INVITE = 2
    TRANSFER_MONEY = 3
    PURCHASE_GOODS = 4
    MANAGE_Integral = 5
    LEAVE_GROUP = 6


class GoodsType(IntEnum):
    ROLE = 1
    CUSTOM = 2


# 卡片 #


## 卡片属性 ##
CardTheme = Literal[
    "grey",
    "red",
    "orange",
    "yellow",
    "green",
    "indigo",
    "blue",
    "purple",
    "black",
    "default",
]


class Card(BaseModel):
    type: Literal["card"] = Field(default="card", init=False)
    components: List["Component"]
    theme: CardTheme = Field(default="default")
    title: Optional[str] = Field(default=None)


## 内容组件 ##


### 标题 ###
class TextData(BaseModel):
    type: Literal["plain-text", "dodo-md"]
    content: str


class CardTitle(BaseModel):
    type: Literal["header"] = Field(default="header", init=False)
    text: TextData


### 文本 ###


class CardText(BaseModel):
    type: Literal["section"] = Field(default="section", init=False)
    text: TextData


### 多栏文本 ###
class MultiTextData(BaseModel):
    type: Literal["paragraph"] = Field(default="paragraph", init=False)
    cols: int = Field(ge=2, le=6)
    fields: List[TextData]


class CardMultiText(BaseModel):
    type: Literal["section"] = Field(default="section", init=False)
    text: MultiTextData


### 备注 ###
class RemarkData(BaseModel):
    type: Literal["image", "plain-text", "dodo-md"]
    content: Optional[str] = Field(default=None)
    src: Optional[str] = Field(default=None)


class CardRemark(BaseModel):
    type: Literal["remark"] = Field(default="remark", init=False)
    elements: List[RemarkData]


### 图片 ###
class CardImage(BaseModel):
    type: Literal["image"] = Field(default="image", init=False)
    src: str


### 多图 ###
class CardImageGroup(BaseModel):
    type: Literal["image-group"] = Field(default="image-group", init=False)
    elements: List[CardImage] = Field(max_items=9)


### 视频 ###
class CardVideo(BaseModel):
    type: Literal["video"] = Field(default="video", init=False)
    title: Optional[str] = Field(default=None)
    cover: str
    src: str


### 倒计时 ###
class CardCountdown(BaseModel):
    type: Literal["countdown"] = Field(default="countdown", init=False)
    title: Optional[str] = Field(default=None)
    style: Literal["day", "hour"]
    end_time: int = Field(alias="endTime")


class CardDivider(BaseModel):
    type: Literal["divider"] = Field(default="divider", init=False)


## 交互组件 ##
### 按钮 ###
class ButtonClickAction(BaseModel):
    value: Optional[str] = Field(default=None)
    action: Literal["link_url", "call_back", "copy_content", "form"]


class CardButton(BaseModel):
    type: Literal["button"] = Field(default="button", init=False)
    interact_custom_id: Optional[str] = Field(default=None, alias="interactCustomId")
    click: ButtonClickAction
    color: Literal[
        "grey", "red", "orange", "green", "blue", "purple", "default"
    ] = "default"
    name: str
    form: Optional["CallbackForm"] = Field(default=None)


class CardButtonGroup(BaseModel):
    type: Literal["button-group"] = Field(default="button-group", init=False)
    elements: List[CardButton]


### 列表选择器 ###
class ListSelectorElement(BaseModel):
    name: str
    desc: Optional[str] = Field(default=None)


class CardListSelector(BaseModel):
    type: Literal["list-selector"] = Field(default="list-selector", init=False)
    interact_custom_id: Optional[str] = Field(default=None, alias="interactCustomId")
    placeholder: Optional[str] = Field(default=None)
    elements: List[ListSelectorElement]
    min: int
    max: int


### 回传表单 ###
class CallbackFormData(BaseModel):
    type: Literal["input"] = Field(default="input", init=False)
    key: str
    title: str
    rows: int = Field(le=4)
    placeholder: Optional[str] = Field(default=None)
    min_char: int = Field(ge=0, le=4000, alias="minChar")
    max_char: int = Field(ge=1, le=4000, alias="maxChar")


class CallbackForm(BaseModel):
    title: str
    elements: List[CallbackFormData]


### 文字 + 模块 ###
class CardTextModule(BaseModel):
    type: Literal["section"] = Field(default="section", init=False)
    align: Optional[Literal["left", "right"]] = Field(default=None)
    text: Union[CardText, CardMultiText]
    accessory: Union[CardImage, CardButton]


Component = Union[
    CardTitle,
    CardText,
    CardMultiText,
    CardRemark,
    CardImage,
    CardImageGroup,
    CardVideo,
    CardCountdown,
    CardDivider,
    CardButtonGroup,
    CardListSelector,
    CardTextModule,
]

MemberData.update_forward_refs()
MessageReactionData.update_forward_refs()
CardButton.update_forward_refs()
Card.update_forward_refs()
CardMessage.update_forward_refs()
