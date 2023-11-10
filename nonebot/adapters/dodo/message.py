from dataclasses import dataclass
import re
from typing import (
    TYPE_CHECKING,
    Iterable,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypedDict,
)
from typing_extensions import Self, override

from nonebot.adapters import (
    Message as BaseMessage,
    MessageSegment as BaseMessageSegment,
)

from .models import (
    Card,
    CardMessage,
    CardTheme,
    Component,
    FileMessage,
    MessageBody,
    PictureMessage,
    RedPacketMessage,
    Reference,
    ShareMessage,
    TextMessage,
    VideoMessage,
)


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def is_text(self) -> bool:
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "TextSegment":
        return TextSegment("text", {"text": text})

    @staticmethod
    def at_user(dodo_id: str) -> "AtUserSegment":
        return AtUserSegment("at_user", {"dodo_id": dodo_id})

    # @staticmethod
    # def at_role(role_id: str) -> "AtRoleSegment":
    #     return AtRoleSegment("at_role", {"role_id": role_id})

    # @staticmethod
    # def at_all() -> "AtAllSegment":
    #     return AtAllSegment("at_all", {})

    @staticmethod
    def channel_link(channel_id: str) -> "ChannelLinkSegment":
        return ChannelLinkSegment("channel_link", {"channel_id": channel_id})

    @staticmethod
    def reference(message_id: str) -> "ReferenceSegment":
        return ReferenceSegment("reference", {"message_id": message_id})

    @staticmethod
    def picture(url: str, width: int, height: int, is_original: Optional[bool] = None):
        return PictureSegment(
            "picture",
            {
                "picture": PictureMessage(
                    url=url,
                    width=width,
                    height=height,
                    isOriginal=is_original,  # type: ignore
                )
            },
        )

    @staticmethod
    def video(
        url: str,
        cover_url: Optional[str] = None,
        duration: Optional[int] = None,
        size: Optional[int] = None,
    ):
        return VideoSegment(
            "video",
            {
                "video": VideoMessage(
                    url=url, coverUrl=cover_url, duration=duration, size=size
                )
            },
        )

    # @staticmethod
    # def share(jump_url: str):
    #     return ShareSegment(
    #         "share", {"share": ShareMessage.parse_obj({"jumpUrl": jump_url})}
    #     )

    # @staticmethod
    # def file(url: str, name: str, size: int):
    #     return FileSegment(
    #         "file", {"file": FileMessage(url=url, name=name, size=size)}
    #     )

    @staticmethod
    def card(
        components: Sequence[Component],
        theme: CardTheme = "default",
        title: Optional[str] = None,
    ):
        return CardSegment(
            "card",
            {
                "card": CardMessage(
                    card=Card(components=list(components), theme=theme, title=title)
                )
            },
        )

    # @staticmethod
    # def red_packet(
    #     type: RedPacketType,
    #     count: int,
    #     total_amount: float,
    #     receiver_type: ReceiverType,
    #     role_id_list: Optional[List[str]] = None,
    # ):
    #     return RedPacketSegment(
    #         "red_packet",
    #         {
    #             "red_packet": RedPacketMessage.parse_obj(
    #                 {
    #                     "type": type,
    #                     "count": count,
    #                     "totalAmount": total_amount,
    #                     "receiverType": receiver_type,
    #                     "roleIdList": role_id_list,
    #                 }
    #             )
    #         },
    #     )


class _TextData(TypedDict):
    text: str


@dataclass
class TextSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["text"]
        data: _TextData

    @override
    def __str__(self) -> str:
        return self.data["text"]


class _AtUserData(TypedDict):
    dodo_id: str


@dataclass
class AtUserSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["at_user"]
        data: _AtUserData

    @override
    def __str__(self) -> str:
        return f"<@!{self.data['dodo_id']}>"


class _AtRoleData(TypedDict):
    role_id: str


@dataclass
class AtRoleSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["at_role"]
        data: _AtRoleData

    @override
    def __str__(self) -> str:
        return f"<@&{self.data['role_id']}>"


@dataclass
class AtAllSegment(MessageSegment):
    @override
    def __str__(self) -> str:
        return "<@all>"


class _ChannelLinkData(TypedDict):
    channel_id: str


@dataclass
class ChannelLinkSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["channel_link"]
        data: _ChannelLinkData

    @override
    def __str__(self) -> str:
        return f"<#{self.data['channel_id']}>"


class _ReferenceData(TypedDict):
    message_id: str


@dataclass
class ReferenceSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["reference"]
        data: _ReferenceData

    @override
    def __str__(self) -> str:
        return f"<reference:{self.data['message_id']}>"


class _PictureData(TypedDict):
    picture: PictureMessage


