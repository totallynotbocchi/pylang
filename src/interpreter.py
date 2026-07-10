from ansimarkup import parse

from src.node import Expr, ExprStmt, NumberExpr, Program, Stmt, UnaryExpr
from src.token import TokenType


class RuntimeError(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(message)

    def __str__(self) -> str:
        return parse(f"<red>Runtime Error</red>: {self.message}")


class Interpreter:
    def __init__(self, ast: Program) -> None:
        self.ast = ast

        self.errors = []

    def add_error(self, error: RuntimeError):
        self.errors.append(error)

    def handle_expr(self, expr: Expr):
        if type(expr) is UnaryExpr:
            unary_expr: UnaryExpr = expr

            match unary_expr.op:
                case TokenType.MINUS:
                    evaluated = self.handle_expr(unary_expr.value)

                    if evaluated is None:
                        return None

                    return -evaluated

                case _:
                    raise RuntimeError("Unknown unary expression")

        elif type(expr) is NumberExpr:
            num_expr: NumberExpr = expr

            try:
                number = int(num_expr.value)
                return number
            except Exception:
                print("Invalid number.")
        elif type(expr) is ExprStmt:
            expr_stmt: ExprStmt = expr
            res = self.handle_expr(expr_stmt.expr)

            if res is None:
                return None

            return res
        else:
            raise RuntimeError("Unknown expression")

    def handle_stmt(self, stmt: Stmt):
        pass

    def execute(self):
        for node in self.ast.root:
            if isinstance(node, Expr):
                try:
                    result = self.handle_expr(node)
                    print(result)
                except RuntimeError as e:
                    self.add_error(e)
            elif isinstance(node, Stmt):
                self.handle_stmt(node)

            self.add_error(RuntimeError("Unknown block"))
