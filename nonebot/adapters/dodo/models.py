from datetime import datetime
from enum import IntEnum
from typing import (
    Any,
    ClassVar,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
)

from nonebot.compat import PYDANTIC_V2, ConfigDict

from pydantic import (
    BaseModel as PydanticBaseModel,
    Field,
)
from pydantic.generics import GenericModel

from .utils import to_lower_camel

T = TypeVar("T")


class BaseModel(PydanticBaseModel):
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


# API #
class ListResult(GenericModel, Generic[T]):
    max_id: int
    list: List[T]

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

    def __iter__(self) -> Iterator[T]:
        return iter(self.list)


class ApiReturn(BaseModel):
    status: int
    message: str
    data: Any


## 机器人API ##


class BotInfo(BaseModel):
    client_id: str
    dodo_source_id: str
    nick_name: str
    avatar_url: str


class BotInviteInfo(BaseModel):
    dodo_source_id: str
    nick_name: str
    avatar_url: str


## 群API ##
class IslandInfo(BaseModel):
    island_source_id: str
    island_id: Optional[str] = None
    island_name: str
    cover_url: str
    member_count: int
    online_member_count: int
    description: Optional[str] = None
    default_channel_id: str
    system_channel_id: str
    owner_dodo_source_id: Optional[str] = None


class IslandLevelRankInfo(BaseModel):
    dodo_source_id: str
    nick_name: str
    level: int
    rank: int


class IslandMuteOrBanData(BaseModel):
    dodo_source_id: str


## 频道API ##
class ChannelType(IntEnum):
    TEXT = 1
    VOICE = 2
    ARTICLE = 4
    LINK = 5
    PROFILE = 6


class ChannelInfo(BaseModel):
    channel_id: str
    channel_name: str
    channel_type: ChannelType
    island_source_id: Optional[str] = None
    default_flag: bool
    group_id: str
    group_name: str


class ChannelData(BaseModel):
    channel_id: str


## 频道消息API ##
class MessageReturn(BaseModel):
    message_id: str


class MessageReactionInfo(BaseModel):
    emoji: "Emoji"
    count: int


class MessageReactionMemberInfo(BaseModel):
    dodo_source_id: str
    nick_name: str


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


class ChannelVoiceMemberStatusInfo(BaseModel):
    channel_id: str
    spk_status: bool
    mic_status: bool
    mic_sort_status: MicSortStatus


## 帖子频道API ##
class ChannelArticleData(BaseModel):
    article_id: str


class BussinessType(IntEnum):
    ARTICLE = 1
    COMMENT = 2
    REPLY = 3


## 身份组API ##
class RoleInfo(BaseModel):
    role_id: str
    role_name: str
    role_color: str
    position: int
    permission: str
    member_count: int


class RoleData(BaseModel):
    role_id: str


class RoleMemberInfo(BaseModel):
    dodo_source_id: str
    nick_name: str


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


class MemberInfo(BaseModel):
    island_source_id: Optional[str] = None
    dodo_source_id: str
    nick_name: str
    personal_nick_name: str
    avatar_url: str
    join_time: datetime
    sex: "Sex"
    level: int
    is_bot: bool
    online_device: OnlineDevice
    online_status: OnlineStatus
    inviter_dodo_source_id: Optional[str] = None


class MemberRoleInfo(BaseModel):
    role_id: str
    role_name: str
    role_color: str
    position: int
    permission: str


class GetMemberInvitationInfoReturn(BaseModel):
    dodo_source_id: str
    nick_name: str
    invitation_count: int


class DoDoIDMapData(BaseModel):
    dodo_id: str
    dodo_source_id: str


## 赠礼系统API ##
class GiftAccountInfo(BaseModel):
    total_income: float
    settlable_income: float
    transferable_income: float


class DefaultRatio(BaseModel):
    island_ratio: float
    user_ratio: float
    platform_ratio: float


class RoleRatio(BaseModel):
    role_id: str
    role_name: str
    island_ratio: float
    user_ratio: float
    platform_ratio: float


