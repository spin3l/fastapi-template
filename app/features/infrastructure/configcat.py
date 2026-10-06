import dataclasses
import typing

import configcatclient
import pydantic
from configcatclient import configcatoptions, pollingmode
from configcatclient.configcatclient import ConfigCatClient

from app.features.application.ports.feature_flags import FeatureFlagProvider


def create_configcat_client(
    sdk: pydantic.SecretStr,
    poll_interval_seconds: int,
) -> typing.Iterator[ConfigCatClient]:
    client = configcatclient.get(
        sdk.get_secret_value(),
        configcatoptions.ConfigCatOptions(
            polling_mode=pollingmode.PollingMode.auto_poll(
                poll_interval_seconds=poll_interval_seconds,
            )
        ),
    )
    try:
        yield client
    finally:
        client.close()


@dataclasses.dataclass(frozen=True, slots=True)
class ConfigCatFeatureFlags(FeatureFlagProvider):
    client: ConfigCatClient

    @typing.override
    def get_value[T: pydantic.BaseModel | str | bool](
        self,
        feature_name: str,
        default: T,
    ) -> T:
        if isinstance(default, pydantic.BaseModel):
            raw = self.client.get_value(feature_name, default.model_dump_json())
            return typing.cast(T, type(default).model_validate_json(raw))

        return typing.cast(T, self.client.get_value(feature_name, default))
