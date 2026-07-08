import ast

import pytest

from app.typing.ast_match import lines_match
from app.typing.seed_data import SNIPPETS

# A handful of entries are deliberately partial statements (e.g. "try:",
# "class Solution:") meant to be typed as a fragment, not full programs.
_PARTIAL_STATEMENTS = {"try:", "class Solution:"}


@pytest.mark.parametrize("content,difficulty", SNIPPETS)
def test_snippet_lines_are_self_consistent(content, difficulty):
    assert 0 < difficulty <= 3000
    assert content == content.rstrip("\n")
    for line in content.split("\n"):
        if line.strip():
            assert lines_match(line, line)


def test_multiline_snippets_compile_as_valid_python():
    for content, _ in SNIPPETS:
        if "\n" not in content or content.strip() in _PARTIAL_STATEMENTS:
            continue
        compile(content, "<snippet>", "exec")


def test_snippet_bank_has_reasonable_size_and_variety():
    assert len(SNIPPETS) >= 30
    multiline_count = sum(1 for content, _ in SNIPPETS if "\n" in content)
    assert multiline_count >= 8


def test_all_snippet_content_is_unique():
    contents = [content for content, _ in SNIPPETS]
    assert len(contents) == len(set(contents))
