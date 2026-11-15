
import pytest

from minilang.parser import parse
from minilang.semantic import analyze
from minilang.interpreter import interpret, RuntimeError


def run_program(source):
    program = parse(source)
    analyze(program)
    return interpret(program)


def test_print_string(capsys):
    run_program('print("Hello MiniLang");')

    captured = capsys.readouterr()
    assert captured.out == "Hello MiniLang\n"


def test_variable_declaration(capsys):
    run_program("""
    let age = 20;
    print(age);
    """)

    captured = capsys.readouterr()
    assert captured.out == "20\n"


def test_arithmetic_addition(capsys):
    run_program("""
    let result = 10 + 5;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "15\n"


def test_arithmetic_precedence(capsys):
    run_program("""
    let result = 5 + 3 * 2;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "11\n"


def test_assignment(capsys):
    run_program("""
    let age = 20;
    age = 25;
    print(age);
    """)

    captured = capsys.readouterr()
    assert captured.out == "25\n"


def test_comparison_true(capsys):
    run_program("""
    let result = 10 >= 5;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "True\n"


def test_if_true_branch(capsys):
    run_program("""
    if (true) {
        print("YES");
    }
    """)

    captured = capsys.readouterr()
    assert captured.out == "YES\n"


def test_if_false_branch(capsys):
    run_program("""
    if (false) {
        print("YES");
    } else {
        print("NO");
    }
    """)

    captured = capsys.readouterr()
    assert captured.out == "NO\n"


def test_nested_if(capsys):
    run_program("""
    if (true) {
        if (true) {
            print("Nested");
        }
    }
    """)

    captured = capsys.readouterr()
    assert captured.out == "Nested\n"


def test_unary_minus(capsys):
    run_program("""
    let result = -10;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "-10\n"


def test_logical_and(capsys):
    run_program("""
    let result = true and false;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "False\n"


def test_logical_or(capsys):
    run_program("""
    let result = false or true;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "True\n"


def test_logical_not(capsys):
    run_program("""
    let result = not false;
    print(result);
    """)

    captured = capsys.readouterr()
    assert captured.out == "True\n"


def test_division_by_zero():
    program = parse("""
    let result = 10 / 0;
    print(result);
    """)
    analyze(program)

    with pytest.raises(RuntimeError, match="Division by zero"):
        interpret(program)


def test_undefined_variable_runtime():
    program = parse("print(age);")

    with pytest.raises(RuntimeError, match="Undefined variable"):
        interpret(program)
