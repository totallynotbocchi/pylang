import logging

from src.node import BinaryExpr, Expr, NumberExpr, Program, Stmt, VariableExpr
from src.token import Token, TokenType

logging.basicConfig(level=logging.DEBUG)


class Parser:
    def __init__(self, tokens: list[Token] = []) -> None:
        self.tree: Program = Program(Stmt())
        self.tokens: list[Token] = tokens
        self.pos: int = 0

    # look at the next token in the stream
    def peek(self, n: int = 1) -> Token | None:
        if self.pos + n >= len(self.tokens):
            return None

        return self.tokens[self.pos + n]

    # move the pointer
    def advance(self, n: int = 1) -> None:
        self.pos += n
        logging.info(f"Advancing from {self.pos - n} to {self.pos}")

    # get the current token
    def current(self) -> Token | None:
        if self.pos >= len(self.tokens):
            return None

        return self.tokens[self.pos]

    def handle_primary(self) -> Expr | None:
        prim: Token | None = self.current()

        if prim is None:
            return None

        match prim.type:
            case TokenType.NUMBER:
                self.advance()
                return NumberExpr(value=prim.value)

            case TokenType.IDENTF:
                self.advance()
                return VariableExpr(name=prim.value)

            # if its "(" expr ")"
            case TokenType.LPAREN:
                self.advance()  # eat "("
                expr = self.handle_expr()

                current = self.current()
                if current is None or current.type != TokenType.RPAREN:
                    raise Exception("Invalid")

                self.advance()  # eat ")"
                return expr

        # by this point, its not a primary
        return None

    def handle_mult(self) -> Expr | None:
        # check if the current value is a term/factor (like a in a * b)
        left_expr = self.handle_primary()
        if left_expr is None:
            return None

        right_expr: Expr | None = None  # the next hypothetical term of a * b

        # get the new token
        current = self.current()

        # parse until we run out of multiplication symbols
        while current is not None and current.type is TokenType.TIMES:
            self.advance()  # consume *
            right_expr = self.handle_primary()

            # theres no right, but one is expected, because we have:
            # "left_expr * [HERE]""
            if right_expr is None:
                raise Exception("Invalid")

            # do left associativity
            # a * b = (a*b)
            # a * b * c = (a*b)*c
            left_expr = BinaryExpr(left=left_expr, right=right_expr, op=TokenType.TIMES)
            right_expr = None

            current = self.current()

        # return the operation
        return left_expr

    def handle_addition(self) -> Expr | None:
        # check if left is something like a * b in a*b+c
        left_expr = self.handle_mult()
        if left_expr is None:
            return None

        right_expr: Expr | None = None

        # get the new token
        current = self.current()

        # parse until we run out of multiplication symbols
        while current is not None and current.type is TokenType.PLUS:
            self.advance()  # consume +
            right_expr = self.handle_mult()

            # theres no right, but one is expected, because we have:
            # "left_expr + [HERE]""
            if right_expr is None:
                raise Exception("Invalid")

            # do left associativity
            # a + b = (a+b)
            # a + b + c = (a+b)+c
            left_expr = BinaryExpr(left=left_expr, right=right_expr, op=TokenType.PLUS)
            right_expr = None

            current = self.current()

        # return the operation
        # it automatically falls back to sub operations in the hierarchy:
        # addition:
        # -> multiplication
        # --> factor/term
        return left_expr

    def handle_expr(self) -> Expr | None:
        return self.handle_addition()

    # return the parsed tree
    def get_ast(self) -> Program:
        mult = self.handle_expr()

        if mult is not None:
            self.tree.root = mult  # type: ignore

        return self.tree
