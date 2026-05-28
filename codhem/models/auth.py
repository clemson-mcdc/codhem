from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    name: str
    email: str
    role: str
    organization: str
    country: str
    position: str
    verified: bool
