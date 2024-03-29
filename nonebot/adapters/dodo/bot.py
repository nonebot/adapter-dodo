from io import BytesIO
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, NoReturn, Optional, Union
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot
from nonebot.compat import model_dump, type_validate_python
from nonebot.drivers import Request, Response
from nonebot.message import handle_event

from .config import BotConfig
from .event import ChannelMessageEvent, Event, PersonalMessageEvent
from .exception import (
    ActionFailed,
    NetworkError,
    RateLimitException,
    UnauthorizedException,
)
from .message import Message, MessageSegment
from .models import (
    ApiReturn,
    BotInfo,
    BotInviteInfo,
    BussinessType,
    ChannelArticleData,
    ChannelData,
    ChannelInfo,
    ChannelType,
    ChannelVoiceMemberStatusInfo,
    DoDoIDMapData,
    Emoji,
    GetMemberInvitationInfoReturn,
    GiftAccountInfo,
    GiftGrossValueInfo,
    GiftInfo,
    GiftMemberInfo,
    GiftShareRatioInfo,
    IntegralInfo,
    IslandInfo,
    IslandLevelRankInfo,
    IslandMuteOrBanData,
    ListResult,
    ManageOperateType,
    MemberInfo,
    MemberRoleInfo,
    MessageBody,
    MessageReactionInfo,
    MessageReactionMemberInfo,
    MessageReturn,
    MessageType,
    PictureInfo,
    RoleData,
    RoleInfo,
    RoleMemberInfo,
    TargetType,
    WebSocketConnectionData,
)
from .utils import API, exclude_none

if TYPE_CHECKING:
    from .adapter import Adapter


def _check_at_me(
    bot: "Bot",
    event: ChannelMessageEvent,
):
    def _is_at_me_seg(segment: MessageSegment) -> bool:
        return (
            bot.bot_info is not None
            and segment.type == "at_user"
            and segment.data["dodo_id"] == bot.bot_info.dodo_source_id
        )

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    if any(_is_at_me_seg(seg) for seg in message) or (
        event.get_message()["at_all"] or None
    ):
        event.to_me = True

    deleted = False
    if _is_at_me_seg(message[0]):
        message.pop(0)
        deleted = True
        event.to_me = True
        if message and message[0].type == "text":
            message[0].data["text"] = message[0].data["text"].lstrip("\xa0").lstrip()
            if not message[0].data["text"]:
                del message[0]

    if not deleted:
        # check the last segment
        i = -1
        last_msg_seg = message[i]
        if (
            last_msg_seg.type == "text"
            and not last_msg_seg.data["text"].strip()
            and len(message) >= 2
        ):
            i -= 1
            last_msg_seg = message[i]

        if _is_at_me_seg(last_msg_seg):
            deleted = True
            event.to_me = True
            del message[i:]

    if not message:
        message.append(MessageSegment.text(""))


