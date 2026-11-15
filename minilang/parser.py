
from minilang.tokens import Token, TokenType
from minilang.lexer import tokenize
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


class ParserError(Exception):
    """Raised when the parser finds invalid syntax."""
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type):
        if self.is_at_end():
            return token_type == TokenType.EOF
        return self.peek().type == token_type

    def check_next(self, token_type):
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == token_type

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()

        token = self.peek()
        raise ParserError(
            f"{message} at line {token.line}, column {token.column}"
        )

    # Program

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.statement())

        return Program(statements)

    # Statements

    def statement(self):
        if self.match(TokenType.LET):
            return self.let_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if (
            self.check(TokenType.IDENTIFIER)
            and self.check_next(TokenType.EQUAL)
        ):
            return self.assignment_statement()

        token = self.peek()
        raise ParserError(
            f"Unexpected token '{token.value}' "
            f"at line {token.line}, column {token.column}"
        )

    def let_statement(self):
        name = self.consume(
            TokenType.IDENTIFIER,
            "Expected variable name after 'let'"
        )

        self.consume(
            TokenType.EQUAL,
            "Expected '=' after variable name"
        )

        initializer = self.expression()

        self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after variable declaration"
        )

        return LetStatement(name, initializer)

    def assignment_statement(self):
        name = self.advance()

        self.consume(
            TokenType.EQUAL,
            "Expected '=' in assignment"
        )

        value = self.expression()

        self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after assignment"
        )

        return AssignStatement(name, value)

    def print_statement(self):
        self.consume(
            TokenType.LPAREN,
            "Expected '(' after 'print'"
        )

        expression = self.expression()

        self.consume(
            TokenType.RPAREN,
            "Expected ')' after print expression"
        )

        self.consume(
            TokenType.SEMICOLON,
            "Expected ';' after print statement"
        )

        return PrintStatement(expression)

    def if_statement(self):
        self.consume(
            TokenType.LPAREN,
            "Expected '(' after 'if'"
        )

        condition = self.expression()

        self.consume(
            TokenType.RPAREN,
            "Expected ')' after if condition"
        )

        then_branch = self.block()

        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.block()

        return IfStatement(condition, then_branch, else_branch)

    def block(self):
        self.consume(
            TokenType.LBRACE,
            "Expected '{' to start block"
        )

        statements = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.statement())

        self.consume(
            TokenType.RBRACE,
            "Expected '}' after block"
        )

        return statements

    # Expressions

    def expression(self):
        return self.or_expression()

    def or_expression(self):
        expression = self.and_expression()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expression()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def and_expression(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def equality(self):
        expression = self.comparison()

        while self.match(
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL
        ):
            operator = self.previous()
            right = self.comparison()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL
        ):
            operator = self.previous()
            right = self.term()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def term(self):
        expression = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT
        ):
            operator = self.previous()
            right = self.unary()

            expression = BinaryExpr(expression, operator, right)

        return expression

    def unary(self):
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous()
            right = self.unary()

            return UnaryExpr(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.TRUE, TokenType.FALSE):
            return LiteralExpr(self.previous().value)

        if self.match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            return LiteralExpr(self.previous().value)

        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())

        if self.match(TokenType.LPAREN):
            expression = self.expression()

            self.consume(
                TokenType.RPAREN,
                "Expected ')' after expression"
            )

            return GroupingExpr(expression)

        token = self.peek()

        raise ParserError(
            f"Expected expression at line {token.line}, "
            f"column {token.column}"
        )


def parse(source: str):
    """Tokenize and parse MiniLang source code."""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