class GiftShareRatioInfo(BaseModel):
    default_ratio: DefaultRatio
    role_ratio_list: List[RoleRatio]


class GiftInfo(BaseModel):
    gift_id: str
    gift_count: int
    gift_total_amount: float


class GiftMemberInfo(BaseModel):
    dodo_source_id: str
    nick_name: str
    gift_count: int


class GiftGrossValueInfo(BaseModel):
    dodo_source_id: str
    nick_name: str
    gift_total_amount: float


## 积分系统API ##
class IntegralInfo(BaseModel):
    integral_balance: int


## 资源API ##
class PictureInfo(BaseModel):
    url: str
    width: int
    height: int


## 事件API ##


class WebSocketConnectionData(BaseModel):
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
    is_original: Optional[OriginType] = None


class VideoMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.VIDEO]] = MessageType.VIDEO
    url: str
    cover_url: Optional[str] = None
    duration: Optional[int] = None
    size: Optional[int] = None


class ShareMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.SHARE]] = MessageType.SHARE
    jump_url: str


class FileMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.FILE]] = MessageType.FILE
    url: str
    name: str
    size: int


class CardMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.CARD]] = MessageType.CARD
    content: Optional[str] = None
    card: "Card"


class RedPacketMessage(BaseModel):
    __type__: ClassVar[Literal[MessageType.RED_PACKET]] = MessageType.RED_PACKET
    type: RedPacketType
    count: int
    total_amount: float
    receiver_type: ReceiverType
    role_id_list: Optional[List[str]] = None


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
    nick_name: str
    avatar_url: str
    sex: Sex


class Member(BaseModel):
    nick_name: str
    join_time: datetime


class Reference(BaseModel):
    message_id: str
    dodo_source_id: str
    nick_name: str


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
    title: Optional[str] = None


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
    content: Optional[str] = None
    src: Optional[str] = None


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
    title: Optional[str] = None
    cover: str
    src: str


### 倒计时 ###
class CardCountdown(BaseModel):
    type: Literal["countdown"] = Field(default="countdown", init=False)
    title: Optional[str] = None
    style: Literal["day", "hour"]
    end_time: int


class CardDivider(BaseModel):
    type: Literal["divider"] = Field(default="divider", init=False)


## 交互组件 ##
### 按钮 ###
class ButtonClickAction(BaseModel):
    value: Optional[str] = None
    action: Literal["link_url", "call_back", "copy_content", "form"]


class CardButton(BaseModel):
    type: Literal["button"] = Field(default="button", init=False)
    interact_custom_id: Optional[str] = None
    click: ButtonClickAction
    color: Literal[
        "grey", "red", "orange", "green", "blue", "purple", "default"
    ] = "default"
    name: str
    form: Optional["CallbackForm"] = None


class CardButtonGroup(BaseModel):
    type: Literal["button-group"] = Field(default="button-group", init=False)
    elements: List[CardButton]


### 列表选择器 ###
class ListSelectorElement(BaseModel):
    name: str
    desc: Optional[str] = None


class CardListSelector(BaseModel):
    type: Literal["list-selector"] = Field(default="list-selector", init=False)
    interact_custom_id: Optional[str] = None
    placeholder: Optional[str] = None
    elements: List[ListSelectorElement]
    min: int
    max: int


### 回传表单 ###
class CallbackFormData(BaseModel):
    type: Literal["input"] = Field(default="input", init=False)
    key: str
    title: str
    rows: int = Field(le=4)
    placeholder: Optional[str] = None
    min_char: int = Field(ge=0, le=4000)
    max_char: int = Field(ge=1, le=4000)


class CallbackForm(BaseModel):
    title: str
    elements: List[CallbackFormData]


### 文字 + 模块 ###
class CardTextModule(BaseModel):
    type: Literal["section"] = Field(default="section", init=False)
    align: Optional[Literal["left", "right"]] = None
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

MemberInfo.update_forward_refs()
MessageReactionInfo.update_forward_refs()
CardButton.update_forward_refs()
Card.update_forward_refs()
CardMessage.update_forward_refs()
