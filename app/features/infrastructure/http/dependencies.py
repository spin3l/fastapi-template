import collections.abc
import typing

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from app.di import Container
from app.features.application.ports.feature_flags import FeatureFlagProvider
from app.features.domain.constants import Features
from app.features.domain.exceptions import UnavailableFeatureError


@inject
async def get_feature_flags(
    feature_flags: typing.Annotated[FeatureFlagProvider, Depends(Provide[Container.feature_flags])],
) -> FeatureFlagProvider:
    return feature_flags


FeatureFlagsDep = typing.Annotated[FeatureFlagProvider, Depends(get_feature_flags)]


def require_feature(feature: Features) -> collections.abc.Callable[..., typing.Awaitable[None]]:
    async def dependency(feature_flags: FeatureFlagsDep) -> None:
        if not feature_flags.get_value(feature, False):
            raise UnavailableFeatureError(feature)

    return dependency
