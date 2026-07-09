from enum import Enum, auto, unique


@unique
class TokenType(Enum):
    EOF = auto()
    SEMICOL = auto()

    NUMBER = auto()
    IDENTF = auto()

    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIV = auto()

    EQUAL = auto()
    DOUBLE_EQUAL = auto()
    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()
    TIMES_EQUAL = auto()
    DIV_EQUAL = auto()

    LPAREN = auto()
    RPAREN = auto()

    KW_IF = auto()
    KW_ELSIF = auto()
    KW_THEN = auto()
    KW_END = auto()
    KW_LET = auto()


class Token:
    def __init__(self, value: str, type: TokenType) -> None:
        self.value: str = value
        self.type: TokenType = type

    def __repr__(self) -> str:
        return f'Token {{ value="{self.value}", type="{str(self.type)}" }}'