class Bot(BaseBot):
    adapter: "Adapter"

    @override
    def __init__(self, adapter: "Adapter", self_id: str, bot_config: BotConfig):
        super().__init__(adapter, self_id)
        self.bot_config = bot_config
        self.bot_info: Optional[BotInfo] = None

    @override
    def __getattr__(self, name: str) -> NoReturn:
        raise AttributeError(
            f'"{self.__class__.__name__}" object has no attribute "{name}"'
        )

    async def send_to_channel(
        self,
        channel_id: str,
        message: Union[str, Message, MessageSegment],
    ) -> str:
        msg, referenced_message_id = Message(message).to_message_body()
        return (
            await self.set_channel_message_send(
                channel_id=channel_id,
                message_type=msg.__type__,
                message_body=msg,
                referenced_message_id=referenced_message_id,
            )
        ).message_id

    async def send_to_channel_personal(
        self,
        channel_id: str,
        message: Union[str, Message, MessageSegment],
        dodo_source_id: str,
    ) -> str:
        msg, referenced_message_id = Message(message).to_message_body()
        return (
            await self.set_channel_message_send(
                channel_id=channel_id,
                message_type=msg.__type__,
                message_body=msg,
                referenced_message_id=referenced_message_id,
                dodo_source_id=dodo_source_id,
            )
        ).message_id

    async def send_to_personal(
        self,
        island_source_id: str,
        dodo_source_id: str,
        message: Union[str, Message, MessageSegment],
    ) -> str:
        msg, _ = Message(message).to_message_body()
        return (
            await self.set_personal_message_send(
                island_source_id=island_source_id,
                dodo_source_id=dodo_source_id,
                message_type=msg.__type__,
                message_body=msg,
            )
        ).message_id

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        at_sender: bool = False,
        reply_message: bool = False,
    ) -> str:
        if isinstance(event, ChannelMessageEvent):
            message = Message(message)
            if at_sender:
                message.insert(0, MessageSegment.at_user(event.dodo_source_id))
            if reply_message:
                message.insert(0, MessageSegment.reference(event.message_id))
            return await self.send_to_channel(event.channel_id, message)
        if isinstance(event, PersonalMessageEvent):
            if not event.island_source_id:
                raise RuntimeError("Event cannot be replied to!")
            return await self.send_to_personal(
                event.island_source_id, event.dodo_source_id, message
            )
        raise RuntimeError("Event cannot be replied to!")

    def _handle_response(self, response: Response) -> Any:
        if response.content and (
            result := type_validate_python(ApiReturn, json.loads(response.content))
        ):
            if result.status == 0:
                return result.data
            if result.status == 10005:
                raise UnauthorizedException(result.status, result.message)
            if result.status in (10082, 10083):
                raise RateLimitException(result.status, result.message)
            raise ActionFailed(result.status, result.message)
        raise NetworkError("API request error when parsing response")

    async def _request(self, request: Request) -> Any:
        request.headers.update(
            {
                "Authorization": f"Bot {self.self_id}.{self.bot_config.token}",
            }
        )

        try:
            response = await self.adapter.request(request)
        except Exception as e:
            raise NetworkError("API request error") from e

        return self._handle_response(response)

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, ChannelMessageEvent):
            _check_at_me(self, event)
        await handle_event(self, event)

    @API
    async def get_bot_info(self) -> BotInfo:
        request = Request("POST", self.adapter.api_base / "bot/info")
        bot_info = type_validate_python(BotInfo, await self._request(request))
        self.bot_info = bot_info
        return bot_info

    @API
    async def set_bot_island_leave(self, *, island_source_id: str) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "bot/island/leave",
            json={"islandSourceId": island_source_id},
        )
        await self._request(request)

    @API
    async def get_bot_invite_list(
        self, *, page_size: int, max_id: int = 0
    ) -> ListResult[BotInviteInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "bot/invite/list",
            json={"pageSize": page_size, "maxId": max_id},
        )
        return type_validate_python(
            ListResult[BotInviteInfo], await self._request(request)
        )

    @API
    async def set_bot_invite_add(self, *, dodo_source_id: str) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "bot/invite/add",
            json={"dodoSourceId": dodo_source_id},
        )
        await self._request(request)

    @API
    async def set_bot_invite_remove(self, *, dodo_source_id: str) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "bot/invite/remove",
            json={"dodoSourceId": dodo_source_id},
        )
        await self._request(request)

    @API
    async def get_island_list(self) -> List[IslandInfo]:
        request = Request("POST", self.adapter.api_base / "island/list")
        return type_validate_python(List[IslandInfo], await self._request(request))

    @API
    async def get_island_info(self, *, island_source_id: str) -> IslandInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "island/info",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(IslandInfo, await self._request(request))

    @API
    async def get_island_level_rank_list(
        self, *, island_source_id: str
    ) -> List[IslandLevelRankInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "island/level/rank/list",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(
            List[IslandLevelRankInfo], await self._request(request)
        )

    @API
    async def get_island_mute_list(
        self, *, island_source_id: str, page_size: int, max_id: int = 0
    ) -> ListResult[IslandMuteOrBanData]:
        request = Request(
            "POST",
            self.adapter.api_base / "island/mute/list",
            json={
                "islandSourceId": island_source_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[IslandMuteOrBanData], await self._request(request)
        )

    @API
    async def get_island_ban_list(
        self, *, island_source_id: str, page_size: int, max_id: int = 0
    ) -> ListResult[IslandMuteOrBanData]:
        request = Request(
            "POST",
            self.adapter.api_base / "island/ban/list",
            json={
                "islandSourceId": island_source_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[IslandMuteOrBanData], await self._request(request)
        )

    @API
    async def get_channel_list(self, *, island_source_id: str) -> List[ChannelInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/list",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(List[ChannelInfo], await self._request(request))

    @API
    async def get_channel_info(self, *, channel_id: str) -> ChannelInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/info",
            json={"channelId": channel_id},
        )
        return type_validate_python(ChannelInfo, await self._request(request))

    @API
    async def set_channel_add(
        self,
        *,
        island_source_id: str,
        channel_type: ChannelType,
        channel_name: Optional[str] = None,
    ) -> ChannelData:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/add",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "channelType": channel_type,
                    "channelName": channel_name,
                }
            ),
        )
        return type_validate_python(ChannelData, await self._request(request))

    @API
    async def set_channel_edit(
        self,
        *,
        island_source_id: str,
        channel_id: str,
        channel_name: Optional[str] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/edit",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "channelId": channel_id,
                    "channelName": channel_name,
                }
            ),
        )
        await self._request(request)

    @API
    async def set_channel_remove(
        self,
        *,
        island_source_id: str,
        channel_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/remove",
            json={"islandSourceId": island_source_id, "channelId": channel_id},
        )
        await self._request(request)

    @API
    async def set_channel_message_send(
        self,
        *,
        channel_id: str,
        message_type: MessageType,
        message_body: MessageBody,
        referenced_message_id: Optional[str] = None,
        dodo_source_id: Optional[str] = None,
    ) -> MessageReturn:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/send",
            json=exclude_none(
                {
                    "channelId": channel_id,
                    "messageType": message_type,
                    "messageBody": model_dump(
                        message_body, by_alias=True, exclude_none=True
                    ),
                    "referencedMessageId": referenced_message_id,
                    "dodoSourceId": dodo_source_id,
                }
            ),
        )
        return type_validate_python(MessageReturn, await self._request(request))

    @API
    async def set_channel_message_edit(
        self, *, message_id: str, message_body: MessageBody
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/edit",
            json={
                "messageId": message_id,
                "messageBody": model_dump(
                    message_body, by_alias=True, exclude_none=True
                ),
            },
        )
        await self._request(request)

    @API
    async def set_channel_message_withdraw(
        self, *, message_id: str, reason: Optional[str] = None
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/withdraw",
            json=exclude_none({"messageId": message_id, "reason": reason}),
        )
        await self._request(request)

    @API
    async def set_channel_message_top(
        self, *, message_id: str, is_cancel: bool = False
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/top",
            json={"messageId": message_id, "operateType": int(not is_cancel)},
        )
        await self._request(request)

    @API
    async def get_channel_message_reaction_list(
        self, *, message_id: str
    ) -> List[MessageReactionInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/reaction/list",
            json={"messageId": message_id},
        )
        return type_validate_python(
            List[MessageReactionInfo], await self._request(request)
        )

    @API
    async def get_channel_message_reaction_member_list(
        self, *, message_id: str, emoji: Emoji, page_size: int, max_id: int = 0
    ) -> ListResult[MessageReactionMemberInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/reaction/member/list",
            json={
                "messageId": message_id,
                "emoji": model_dump(emoji),
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[MessageReactionMemberInfo], await self._request(request)
        )

    @API
    async def set_channel_message_reaction_add(
        self, *, message_id: str, emoji: Emoji
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/reaction/add",
            json={"messageId": message_id, "emoji": model_dump(emoji)},
        )
        await self._request(request)

    @API
    async def set_channel_message_reaction_remove(
        self, *, message_id: str, emoji: Emoji, dodo_source_id: Optional[str] = None
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/message/reaction/remove",
            json=exclude_none(
                {
                    "messageId": message_id,
                    "emoji": model_dump(emoji),
                    "dodoSourceId": dodo_source_id,
                }
            ),
        )
        await self._request(request)

    @API
    async def get_channel_voice_member_status(
        self, *, island_source_id: str, dodo_source_id: str
    ) -> ChannelVoiceMemberStatusInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/voice/member/status",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
            },
        )
        return type_validate_python(
            ChannelVoiceMemberStatusInfo, await self._request(request)
        )

    @API
    async def set_channel_voice_member_move(
        self, *, island_source_id: str, dodo_source_id: str, channel_id: str
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/voice/member/move",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "channelId": channel_id,
            },
        )
        await self._request(request)

    @API
    async def set_channel_voice_member_edit(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        operate_type: ManageOperateType,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/voice/member/edit",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "operateType": operate_type,
            },
        )
        await self._request(request)

    @API
    async def set_channel_article_add(
        self,
        *,
        channel_id: str,
        titile: str,
        content: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> ChannelArticleData:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/article/add",
            json=exclude_none(
                {
                    "channelId": channel_id,
                    "titile": titile,
                    "content": content,
                    "imageUrl": image_url,
                }
            ),
        )
        return type_validate_python(ChannelArticleData, await self._request(request))

    @API
    async def set_channel_article_remove(
        self, *, channel_id: str, type: BussinessType, id: str
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "channel/article/remove",
            json={"channelId": channel_id, "type": type, "id": id},
        )
        await self._request(request)

    @API
    async def get_role_list(self, *, island_source_id: str) -> List[RoleInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "role/list",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(List[RoleInfo], await self._request(request))

    @API
    async def set_role_add(
        self,
        *,
        island_source_id: str,
        role_name: Optional[str] = None,
        role_color: Optional[str] = None,
        position: Optional[int] = None,
        permission: Optional[str] = None,
    ) -> RoleData:
        request = Request(
            "POST",
            self.adapter.api_base / "role/add",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "roleName": role_name,
                    "roleColor": role_color,
                    "position": position,
                    "permission": permission,
                }
            ),
        )
        return type_validate_python(RoleData, await self._request(request))

    @API
    async def set_role_edit(
        self,
        *,
        island_source_id: str,
        role_id: str,
        role_name: Optional[str] = None,
        role_color: Optional[str] = None,
        position: Optional[int] = None,
        permission: Optional[str] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "role/edit",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "roleId": role_id,
                    "roleName": role_name,
                    "roleColor": role_color,
                    "position": position,
                    "permission": permission,
                }
            ),
        )
        await self._request(request)

    @API
    async def set_role_remove(
        self,
        *,
        island_source_id: str,
        role_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "role/remove",
            json={
                "islandSourceId": island_source_id,
                "roleId": role_id,
            },
        )
        await self._request(request)

    @API
    async def get_role_member_list(
        self, *, island_source_id: str, role_id: str, page_size: int, max_id: int = 0
    ) -> ListResult[RoleMemberInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "role/member/list",
            json={
                "islandSourceId": island_source_id,
                "roleId": role_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[RoleMemberInfo], await self._request(request)
        )

    @API
    async def set_role_member_add(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        role_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "role/member/add",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "roleId": role_id,
            },
        )
        await self._request(request)

    @API
    async def set_role_member_remove(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        role_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "role/member/remove",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "roleId": role_id,
            },
        )
        await self._request(request)

    @API
    async def get_member_list(
        self, *, island_source_id: str, page_size: int, max_id: int = 0
    ) -> ListResult[MemberInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "member/list",
            json={
                "islandSourceId": island_source_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[MemberInfo], await self._request(request)
        )

    @API
    async def get_member_info(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> MemberInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "member/info",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
            },
        )
        return type_validate_python(MemberInfo, await self._request(request))

    @API
    async def get_member_role_list(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> List[MemberRoleInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "member/role/list",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
            },
        )
        return type_validate_python(List[MemberRoleInfo], await self._request(request))

    @API
    async def get_member_invitation_info(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> GetMemberInvitationInfoReturn:
        request = Request(
            "POST",
            self.adapter.api_base / "member/invitation/info",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
            },
        )
        return type_validate_python(
            GetMemberInvitationInfoReturn, await self._request(request)
        )

    @API
    async def get_member_dodo_id_map_list(
        self, *, dodo_id_list: List[str]
    ) -> List[DoDoIDMapData]:
        request = Request(
            "POST",
            self.adapter.api_base / "member/dodoid/map/list",
            json={"dodoIdList": dodo_id_list},
        )
        return type_validate_python(List[DoDoIDMapData], await self._request(request))

    @API
    async def set_member_nick_name_edit(
        self, *, island_source_id: str, dodo_source_id: str, nick_name: str
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "member/nickname/edit",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "nickName": nick_name,
            },
        )
        await self._request(request)

    @API
    async def set_member_mute_add(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        duration: int,
        reason: Optional[str] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "member/mute/add",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "dodoSourceId": dodo_source_id,
                    "duration": duration,
                    "reason": reason,
                }
            ),
        )
        await self._request(request)

    @API
    async def set_member_mute_remove(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "member/mute/remove",
            json={"islandSourceId": island_source_id, "dodoSourceId": dodo_source_id},
        )
        await self._request(request)

    @API
    async def set_member_ban_add(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        notice_channel_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "member/ban/add",
            json=exclude_none(
                {
                    "islandSourceId": island_source_id,
                    "dodoSourceId": dodo_source_id,
                    "noticeChannelId": notice_channel_id,
                    "reason": reason,
                }
            ),
        )
        await self._request(request)

    @API
    async def set_member_ban_remove(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> None:
        request = Request(
            "POST",
            self.adapter.api_base / "member/ban/remove",
            json={"islandSourceId": island_source_id, "dodoSourceId": dodo_source_id},
        )
        await self._request(request)

    @API
    async def get_gift_account(
        self,
        *,
        island_source_id: str,
    ) -> GiftAccountInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "gift/account/info",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(GiftAccountInfo, await self._request(request))

    @API
    async def get_gift_share_ratio_info(
        self,
        *,
        island_source_id: str,
    ) -> GiftShareRatioInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "gift/share/ratio/info",
            json={"islandSourceId": island_source_id},
        )
        return type_validate_python(GiftShareRatioInfo, await self._request(request))

    @API
    async def get_gift_list(
        self, *, target_type: TargetType, target_id: str
    ) -> List[GiftInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "gift/list",
            json={"targetType": target_type, "targetId": target_id},
        )
        return type_validate_python(List[GiftInfo], await self._request(request))

    @API
    async def get_gift_member_list(
        self,
        *,
        target_type: TargetType,
        target_id: str,
        gift_id: str,
        page_size: int,
        max_id: int = 0,
    ) -> ListResult[GiftMemberInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "gift/member/list",
            json={
                "targetType": target_type,
                "targetId": target_id,
                "giftId": gift_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[GiftMemberInfo], await self._request(request)
        )

    @API
    async def get_gift_gross_value_list(
        self,
        *,
        target_type: TargetType,
        target_id: str,
        page_size: int,
        max_id: int = 0,
    ) -> ListResult[GiftGrossValueInfo]:
        request = Request(
            "POST",
            self.adapter.api_base / "gift/gross/value/list",
            json={
                "targetType": target_type,
                "targetId": target_id,
                "pageSize": page_size,
                "maxId": max_id,
            },
        )
        return type_validate_python(
            ListResult[GiftGrossValueInfo], await self._request(request)
        )

    @API
    async def get_integral_info(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
    ) -> IntegralInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "integral/info",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
            },
        )
        return type_validate_python(IntegralInfo, await self._request(request))

    @API
    async def set_integral_edit(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        integral: int,
        is_add: bool = True,
    ) -> IntegralInfo:
        request = Request(
            "POST",
            self.adapter.api_base / "integral/edit",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "integral": integral,
                "operateType": 1 if is_add else 2,
            },
        )
        return type_validate_python(IntegralInfo, await self._request(request))

    @API
    async def set_personal_message_send(
        self,
        *,
        island_source_id: str,
        dodo_source_id: str,
        message_type: MessageType,
        message_body: MessageBody,
    ) -> MessageReturn:
        request = Request(
            "POST",
            self.adapter.api_base / "personal/message/send",
            json={
                "islandSourceId": island_source_id,
                "dodoSourceId": dodo_source_id,
                "messageType": message_type,
                "messageBody": model_dump(
                    message_body, by_alias=True, exclude_none=True
                ),
            },
        )
        return type_validate_python(MessageReturn, await self._request(request))

    @API
    async def set_resouce_picture_upload(
        self, *, file: Union[bytes, BytesIO, Path], file_name: Optional[str] = None
    ) -> PictureInfo:
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        request = Request(
            "POST",
            self.adapter.api_base / "resource/picture/upload",
            files={"file": (file_name or "image.png", file, "multipart/form-data")},
        )
        return type_validate_python(PictureInfo, await self._request(request))

    @API
    async def get_websocket_connection(self) -> WebSocketConnectionData:
        request = Request("POST", self.adapter.api_base / "websocket/connection")
        return type_validate_python(
            WebSocketConnectionData, await self._request(request)
        )
