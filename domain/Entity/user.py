from dataclasses import dataclass
from userConfig import UserConfig


@dataclass
class User:
    id: str
    departmant: str
    config: UserConfig