@dataclass
class PictureSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["picture"]
        data: _PictureData

    @override
    def __str__(self) -> str:
        return f"<picture:{self.message_body.url}>"

    @property
    def message_body(self) -> PictureMessage:
        return self.data["picture"]


class _VideoData(TypedDict):
    video: VideoMessage


@dataclass
class VideoSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["video"]
        data: _VideoData

    @override
    def __str__(self) -> str:
        return f"<video:{self.message_body.url}>"

    @property
    def message_body(self) -> VideoMessage:
        return self.data["video"]


class _ShareData(TypedDict):
    share: ShareMessage


@dataclass
class ShareSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["share"]
        data: _ShareData

    @override
    def __str__(self) -> str:
        return f"<share:{self.message_body.jump_url}>"

    @property
    def message_body(self) -> ShareMessage:
        return self.data["share"]


class _FileData(TypedDict):
    file: FileMessage


@dataclass
class FileSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["file"]
        data: _FileData

    @override
    def __str__(self) -> str:
        return f"<share:{self.message_body.url}>"

    @property
    def message_body(self) -> FileMessage:
        return self.data["file"]


class _CardData(TypedDict):
    card: CardMessage


@dataclass
class CardSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["card"]
        data: _CardData

    @override
    def __str__(self) -> str:
        return f"<card:{self.message_body.card.title}>"

    @property
    def message_body(self) -> CardMessage:
        return self.data["card"]


class _RedPacketData(TypedDict):
    red_packet: RedPacketMessage


@dataclass
class RedPacketSegment(MessageSegment):
    if TYPE_CHECKING:
        type: Literal["red_packet"]
        data: _RedPacketData

    @override
    def __str__(self) -> str:
        return (
            f"<red_packet:{self.message_body.total_amount}/{self.message_body.count}>"
        )

    @property
    def message_body(self) -> RedPacketMessage:
        return self.data["red_packet"]


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        text_begin = 0
        for embed in re.finditer(
            r"\<(?P<type>(?:@!|@&|@|#))(?P<id>\w+?)\>",
            msg,
        ):
            content = msg[text_begin : embed.pos + embed.start()]
            if content:
                yield TextSegment("text", {"text": content})
            text_begin = embed.pos + embed.end()
            if embed["type"] == "@!":
                yield AtUserSegment("at_user", {"dodo_id": embed["id"]})
            elif embed["type"] == "@&":
                yield AtRoleSegment("at_role", {"role_id": embed["id"]})
            elif embed["type"] == "#":
                yield ChannelLinkSegment("channel_link", {"channel_id": embed["id"]})
            elif embed["type"] == "@" and embed["id"] == "all":
                yield AtAllSegment("at_all", {})
            else:
                yield TextSegment("text", {"text": f"<{embed['type']}{embed['id']}>"})
        content = msg[text_begin:]
        if content:
            yield TextSegment("text", {"text": content})

    @classmethod
    def from_message_body(
        cls, body: MessageBody, reference: Optional[Reference] = None
    ) -> Self:
        if isinstance(body, TextMessage):
            msg = cls(body.content)
        elif isinstance(body, PictureMessage):
            msg = cls(
                PictureSegment(
                    "picture",
                    {"picture": body},
                )
            )
        elif isinstance(body, VideoMessage):
            msg = cls(
                VideoSegment(
                    "video",
                    {"video": body},
                )
            )
        elif isinstance(body, ShareMessage):
            msg = cls(
                ShareSegment(
                    "share",
                    {"share": body},
                )
            )
        elif isinstance(body, FileMessage):
            msg = cls(
                FileSegment(
                    "file",
                    {"file": body},
                )
            )
        elif isinstance(body, CardMessage):
            msg = cls(
                CardSegment(
                    "card",
                    {"card": body},
                )
            )
        else:
            msg = cls(
                RedPacketSegment(
                    "red_packet",
                    {"red_packet": body},
                )
            )
        if reference:
            msg += ReferenceSegment("reference", {"message_id": reference.message_id})
        return msg

    def to_message_body(self) -> Tuple[MessageBody, Optional[str]]:
        ref = self["reference"] or None
        if ref:
            message_id = ref[-1].data["message_id"]
        else:
            message_id = None
        last_seg = self[-1]
        if isinstance(
            last_seg,
            (
                PictureSegment,
                VideoSegment,
                ShareSegment,
                FileSegment,
                CardSegment,
                RedPacketSegment,
            ),
        ):
            return last_seg.message_body, message_id
        if card := (self["card"] or None):
            return CardMessage(
                content=self.extract_text_content() or None, card=card[-1].data["card"]
            ), message_id
        return TextMessage(content=self.extract_text_content()), message_id

    def extract_text_content(self) -> str:
        return "".join(
            str(seg)
            for seg in self
            if isinstance(seg, (TextSegment, AtUserSegment, ChannelLinkSegment))
        )
