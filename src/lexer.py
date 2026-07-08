from ansimarkup import parse

from src.token import Token, TokenType


class LexerError:
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __repr__(self) -> str:
        return parse(f"<red>Lexer Error</red>: {self.message}")


class Lexer:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.pos: int = 0

        self.errors: list[LexerError] = []

    def add_error(self, error: LexerError) -> None:
        self.errors.append(error)

    # return true if the position goes beyond what the source code actually is
    def is_oob(self) -> bool:
        return self.pos >= len(self.source)

    # look at the next character
    # n: how many character forward to peek
    def peek(self, n: int = 1) -> str | None:
        # return nothing if its out of bounds
        if self.pos + n >= len(self.source):
            return None

        return self.source[self.pos + n]

    # return the current character
    def current(self) -> str | None:
        if self.is_oob():
            return None

        char = self.source[self.pos]
        return char

    # advance a set number of times in the source
    def advance(self, times: int = 1) -> None:
        self.pos += times

    # handle the lexing case of numbers
    # WARN: this function stops at the first non digit
    #
    # example:
    # "1"234
    # 1"2"34
    # 12"3"4
    # 123"4"
    # 1234" "  <- STOP
    def handle_number(self) -> Token | None:
        char = self.current()

        # return if there are no characters
        if char is None or not char.isdigit():
            return None

        whole_number: list[str] = []
        used_floating_point = False

        # loop continously until theres no numeric value
        while char.isdigit() or char == ".":
            # stop on "." if we already have a floating point number
            if used_floating_point and char == ".":
                break
            elif not used_floating_point and char == ".":
                used_floating_point = True

            # append to the number being built
            whole_number.append(char)

            # move forward
            self.advance()

            # get the new current character
            char = self.current()
            if char is None:  # stop if we ran out of characters now
                break

        # build token
        tok = Token(value="".join(whole_number), type=TokenType.NUMBER)
        return tok

    # the "main" function of the lexer
    def get_tokens(self) -> list[Token]:
        tokens: list[Token] = []

        while not self.is_oob():
            # skip whitespaces
            if self.current().isspace():  # type: ignore
                self.advance()
                continue

            # handle numbers
            tok = self.handle_number()
            if tok is not None:
                tokens.append(tok)
                continue

            self.add_error(
                LexerError(f'Unknown token "{self.current()}" at position {self.pos}')
            )
            self.advance()

        return tokens
