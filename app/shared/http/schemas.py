import pydantic
import pydantic.alias_generators


class BaseSchema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        populate_by_name=True,
        alias_generator=pydantic.alias_generators.to_camel,
    )
