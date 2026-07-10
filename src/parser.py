import logging

from ansimarkup import parse

from src.node import (
    BinaryExpr,
    Expr,
    ExprStmt,
    IfStmt,
    NumberExpr,
    Program,
    Stmt,
    UnaryExpr,
    VarDeclStmt,
    VariableExpr,
)
from src.token import Token, TokenType

logging.basicConfig(level=logging.DEBUG)

UNARY_SYMBOLS = [
    TokenType.PLUS,
    TokenType.MINUS,
]

ADDITION_SYMBOLS = [
    TokenType.PLUS,
    TokenType.MINUS,
]

MULTIPLICATIN_SYMBOLS = [
    TokenType.PLUS,
    TokenType.MINUS,
]


class SyntaxError(Exception):
    def __init__(self, message: str, line: int) -> None:
        self.line = line
        self.message: str = message
        super().__init__(message)

    def __str__(self) -> str:
        return parse(
            f"Parsing error at line {self.line}:\n<red>Syntax Error</red>: {self.message}"
        )


class Parser:
    def __init__(self, tokens: list[Token] = []) -> None:
        self.tokens: list[Token] = tokens
        self.pos: int = 0

        self.tree: Program = Program()

        self.errors: list[SyntaxError] = []

    def is_at_end(self) -> bool:
        return (
            self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF
        )

    def add_error(self, error: SyntaxError) -> None:
        self.errors.append(error)

    def get_current_line(self) -> int:
        current = self.current()

        line = -1
        if current is not None:
            line = current.line

        return line

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

    # handle basic types, like variable, number or etc. also handles
    # parentheses
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

                # if theres no ")" after the entire expression
                current = self.current()
                if current is None or current.type != TokenType.RPAREN:
                    raise SyntaxError(
                        'Missing closing ")" after expression',
                        self.get_current_line(),
                    )

                self.advance()  # eat ")"
                return expr

        # by this point, its not a primary

    # handle unary expressions, like -x,--x
    def handle_unary(self) -> Expr | None:
        symbol = self.current()
        if symbol is None:
            return None

        # check if its an unary symbol
        if symbol.type in UNARY_SYMBOLS:
            self.advance()  # eat the symbol, like -

            # check for nests
            expr = self.handle_unary()

            if expr is None:
                # syntax error, "- <nothing>"?

                raise SyntaxError(
                    "Missing expression after unary minus.", self.get_current_line()
                )

            unary = UnaryExpr(value=expr, op=symbol.type)
            return unary

        return self.handle_primary()

    # handle multiplication expressions
    def handle_mult(self) -> Expr | None:
        # check if the current value is a term/factor (like a in a * b)
        left_expr = self.handle_unary()
        if left_expr is None:
            return None

        right_expr: Expr | None = None  # the next hypothetical term of a * b

        # get the new token
        current = self.current()

        # parse until we run out of multiplication symbols
        op: TokenType = TokenType.TIMES
        while current is not None and current.type is MULTIPLICATIN_SYMBOLS:
            if current.type in MULTIPLICATIN_SYMBOLS:
                op = current.type  # store the operator
                self.advance()  # consume *

            right_expr = self.handle_unary()

            # theres no right, but one is expected, because we have:
            # "left_expr * [HERE]""
            if right_expr is None:
                raise SyntaxError(
                    "Missing right side of multiplication", self.get_current_line()
                )

            # do left associativity
            # a * b = (a*b)
            # a * b * c = (a*b)*c
            left_expr = BinaryExpr(left=left_expr, right=right_expr, op=op)
            right_expr = None

            current = self.current()

        # return the operation
        return left_expr

    # handle addition expressions
    def handle_addition(self) -> Expr | None:
        # check if left is something like a * b in a*b+c
        left_expr = self.handle_mult()
        if left_expr is None:
            return None

        right_expr: Expr | None = None

        # get the new token
        current = self.current()

        # parse until we run out of addition symbols
        op: TokenType = TokenType.PLUS
        while current is not None and current.type in ADDITION_SYMBOLS:
            # dont consume -
            if current.type in ADDITION_SYMBOLS:
                op = current.type  # store the operator
                self.advance()  # consume the symbol

            right_expr = self.handle_mult()

            # theres no right, but one is expected, because we have:
            # "left_expr + [HERE]""
            if right_expr is None:
                raise SyntaxError(
                    "Missing right side of addition", self.get_current_line()
                )

            # do left associativity
            # a + b = (a+b)
            # a + b + c = (a+b)+c
            left_expr = BinaryExpr(left=left_expr, right=right_expr, op=op)
            right_expr = None

            current = self.current()

        # return the operation
        # it automatically falls back to sub operations in the hierarchy:
        # addition:
        # -> multiplication
        # --> factor/term
        return left_expr

    # handle expressions that evaluate to something
    def handle_expr(self) -> Expr | None:
        return self.handle_addition()

    # handle if conditions, looks like:
    #   if <expr> then <blocks>* end
    def handle_if(self) -> IfStmt | None:
        logging.info("Trying if statement")

        # get the current token
        current = self.current()
        if current is None:
            return None

        # not even an "if" statement if theres no "if"
        if current.type is not TokenType.KW_IF:
            return None

        # we should have an if statement, so eat this keyword
        self.advance()

        # next should be an expression for the condition,
        # if it isnt, this is invalid syntax
        expr = self.handle_expr()
        if expr is None:
            self.add_error(
                SyntaxError(
                    'Expected boolean expression after "if"', self.get_current_line()
                )
            )
            return None

        # check for "then", notice "handle_expr" leaves us at the next token after the expr
        next_token = self.current()

        # if there isnt any "then", thats a syntax error
        if next_token is None or next_token.type is not TokenType.KW_THEN:
            raise SyntaxError(
                'Expected "then" after expression', self.get_current_line()
            )

        # eat "then" and get the blocks until there is "end"
        self.advance()
        current = self.current()

        main_branch: list[Expr | Stmt] = []
        while (
            current is not None
            and current.type is not TokenType.KW_END
            and current.type is not TokenType.EOF
        ):
            # handle nested statements
            nested_stmt = self.handle_stmt()
            if nested_stmt is None:
                raise SyntaxError(
                    "Expected statement in conditional block.",
                    self.get_current_line(),
                )

            main_branch.append(nested_stmt)

            # update values
            current = self.current()

        # eat the "end" so this function should stop at the next token after "ens"
        self.advance()

        # return the statement block
        stmt = IfStmt(condition=expr, main_branch=main_branch)
        return stmt

    def handle_var_decl(self) -> VarDeclStmt | None:
        logging.info("Trying variable declaration")

        current = self.current()
        if current is None:
            return None

        # variables look like this:
        #   let <identifier> = <initial value expr>

        # check for the starting "let"
        if current.type is not TokenType.KW_LET:
            return None

        # check for the identifier
        self.advance()
        identf_token = self.current()
        if identf_token is None or identf_token.type is not TokenType.IDENTF:
            raise SyntaxError(
                "Missing identifier for variable declaration.",
                self.get_current_line(),
            )

        # dont add any initial value (and ignore equals) if next is a semicolon
        peek = self.peek()
        if peek is not None and peek.type is TokenType.SEMICOL:
            self.advance()  # eat the ;
            var_stmt = VarDeclStmt(name=identf_token.value)
            return var_stmt

        # check for the equal sign
        self.advance()
        current = self.current()
        if current is None or current.type is not TokenType.EQUAL:
            raise SyntaxError(
                "Missing equal sign or semicolon after identifier.",
                self.get_current_line(),
            )

        self.advance()  # eat the =

        # check for the initial value
        # remeber, this code starts after the equal sign
        initial_value: Expr | None = self.handle_expr()
        if initial_value is None:
            raise SyntaxError(
                "Missing expression after equals sign.", self.get_current_line()
            )

        # return what was made until now
        # remember handle_expr() left the code right after the expression
        var_stmt = VarDeclStmt(name=identf_token.value, initial_value=initial_value)
        return var_stmt

    # handle statements that run instructions
    def handle_stmt(self) -> Stmt | None:
        # check if its an if statement
        if_stmt = self.handle_if()
        if if_stmt is not None:
            return if_stmt

        # check if its a variable decladation
        var_stmt = self.handle_var_decl()
        if var_stmt is not None:
            return var_stmt

        # check if the line is an expression (theyre allowed as statements)
        expr = self.handle_expr()
        if expr is not None:
            # mark semicolons as statement enders
            current = self.current()
            if current is not None:
                if current.type is TokenType.SEMICOL:
                    self.advance()  # eat ;
                else:
                    raise SyntaxError(
                        "Missing semicolon after expression in statement.",
                        self.get_current_line(),
                    )

            return ExprStmt(expr)

    # return the parsed tree
    def get_ast(self) -> Program:
        while not self.is_at_end():
            # add statements
            try:
                stmt = self.handle_stmt()
                if stmt is not None:
                    self.tree.root.append(stmt)
            except SyntaxError as e:
                print(e)
                self.add_error(e)
                self.advance()

            # break out if theres no current character, though is_at_end should already handle it
            current = self.current()
            if current is None or current.type is TokenType.EOF:
                break
            # ignore extra semicolons
            elif current.type is TokenType.SEMICOL:
                self.advance()
                continue

            # by this point, we dont know what the token is
            self.add_error(
                SyntaxError(f"Invalid token: {self.current()}", self.get_current_line())
            )
            self.advance()  # skip it

        return self.tree
