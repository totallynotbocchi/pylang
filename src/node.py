from dataclasses import dataclass, field

from src.token import TokenType

# expressions


@dataclass
class Expr:
    pass


# numbers, like "2"
@dataclass
class NumberExpr(Expr):
    value: str


# variable calling, like "x"
@dataclass
class VariableExpr(Expr):
    name: str


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: TokenType
    right: Expr


# values with a preceding operator, like "!x" (not x) or "-y" (negative y)
@dataclass
class UnaryExpr(Expr):
    value: Expr
    op: TokenType


# statements


@dataclass
class Stmt:
    pass


@dataclass
class Program(Stmt):
    root: list[Stmt | Expr] = field(default_factory=list)


@dataclass
class IfStmt(Stmt):
    condition: Expr
    main_branch: list[Stmt | Expr]

    # maps condition -> block
    elsif_branches: dict[Expr, list[Stmt | Expr]] = field(default_factory=dict)

    else_branch: list[Stmt | Expr] = field(default_factory=list)


# expressions used standalone, like:
#   x+2; x+3
@dataclass
class ExprStmt(Stmt, Expr):
    expr: Expr


# variable declaration, like:
#   let x = y;
@dataclass
class VarDeclStmt(Stmt):
    name: str
    initial_value: Expr | None = None
