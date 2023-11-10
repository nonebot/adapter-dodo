from typing import Optional

from nonebot.exception import (
    ActionFailed as BaseActionFailed,
    AdapterException,
    ApiNotAvailable as BaseApiNotAvailable,
    NetworkError as BaseNetworkError,
    NoLogException as BaseNoLogException,
)


class DoDoAdapterException(AdapterException):
    def __init__(self):
        super().__init__("dodo")


class NoLogException(BaseNoLogException, DoDoAdapterException):
    pass


class ActionFailed(BaseActionFailed, DoDoAdapterException):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

    def __repr__(self) -> str:
        return f"<ActionFailed: {self.status}, {self.message}>"

    def __str__(self):
        return self.__repr__()


class UnauthorizedException(ActionFailed):
    pass


class RateLimitException(ActionFailed):
    pass


class NetworkError(BaseNetworkError, DoDoAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class ApiNotAvailable(BaseApiNotAvailable, DoDoAdapterException):
    pass
