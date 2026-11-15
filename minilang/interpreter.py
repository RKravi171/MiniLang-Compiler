
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


class RuntimeError(Exception):
    """Raised when an error occurs during program execution."""
    pass


class Interpreter:
    def __init__(self):
        self.scopes = [{}]

    def error(self, message, token=None):
        if token:
            raise RuntimeError(
                f"{message} at line {token.line}, column {token.column}"
            )
        raise RuntimeError(message)

    # Variable management

    def define(self, name, value):
        if name in self.scopes[-1]:
            self.error(f"Variable '{name}' is already defined")
        self.scopes[-1][name] = value

    def get_variable(self, name, token):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        self.error(f"Undefined variable '{name}'", token)

    def assign_variable(self, name, value, token):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

        self.error(f"Undefined variable '{name}'", token)

    # Program execution

    def interpret(self, program):
        if not isinstance(program, Program):
            self.error("Expected a Program node")

        for statement in program.statements:
            self.execute(statement)

        return True

    def execute(self, statement):

        if isinstance(statement, LetStatement):
            value = self.evaluate(statement.initializer)
            self.define(statement.name.value, value)

        elif isinstance(statement, AssignStatement):
            value = self.evaluate(statement.value)
            self.assign_variable(
                statement.name.value,
                value,
                statement.name
            )

        elif isinstance(statement, PrintStatement):
            value = self.evaluate(statement.expression)
            print(value)

        elif isinstance(statement, IfStatement):
            condition = self.evaluate(statement.condition)

            if not isinstance(condition, bool):
                self.error("If condition must be Boolean")

            if condition:
                self.execute_block(statement.then_branch)
            elif statement.else_branch is not None:
                self.execute_block(statement.else_branch)

        else:
            self.error(
                f"Unsupported statement: {type(statement).__name__}"
            )

    def execute_block(self, statements):
        self.scopes.append({})

        try:
            for statement in statements:
                self.execute(statement)
        finally:
            self.scopes.pop()

    # Expression evaluation

    def evaluate(self, expression):

        if isinstance(expression, LiteralExpr):
            return expression.value

        if isinstance(expression, VariableExpr):
            return self.get_variable(
                expression.name.value,
                expression.name
            )

        if isinstance(expression, GroupingExpr):
            return self.evaluate(expression.expression)

        if isinstance(expression, UnaryExpr):
            right = self.evaluate(expression.right)

            if expression.operator.type == TokenType.MINUS:
                if isinstance(right, bool) or not isinstance(
                    right, (int, float)
                ):
                    self.error("Unary '-' requires a numeric value")

                return -right

            if expression.operator.type == TokenType.NOT:
                if not isinstance(right, bool):
                    self.error("'not' requires a Boolean value")

                return not right

        if isinstance(expression, BinaryExpr):
            left = self.evaluate(expression.left)
            operator = expression.operator.type

            # Short-circuit logical operators
            if operator == TokenType.AND:
                if not isinstance(left, bool):
                    self.error("'and' requires Boolean operands")

                if not left:
                    return False

                right = self.evaluate(expression.right)

                if not isinstance(right, bool):
                    self.error("'and' requires Boolean operands")

                return left and right

            if operator == TokenType.OR:
                if not isinstance(left, bool):
                    self.error("'or' requires Boolean operands")

                if left:
                    return True

                right = self.evaluate(expression.right)

                if not isinstance(right, bool):
                    self.error("'or' requires Boolean operands")

                return left or right

            right = self.evaluate(expression.right)

            # Arithmetic
            if operator == TokenType.PLUS:
                return self.numeric_operation(left, right, lambda a, b: a + b)

            if operator == TokenType.MINUS:
                return self.numeric_operation(left, right, lambda a, b: a - b)

            if operator == TokenType.STAR:
                return self.numeric_operation(left, right, lambda a, b: a * b)

            if operator == TokenType.SLASH:
                if right == 0:
                    self.error("Division by zero")

                return self.numeric_operation(
                    left, right, lambda a, b: a / b
                )

            if operator == TokenType.PERCENT:
                if right == 0:
                    self.error("Modulo by zero")

                return self.numeric_operation(
                    left, right, lambda a, b: a % b
                )

            # Comparison
            if operator == TokenType.GREATER:
                return self.compare(left, right, lambda a, b: a > b)

            if operator == TokenType.GREATER_EQUAL:
                return self.compare(left, right, lambda a, b: a >= b)

            if operator == TokenType.LESS:
                return self.compare(left, right, lambda a, b: a < b)

            if operator == TokenType.LESS_EQUAL:
                return self.compare(left, right, lambda a, b: a <= b)

            # Equality
            if operator == TokenType.EQUAL_EQUAL:
                return type(left) is type(right) and left == right

            if operator == TokenType.BANG_EQUAL:
                return type(left) is not type(right) or left != right

        self.error(
            f"Unsupported expression: {type(expression).__name__}"
        )

    # Operation helpers

    def numeric_operation(self, left, right, operation):
        if (
            isinstance(left, bool)
            or isinstance(right, bool)
            or not isinstance(left, (int, float))
            or not isinstance(right, (int, float))
        ):
            self.error("Arithmetic requires numeric values")

        return operation(left, right)

    def compare(self, left, right, operation):
        if (
            isinstance(left, bool)
            or isinstance(right, bool)
            or not isinstance(left, (int, float))
            or not isinstance(right, (int, float))
        ):
            self.error("Comparison requires numeric values")

        return operation(left, right)


def interpret(program):
    """Convenience function to execute a MiniLang program."""
    interpreter = Interpreter()
    return interpreter.interpret(program)
