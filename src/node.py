from dataclasses import dataclass

from src.token import TokenType

# expressions


@dataclass
class Expr:
    pass


@dataclass
class NumberExpr(Expr):
    value: str


@dataclass
class VariableExpr(Expr):
    name: str


@dataclass
class GroupedExpr(Expr):
    expr: Expr


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: TokenType
    right: Expr


# statements


@dataclass
class Stmt:
    pass


@dataclass
class IfStmt(Stmt):
    condition: Expr
    main_branch: list[Stmt | Expr]
    elsif_branches: dict[Expr, list[Stmt | Expr]]  # maps condition -> block
    else_branch: list[Stmt | Expr]


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class Program(Stmt):
    root: list[Stmt | Expr]
