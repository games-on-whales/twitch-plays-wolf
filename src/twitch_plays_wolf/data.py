from dataclasses import dataclass


@dataclass(frozen=True)
class MessageEvent:
    room: str
    user: str
    msg: str
