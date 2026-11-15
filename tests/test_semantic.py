
import pytest

from minilang.parser import parse
from minilang.semantic import analyze, SemanticError


def test_valid_variable_declaration():
    program = parse("let age = 20;")
    assert analyze(program) is True


def test_valid_variable_usage():
    program = parse("""
    let age = 20;
    print(age);
    """)
    assert analyze(program) is True


def test_undefined_variable():
    program = parse("print(salary);")

    with pytest.raises(SemanticError, match="Undefined variable"):
        analyze(program)


def test_duplicate_variable_declaration():
    program = parse("""
    let age = 20;
    let age = 25;
    """)

    with pytest.raises(SemanticError, match="already declared"):
        analyze(program)


def test_valid_assignment():
    program = parse("""
    let age = 20;
    age = 25;
    """)

    assert analyze(program) is True


def test_assignment_to_undefined_variable():
    program = parse("age = 25;")

    with pytest.raises(SemanticError, match="Undefined variable"):
        analyze(program)


def test_assignment_type_mismatch():
    program = parse("""
    let age = 20;
    age = "Hello";
    """)

    with pytest.raises(SemanticError, match="Cannot assign"):
        analyze(program)


def test_valid_arithmetic():
    program = parse("let result = 5 + 3;")
    assert analyze(program) is True


def test_invalid_arithmetic_types():
    program = parse('let result = "Hello" + 5;')

    with pytest.raises(SemanticError, match="numeric operands"):
        analyze(program)


def test_valid_boolean_condition():
    program = parse("""
    if (true) {
        print("Yes");
    }
    """)

    assert analyze(program) is True


def test_invalid_if_condition():
    program = parse("""
    if (20) {
        print("Yes");
    }
    """)

    with pytest.raises(SemanticError, match="Boolean"):
        analyze(program)


def test_valid_comparison():
    program = parse("let result = 10 >= 5;")
    assert analyze(program) is True


def test_invalid_logical_operation():
    program = parse("let result = 10 and 20;")

    with pytest.raises(SemanticError, match="Boolean operands"):
        analyze(program)


def test_valid_if_else():
    program = parse("""
    if (true) {
        print("Yes");
    } else {
        print("No");
    }
    """)

    assert analyze(program) is True


def test_block_scope():
    program = parse("""
    if (true) {
        let message = "Hello";
    }
    print(message);
    """)

    with pytest.raises(SemanticError, match="Undefined variable"):
        analyze(program)
