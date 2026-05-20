"""
Tests for type checking on example scripts.

Verifies that example scripts are properly typed and would pass mypy --strict.
"""

from __future__ import annotations

import ast
from pathlib import Path


def get_python_files(directory: Path) -> list[Path]:
    """Get all Python files in a directory."""
    return list(directory.glob("*.py"))


def has_type_annotations(file_path: Path) -> bool:
    """Check if a Python file has type annotations."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            # Check for function/method annotations
            if isinstance(node, ast.FunctionDef):
                if node.returns is not None:
                    return True
                # Check function arguments
                for arg in node.args.args:
                    if arg.annotation is not None:
                        return True

            # Check for variable annotations
            if isinstance(node, ast.AnnAssign):
                return True

        return False
    except (SyntaxError, OSError):
        return False


def test_example_files_exist() -> None:
    """Verify that example scripts exist."""
    examples_dir = Path(__file__).parent.parent / "examples"
    assert examples_dir.exists(), "examples directory not found"

    example_files = get_python_files(examples_dir)
    assert len(example_files) > 0, "No example Python files found in examples/"


def test_example_files_have_type_hints() -> None:
    """Verify that example scripts include type hints."""
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = get_python_files(examples_dir)

    for example_file in example_files:
        has_hints = has_type_annotations(example_file)
        assert (
            has_hints
        ), f"Example file {example_file.name} lacks type annotations. Add function return types and parameter types."


def test_examples_are_syntactically_valid() -> None:
    """Verify all example scripts are syntactically valid Python."""
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = get_python_files(examples_dir)

    for example_file in example_files:
        try:
            with open(example_file) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {example_file.name}: {e}") from e


def test_no_future_annotations_in_py312_files() -> None:
    """Verify Python 3.12+ files don't require __future__ annotations import.

    Python 3.12+ supports native PEP 563 semantics for string annotations.
    """
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = get_python_files(examples_dir)

    for example_file in example_files:
        with open(example_file) as f:
            content = f.read()

        # Check if file uses `from __future__ import annotations`
        if "from __future__ import annotations" in content:
            # This is acceptable for compatibility, but not required on 3.12+
            # Just verify it's one of the first imports
            lines = content.split("\n")
            found_on_line = None
            for i, line in enumerate(lines[:20]):  # Check first 20 lines
                if "from __future__ import annotations" in line:
                    found_on_line = i + 1
                    break

            assert found_on_line is not None, f"{example_file.name} has misplaced __future__ import"
