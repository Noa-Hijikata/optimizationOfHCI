from dataclasses import dataclass


@dataclass
class UserConfig:
    categoryOrder: list[str]
    buttonOrder: list[str]
    suggest: dict[str, list[str]]
