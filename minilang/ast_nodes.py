
from dataclasses import dataclass, field
from typing import Optional

from minilang.tokens import Token


# Base classes

class Expression:
    """Base class for all expressions."""
    pass


class Statement:
    """Base class for all statements."""
    pass


# Program

@dataclass
class Program:
    statements: list[Statement] = field(default_factory=list)


# Expressions

@dataclass
class LiteralExpr(Expression):
    value: object


@dataclass
class VariableExpr(Expression):
    name: Token


@dataclass
class GroupingExpr(Expression):
    expression: Expression


@dataclass
class UnaryExpr(Expression):
    operator: Token
    right: Expression


@dataclass
class BinaryExpr(Expression):
    left: Expression
    operator: Token
    right: Expression


# Statements

@dataclass
class LetStatement(Statement):
    name: Token
    initializer: Expression


@dataclass
class AssignStatement(Statement):
    name: Token
    value: Expression


@dataclass
class PrintStatement(Statement):
    expression: Expression


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: list[Statement]
    else_branch: Optional[list[Statement]] = None
