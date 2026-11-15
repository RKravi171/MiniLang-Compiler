
import argparse
import sys
from pathlib import Path
from pprint import pprint

from minilang.lexer import tokenize, LexerError
from minilang.parser import parse, ParserError
from minilang.semantic import analyze, SemanticError
from minilang.interpreter import interpret, RuntimeError


def read_source(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    if path.suffix != ".mini":
        raise ValueError("MiniLang source files must use the .mini extension")

    return path.read_text(encoding="utf-8")


def command_tokens(source):
    tokens = tokenize(source)

    print("\nMINILANG TOKENS")
    print("-" * 50)

    for token in tokens:
        print(
            f"{token.type.name:<18} "
            f"Value: {str(token.value):<15} "
            f"Line: {token.line:<4} "
            f"Column: {token.column}"
        )


def command_ast(source):
    program = parse(source)

    print("\nABSTRACT SYNTAX TREE")
    print("-" * 50)

    pprint(program, indent=4, sort_dicts=False)


def command_check(source):
    program = parse(source)
    analyze(program)

    print("Semantic analysis successful!")
    print("No semantic errors found.")


def command_run(source):
    program = parse(source)
    analyze(program)

    print("\nPROGRAM OUTPUT")
    print("-" * 50)

    interpret(program)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="minilang",
        description="MiniLang - A Mini If-Else Language Interpreter",
        epilog="Example: python -m minilang.cli run examples/hello.mini"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    for command, description in [
        ("run", "Execute a MiniLang program"),
        ("tokens", "Display the tokens"),
        ("ast", "Display the Abstract Syntax Tree"),
        ("check", "Check semantic errors"),
    ]:
        command_parser = subparsers.add_parser(
            command,
            help=description
        )

        command_parser.add_argument(
            "file",
            help="Path to a .mini source file"
        )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        source = read_source(args.file)

        if args.command == "run":
            command_run(source)

        elif args.command == "tokens":
            command_tokens(source)

        elif args.command == "ast":
            command_ast(source)

        elif args.command == "check":
            command_check(source)

    except (
        FileNotFoundError,
        ValueError,
        LexerError,
        ParserError,
        SemanticError,
        RuntimeError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
