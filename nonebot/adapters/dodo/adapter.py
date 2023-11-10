import asyncio
import json
from typing import Any, List, Optional
from typing_extensions import override

from nonebot.adapters import Adapter as BaseAdapter
from nonebot.drivers import (
    URL,
    Driver,
    HTTPClientMixin,
    Request,
    WebSocket,
    WebSocketClientMixin,
)
from nonebot.exception import WebSocketClosed
from nonebot.utils import escape_tag

from .bot import Bot
from .config import BotConfig, Config
from .event import EventSubject
from .exception import ApiNotAvailable
from .utils import API, log


class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.dodo_config = Config.parse_obj(self.config)
        self.api_base: URL = URL("https://botopen.imdodo.com/api/v2")
        self.tasks: List["asyncio.Task"] = []
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        return "DoDo"

    def setup(self) -> None:
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "http client requests! "
                "DoDo Adapter need a HTTPClient Driver to work."
            )
        if not isinstance(self.driver, WebSocketClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support "
                "websocket client! "
                "DoDo Adapter need a WebSocketClient Driver to work."
            )
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        for bot in self.dodo_config.bots:
            self.tasks.append(asyncio.create_task(self.run_bot(bot)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )

    async def run_bot(self, bot_info: BotConfig) -> None:
        bot = Bot(self, bot_info.client_id, bot_info)
        await bot.get_bot_info()
        try:
            ws_result = await bot.get_websocket_connection()
            ws_url = URL(ws_result.endpoint)
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Failed to get websocket url.</bg #f8bbd0></r>",
                e,
            )
            return

        self.tasks.append(asyncio.create_task(self._forward_ws(bot, ws_url)))

    async def _forward_ws(self, bot: Bot, ws_url: URL) -> None:
        request = Request("GET", ws_url, timeout=30.0)
        heartbeat_task: Optional["asyncio.Task"] = None
        while True:
            try:
                async with self.websocket(request) as ws:
                    log(
                        "DEBUG",
                        (
                            "WebSocket Connection to "
                            f"{escape_tag(str(ws_url))} established"
                        ),
                    )
                    try:
                        self.bot_connect(bot)
                        heartbeat_task = asyncio.create_task(self._heartbeat(ws))

                        await self._loop(bot, ws)
                    except WebSocketClosed as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>WebSocket Closed</bg #f8bbd0></r>",
                            e,
                        )
                    except Exception as e:
                        log(
                            "ERROR",
                            (
                                "<r><bg #f8bbd0>"
                                "Error while process data from websocket "
                                f"{escape_tag(str(ws_url))}. Trying to reconnect..."
                                "</bg #f8bbd0></r>"
                            ),
                            e,
                        )
                    finally:
                        if heartbeat_task:
                            heartbeat_task.cancel()
                            heartbeat_task = None
                        self.bot_disconnect(bot)
            except Exception as e:
                log(
                    "ERROR",
                    (
                        "<r><bg #f8bbd0>"
                        "Error while setup websocket to "
                        f"{escape_tag(str(ws_url))}. Trying to reconnect..."
                        "</bg #f8bbd0></r>"
                    ),
                    e,
                )
            await asyncio.sleep(5.0)

    async def _heartbeat(self, ws: WebSocket):
        """心跳"""
        while True:
            await asyncio.sleep(25.0)
            await ws.send(json.dumps({"type": 1}))
            log("TRACE", "Send Heartbeat")

    async def _loop(self, bot: Bot, ws: WebSocket):
        while True:
            payload = json.loads(await ws.receive())
            if payload["type"] == 1:
                log("TRACE", f"Receive Heartbeat: {payload}")
                continue
            try:
                event_subject = EventSubject.parse_obj(payload)
            except Exception as e:
                log(
                    "WARNING",
                    f"Failed to parse payload {payload}",
                    e,
                )
            else:
                asyncio.create_task(bot.handle_event(event_subject.data))

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Bot {bot.self_id} calling API <y>{api}</y>")
        api_handler: Optional[API] = getattr(bot.__class__, api, None)
        if api_handler is None:
            raise ApiNotAvailable
        return await api_handler(bot, **data)
