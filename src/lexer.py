import logging

from ansimarkup import parse

from src.token import Token, TokenType

logging.basicConfig(level=logging.DEBUG)

SINGLE_CHAR_SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.DIV,
    "=": TokenType.EQUAL,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ";": TokenType.SEMICOL,
}

DOUBLE_CHAR_SYMBOLS = {
    "+=": TokenType.PLUS_EQUAL,
    "-=": TokenType.MINUS_EQUAL,
    "*=": TokenType.TIMES_EQUAL,
    "/=": TokenType.DIV_EQUAL,
    "==": TokenType.DOUBLE_EQUAL,
}

KEYWORDS = {
    "if": TokenType.KW_IF,
    "elsif": TokenType.KW_ELSIF,
    "then": TokenType.KW_THEN,
    "end": TokenType.KW_END,
    "let": TokenType.KW_LET,
}


class LexerError(Exception):
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

    # handle the lexing case of (positive) numbers
    # WARN: this function stSYMBOLS at the first non digit
    #
    # example:
    # "1"234
    # 1"2"34
    # 12"3"4
    # 123"4"
    # 1234" "  <- STOP
    def handle_number(self) -> Token | None:
        char = self.current()

        # return if there are no valid characters
        if char is None or not char.isdecimal():
            return None

        whole_number: list[str] = []
        used_float_point = False

        # loop continously until theres no numeric value, no dot for floats
        # or no characters
        while char is not None and (char.isdigit() or char == "."):
            # stop on "." if we alr have a floating point number
            if used_float_point and char == ".":
                break
            # set the floating point dot so it wont allow for "2.2.2" later
            if char == ".":
                used_float_point = True

            # append to the number being built
            whole_number.append(char)

            # move forward
            self.advance()

            # get the new current character
            char = self.current()

        # build token
        tok = Token(value="".join(whole_number), type=TokenType.NUMBER)
        return tok

    def handle_operator(self) -> Token | None:
        char = self.current()  # first character of an operator

        # skip if end
        if char is None:
            return None

        next_char = self.peek() or ""  # second character of the operator

        # combined substring
        op: str = char + next_char

        # check for double SYMBOLS like +=, == first
        toktype = DOUBLE_CHAR_SYMBOLS.get(op)
        if toktype is not None:
            self.advance(2)  # eat the two numbers
            tok = Token(value=op, type=toktype)
            return tok

        # check for single SYMBOLS (on char, not on op anymore)
        toktype = SINGLE_CHAR_SYMBOLS.get(char)
        if toktype is not None:
            self.advance()
            tok = Token(value=char, type=toktype)
            return tok

        return None

    def handle_identf_or_keyword(self) -> Token | None:
        char = self.current()

        if char is None or not char.isidentifier():
            return None

        identf: list[str] = []
        while char is not None and char.isidentifier():
            identf.append(char)

            self.advance()

            char = self.current()

        # build the string
        identf_str: str = "".join(identf)

        # handle keywords
        keyword_type = KEYWORDS.get(identf_str)
        if keyword_type is not None:
            tok = Token(value=identf_str, type=keyword_type)
            return tok

        # return the identifier we made
        tok = Token(value=identf_str, type=TokenType.IDENTF)
        return tok

    # the "main" function of the lexer
    def get_tokens(self) -> list[Token]:
        logging.info(parse(f"Lexing code:\n<i>\n{self.source}\n</i>"))

        tokens: list[Token] = []

        while not self.is_oob():
            # skip whitespaces
            if self.current().isspace():  # type: ignore
                self.advance()
                continue

            # try all the different possible cases,
            # all of the functions return a token if they match, or None if they dont
            tests = [
                self.handle_number,
                self.handle_operator,
                self.handle_identf_or_keyword,
            ]
            succeeded = False

            for test in tests:
                possible_token: Token | None = test()

                if possible_token is None:
                    continue

                # found token
                tokens.append(possible_token)
                succeeded = True
                break

            if not succeeded:
                self.add_error(
                    LexerError(
                        f'Unknown token "{self.current()}" at position {self.pos}'
                    )
                )
                self.advance()

        # return all collected tokens
        tokens.append(Token(value="\0", type=TokenType.EOF))
        return tokens
