import pytest

from app.typing.ast_match import lines_match
from app.typing.difficulty import DIFFICULTY_CEILING, difficulty_for
from app.typing.seed_data import SNIPPETS


@pytest.mark.parametrize("content", SNIPPETS)
def test_snippet_lines_are_self_consistent(content):
    assert "\n" not in content
    assert content.strip() != ""
    assert 0 < difficulty_for(content) <= DIFFICULTY_CEILING
    assert lines_match(content, content)


def test_snippet_bank_has_reasonable_size_and_variety():
    assert len(SNIPPETS) >= 30

    difficulties = [difficulty_for(c) for c in SNIPPETS]
    # Progressive-overload requires real coverage at both ends: plenty of
    # low-symbol content for new users, and content that reaches near the
    # Elo ceiling for users who've climbed all the way up.
    assert min(difficulties) < 600
    assert max(difficulties) >= 2800


def test_all_snippet_content_is_unique():
    assert len(SNIPPETS) == len(set(SNIPPETS))
