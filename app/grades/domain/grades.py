import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class Grade:
    subject: str
    value: int


@dataclasses.dataclass(frozen=True, slots=True)
class GradePage:
    results: list[Grade]
