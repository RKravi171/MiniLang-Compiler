
import pytest

from minilang.lexer import tokenize, LexerError
from minilang.tokens import TokenType


def test_variable_declaration():
    tokens = tokenize("let age = 20;")

    assert tokens[0].type == TokenType.LET
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "age"
    assert tokens[2].type == TokenType.EQUAL
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[3].value == 20
    assert tokens[4].type == TokenType.SEMICOLON


def test_keywords():
    tokens = tokenize("let if else print true false and or not")

    expected = [
        TokenType.LET,
        TokenType.IF,
        TokenType.ELSE,
        TokenType.PRINT,
        TokenType.TRUE,
        TokenType.FALSE,
        TokenType.AND,
        TokenType.OR,
        TokenType.NOT,
        TokenType.EOF,
    ]

    assert [token.type for token in tokens] == expected


def test_integer_and_float():
    tokens = tokenize("100 25.50")

    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == 100

    assert tokens[1].type == TokenType.FLOAT
    assert tokens[1].value == 25.50


def test_string():
    tokens = tokenize('"Hello MiniLang"')

    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello MiniLang"


def test_string_escape_sequences():
    tokens = tokenize(r'"Hello\nWorld"')

    assert tokens[0].value == "Hello\nWorld"


def test_arithmetic_operators():
    tokens = tokenize("+ - * / %")

    expected = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
    ]

    assert [token.type for token in tokens[:-1]] == expected


def test_comparison_operators():
    tokens = tokenize("= == != > >= < <=")

    expected = [
        TokenType.EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.BANG_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
    ]

    assert [token.type for token in tokens[:-1]] == expected


def test_punctuation():
    tokens = tokenize("( ) { } ; ,")

    expected = [
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.COMMA,
    ]

    assert [token.type for token in tokens[:-1]] == expected


def test_comments_are_ignored():
    tokens = tokenize("let age = 20; // this is a comment")

    assert [token.type for token in tokens] == [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.INTEGER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_line_and_column():
    tokens = tokenize("let age = 20;\nprint(age);")

    assert tokens[0].line == 1
    assert tokens[0].column == 1

    assert tokens[5].line == 2
    assert tokens[5].column == 1


def test_eof_token():
    tokens = tokenize("")

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_unexpected_character():
    with pytest.raises(LexerError):
        tokenize("let age = @;")


def test_unterminated_string():
    with pytest.raises(LexerError):
        tokenize('"Hello MiniLang')


def test_invalid_decimal():
    with pytest.raises(LexerError):
        tokenize("12.3.4")


def test_unexpected_bang():
    with pytest.raises(LexerError):
        tokenize("!")
