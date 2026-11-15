
import pytest

from minilang.parser import parse, ParserError
from minilang.ast_nodes import (
    Program,
    LetStatement,
    AssignStatement,
    PrintStatement,
    IfStatement,
    BinaryExpr,
    LiteralExpr,
    VariableExpr,
    UnaryExpr,
)
from minilang.tokens import TokenType


def test_parse_variable_declaration():
    program = parse("let age = 20;")

    assert isinstance(program, Program)
    assert len(program.statements) == 1

    statement = program.statements[0]

    assert isinstance(statement, LetStatement)
    assert statement.name.value == "age"
    assert statement.initializer.value == 20


def test_parse_assignment():
    program = parse("age = 25;")

    statement = program.statements[0]

    assert isinstance(statement, AssignStatement)
    assert statement.name.value == "age"
    assert statement.value.value == 25


def test_parse_print_statement():
    program = parse('print("Hello");')

    statement = program.statements[0]

    assert isinstance(statement, PrintStatement)
    assert isinstance(statement.expression, LiteralExpr)
    assert statement.expression.value == "Hello"


def test_parse_arithmetic_expression():
    program = parse("let result = 5 + 3;")

    expression = program.statements[0].initializer

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.PLUS
    assert expression.left.value == 5
    assert expression.right.value == 3


def test_operator_precedence():
    program = parse("let result = 5 + 3 * 2;")

    expression = program.statements[0].initializer

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.PLUS

    assert isinstance(expression.right, BinaryExpr)
    assert expression.right.operator.type == TokenType.STAR


def test_parse_comparison():
    program = parse("let result = 10 >= 5;")

    expression = program.statements[0].initializer

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.GREATER_EQUAL


def test_parse_boolean_expression():
    program = parse("let result = true and false;")

    expression = program.statements[0].initializer

    assert isinstance(expression, BinaryExpr)
    assert expression.operator.type == TokenType.AND


def test_parse_if_statement():
    source = """
    let age = 20;

    if (age >= 18) {
        print("Eligible");
    }
    """

    program = parse(source)

    statement = program.statements[1]

    assert isinstance(statement, IfStatement)
    assert isinstance(statement.condition, BinaryExpr)
    assert len(statement.then_branch) == 1
    assert statement.else_branch is None


def test_parse_if_else_statement():
    source = """
    if (true) {
        print("Yes");
    } else {
        print("No");
    }
    """

    program = parse(source)

    statement = program.statements[0]

    assert isinstance(statement, IfStatement)
    assert len(statement.then_branch) == 1
    assert statement.else_branch is not None
    assert len(statement.else_branch) == 1


def test_parse_nested_if():
    source = """
    if (true) {
        if (false) {
            print("Nested");
        }
    }
    """

    program = parse(source)

    outer_if = program.statements[0]
    inner_if = outer_if.then_branch[0]

    assert isinstance(outer_if, IfStatement)
    assert isinstance(inner_if, IfStatement)


def test_parse_unary_expression():
    program = parse("let result = -5;")

    expression = program.statements[0].initializer

    assert isinstance(expression, UnaryExpr)
    assert expression.operator.type == TokenType.MINUS


def test_missing_semicolon():
    with pytest.raises(ParserError):
        parse("let age = 20")


def test_missing_closing_parenthesis():
    with pytest.raises(ParserError):
        parse("print(20;")


def test_invalid_statement():
    with pytest.raises(ParserError):
        parse("20;")


def test_missing_block_brace():
    with pytest.raises(ParserError):
        parse("if (true) { print(1);")

