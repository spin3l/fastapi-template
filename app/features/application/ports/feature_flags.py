import typing

import pydantic


class FeatureFlagProvider(typing.Protocol):
    def get_value[T: pydantic.BaseModel | str | bool](
        self,
        feature_name: str,
        default: T,
    ) -> T: ...
