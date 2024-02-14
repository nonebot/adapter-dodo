from typing import Any, Dict, Literal, Optional, Set, overload

from nonebot.compat import PYDANTIC_V2

from pydantic import BaseModel

__all__ = ("model_validator", "field_validator")

if PYDANTIC_V2:
    from pydantic import (
        field_validator as field_validator,
        model_validator as model_validator,
    )

    def model_dump(
        model: BaseModel,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> Dict[str, Any]:
        return model.model_dump(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_none=exclude_none,
        )
else:
    from pydantic import root_validator, validator

    @overload
    def model_validator(*, mode: Literal["before"]):
        ...

    @overload
    def model_validator(*, mode: Literal["after"]):
        ...

    def model_validator(*, mode: Literal["before", "after"] = "after"):
        return root_validator(pre=mode == "before", allow_reuse=True)

    def field_validator(__field, *fields, mode: Literal["before", "after"] = "after"):
        return validator(__field, *fields, pre=mode == "before", allow_reuse=True)

    def model_dump(
        model: BaseModel,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> Dict[str, Any]:
        return model.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_none=exclude_none,
        )
