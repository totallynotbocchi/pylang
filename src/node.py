from dataclasses import dataclass, field

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


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class VarDeclStmt(Stmt):
    name: str
    initial_value: Expr | None = None
