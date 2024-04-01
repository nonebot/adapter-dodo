from typing import Literal, overload

from nonebot.compat import PYDANTIC_V2

__all__ = ("model_validator", "field_validator", "GenericModel")

if PYDANTIC_V2:
    from pydantic import (
        BaseModel as GenericModel,
        field_validator as field_validator,
        model_validator as model_validator,
    )

else:
    from pydantic import root_validator, validator
    from pydantic.generics import GenericModel as GenericModel

    @overload
    def model_validator(*, mode: Literal["before"]): ...

    @overload
    def model_validator(*, mode: Literal["after"]): ...

    def model_validator(*, mode: Literal["before", "after"] = "after"):
        return root_validator(pre=mode == "before", allow_reuse=True)

    def field_validator(__field, *fields, mode: Literal["before", "after"] = "after"):
        return validator(__field, *fields, pre=mode == "before", allow_reuse=True)
