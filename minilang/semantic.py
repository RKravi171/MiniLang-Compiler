
from minilang.tokens import TokenType
from minilang.ast_nodes import (
    Program,
    LiteralExpr,
    VariableExpr,
    GroupingExpr,
    UnaryExpr,
    BinaryExpr,
    LetStatement,
    AssignStatement,
    PrintStatement,
    IfStatement,
)


class SemanticError(Exception):
    """Raised when semantic analysis finds an invalid program."""
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]

    def error(self, message, token=None):
        if token:
            raise SemanticError(
                f"{message} at line {token.line}, column {token.column}"
            )
        raise SemanticError(message)

    def declare(self, name, value_type, token):
        scope = self.scopes[-1]

        if name in scope:
            self.error(
                f"Variable '{name}' is already declared in this scope",
                token
            )

        scope[name] = value_type

    def resolve(self, name, token):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        self.error(f"Undefined variable '{name}'", token)

    def analyze(self, program):
        if not isinstance(program, Program):
            self.error("Expected a Program node")

        for statement in program.statements:
            self.analyze_statement(statement)

        return True

    def analyze_statement(self, statement):

        if isinstance(statement, LetStatement):
            name = statement.name.value
            value_type = self.analyze_expression(statement.initializer)

            self.declare(name, value_type, statement.name)

        elif isinstance(statement, AssignStatement):
            name = statement.name.value
            existing_type = self.resolve(name, statement.name)
            new_type = self.analyze_expression(statement.value)

            if existing_type != new_type:
                self.error(
                    f"Cannot assign {new_type} to variable "
                    f"'{name}' of type {existing_type}",
                    statement.name
                )

        elif isinstance(statement, PrintStatement):
            self.analyze_expression(statement.expression)

        elif isinstance(statement, IfStatement):
            condition_type = self.analyze_expression(statement.condition)

            if condition_type != "bool":
                self.error("If condition must be a Boolean expression")

            self.scopes.append({})

            try:
                for child in statement.then_branch:
                    self.analyze_statement(child)
            finally:
                self.scopes.pop()

            if statement.else_branch is not None:
                self.scopes.append({})

                try:
                    for child in statement.else_branch:
                        self.analyze_statement(child)
                finally:
                    self.scopes.pop()

        else:
            self.error(
                f"Unsupported statement: {type(statement).__name__}"
            )

    def analyze_expression(self, expression):

        if isinstance(expression, LiteralExpr):
            if isinstance(expression.value, bool):
                return "bool"

            if isinstance(expression.value, int):
                return "int"

            if isinstance(expression.value, float):
                return "float"

            if isinstance(expression.value, str):
                return "string"

        elif isinstance(expression, VariableExpr):
            return self.resolve(
                expression.name.value,
                expression.name
            )

        elif isinstance(expression, GroupingExpr):
            return self.analyze_expression(expression.expression)

        elif isinstance(expression, UnaryExpr):
            operand_type = self.analyze_expression(expression.right)

            if expression.operator.type == TokenType.MINUS:
                if operand_type not in ("int", "float"):
                    self.error(
                        "Unary '-' requires a numeric operand",
                        expression.operator
                    )
                return operand_type

            if expression.operator.type == TokenType.NOT:
                if operand_type != "bool":
                    self.error(
                        "'not' requires a Boolean operand",
                        expression.operator
                    )
                return "bool"

        elif isinstance(expression, BinaryExpr):
            left_type = self.analyze_expression(expression.left)
            right_type = self.analyze_expression(expression.right)
            operator = expression.operator.type

            # Logical operators
            if operator in (TokenType.AND, TokenType.OR):
                if left_type != "bool" or right_type != "bool":
                    self.error(
                        "Logical operators require Boolean operands",
                        expression.operator
                    )
                return "bool"

            # Equality operators
            if operator in (
                TokenType.EQUAL_EQUAL,
                TokenType.BANG_EQUAL
            ):
                if left_type != right_type:
                    self.error(
                        "Equality comparison requires matching types",
                        expression.operator
                    )
                return "bool"

            # Comparison operators
            if operator in (
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL
            ):
                if left_type != right_type or left_type not in (
                    "int", "float"
                ):
                    self.error(
                        "Comparison requires matching numeric types",
                        expression.operator
                    )
                return "bool"

            # Arithmetic operators
            if operator in (
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.PERCENT
            ):
                if left_type not in ("int", "float") or (
                    right_type not in ("int", "float")
                ):
                    self.error(
                        "Arithmetic operators require numeric operands",
                        expression.operator
                    )

                if left_type != right_type:
                    self.error(
                        "Arithmetic operands must have matching types",
                        expression.operator
                    )

                if operator == TokenType.SLASH:
                    return "float"

                return left_type

        self.error(
            f"Unsupported expression: {type(expression).__name__}"
        )


def analyze(program):
    """Convenience function for semantic analysis."""
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
