
from minilang.tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Raised when the lexer finds invalid source code."""
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def is_at_end(self):
        return self.position >= len(self.source)

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.position]

    def peek_next(self):
        if self.position + 1 >= len(self.source):
            return "\0"
        return self.source[self.position + 1]

    def advance(self):
        char = self.source[self.position]
        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def match(self, expected):
        if self.is_at_end() or self.peek() != expected:
            return False

        self.advance()
        return True

    def make_token(self, token_type, value, line, column):
        return Token(token_type, value, line, column)

    def skip_whitespace_and_comments(self):
        while not self.is_at_end():
            char = self.peek()

            if char in " \r\t\n":
                self.advance()

            elif char == "/" and self.peek_next() == "/":
                while not self.is_at_end() and self.peek() != "\n":
                    self.advance()

            else:
                break

    def read_identifier(self, line, column):
        start = self.position

        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[start:self.position]

        if text in KEYWORDS:
            token_type = KEYWORDS[text]

            if token_type == TokenType.TRUE:
                value = True
            elif token_type == TokenType.FALSE:
                value = False
            else:
                value = text

            return self.make_token(token_type, value, line, column)

        return self.make_token(
            TokenType.IDENTIFIER, text, line, column
        )

    def read_number(self, line, column):
        start = self.position

        while self.peek().isdigit():
            self.advance()

        is_float = False

        if self.peek() == "." and self.peek_next().isdigit():
            is_float = True
            self.advance()

            while self.peek().isdigit():
                self.advance()

        if self.peek() == ".":
            raise LexerError(
                f"Invalid number at line {line}, column {column}"
            )

        text = self.source[start:self.position]

        if is_float:
            return self.make_token(
                TokenType.FLOAT, float(text), line, column
            )

        return self.make_token(
            TokenType.INTEGER, int(text), line, column
        )

    def read_string(self, line, column):
        self.advance()  # Skip opening quote
        characters = []

        while not self.is_at_end() and self.peek() != '"':
            char = self.advance()

            if char == "\n":
                raise LexerError(
                    f"Unterminated string at line {line}, column {column}"
                )

            if char == "\\":
                if self.is_at_end():
                    break

                escaped = self.advance()

                escape_sequences = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                }

                if escaped not in escape_sequences:
                    raise LexerError(
                        f"Invalid escape sequence at line {self.line}, "
                        f"column {self.column - 1}"
                    )

                characters.append(escape_sequences[escaped])

            else:
                characters.append(char)

        if self.is_at_end():
            raise LexerError(
                f"Unterminated string at line {line}, column {column}"
            )

        self.advance()  # Skip closing quote

        return self.make_token(
            TokenType.STRING,
            "".join(characters),
            line,
            column
        )

    def tokenize(self):
        tokens = []

        while not self.is_at_end():
            self.skip_whitespace_and_comments()

            if self.is_at_end():
                break

            line = self.line
            column = self.column
            char = self.peek()

            if char.isalpha() or char == "_":
                token = self.read_identifier(line, column)

            elif char.isdigit():
                token = self.read_number(line, column)

            elif char == '"':
                token = self.read_string(line, column)

            else:
                self.advance()

                single_char_tokens = {
                    "+": TokenType.PLUS,
                    "-": TokenType.MINUS,
                    "*": TokenType.STAR,
                    "/": TokenType.SLASH,
                    "%": TokenType.PERCENT,
                    "(": TokenType.LPAREN,
                    ")": TokenType.RPAREN,
                    "{": TokenType.LBRACE,
                    "}": TokenType.RBRACE,
                    ";": TokenType.SEMICOLON,
                    ",": TokenType.COMMA,
                }

                if char in single_char_tokens:
                    token = self.make_token(
                        single_char_tokens[char], char, line, column
                    )

                elif char == "=":
                    if self.match("="):
                        token = self.make_token(
                            TokenType.EQUAL_EQUAL, "==", line, column
                        )
                    else:
                        token = self.make_token(
                            TokenType.EQUAL, "=", line, column
                        )

                elif char == "!":
                    if self.match("="):
                        token = self.make_token(
                            TokenType.BANG_EQUAL, "!=", line, column
                        )
                    else:
                        raise LexerError(
                            f"Unexpected character '!' at line {line}, "
                            f"column {column}"
                        )

                elif char == ">":
                    if self.match("="):
                        token = self.make_token(
                            TokenType.GREATER_EQUAL, ">=", line, column
                        )
                    else:
                        token = self.make_token(
                            TokenType.GREATER, ">", line, column
                        )

                elif char == "<":
                    if self.match("="):
                        token = self.make_token(
                            TokenType.LESS_EQUAL, "<=", line, column
                        )
                    else:
                        token = self.make_token(
                            TokenType.LESS, "<", line, column
                        )

                else:
                    raise LexerError(
                        f"Unexpected character '{char}' at line {line}, "
                        f"column {column}"
                    )

            tokens.append(token)

        tokens.append(
            self.make_token(TokenType.EOF, None, self.line, self.column)
        )

        return tokens


def tokenize(source: str):
    """Convenience function to tokenize source code."""
    return Lexer(source).tokenize()
