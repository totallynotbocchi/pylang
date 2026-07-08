from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()


class Token:
    def __init__(self, value: str, type: TokenType) -> None:
        self.value: str = value
        self.type: TokenType = type

    def __repr__(self) -> str:
        return f'Token {{ value="{self.value}", type="{str(self.type)}" }}'
