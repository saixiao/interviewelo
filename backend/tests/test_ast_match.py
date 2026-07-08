import pytest

from app.typing.ast_match import lines_match


@pytest.mark.parametrize(
    "target,typed",
    [
        ("return nums[i] + nums[j]", "return arr[i] + arr[j]"),
        ("x = 5", "x = 10"),
        ("total = total + 1", "total = total + 999"),
        ("for i in range(len(nums)):", "for idx in range(len(arr)):"),
        ("def two_sum(nums, target):", "def two_sum(a, b):"),
        ("if x > 0:", "if y > 0:"),
        ("return True", "return True"),
        ("s = 'hello'", 's = "world"'),
        ("  return x + 1", "return x+1"),  # whitespace/indentation is incidental
        ("nums.append(x)", "nums.append(y)"),
    ],
)
def test_structurally_equivalent_lines_match(target, typed):
    assert lines_match(target, typed) is True


@pytest.mark.parametrize(
    "target,typed",
    [
        ("return len(nums)", "return sum(nums)"),  # different function called
        ("nums.append(x)", "nums.pop(x)"),  # different method called
        ("x = 5", 'x = "5"'),  # different literal type
        ("if x > 0:", "if x < 0:"),  # different comparison operator
        ("return x + 1", "return x - 1"),  # different binary operator
        ("for i in range(n):", "while i < n:"),  # different statement kind
        ("return nums[i]", "return nums[i] + 1"),  # different shape
    ],
)
def test_structurally_different_lines_do_not_match(target, typed):
    assert lines_match(target, typed) is False


def test_unparseable_lines_fall_back_to_normalized_text():
    # "else:" alone can never parse (needs a preceding if), even wrapped.
    assert lines_match("else:", "else:") is True
    assert lines_match("else:", "elif:") is False


def test_blank_lines_match():
    assert lines_match("", "   ") is True


def test_multiline_snippet_body_extracted_correctly():
    assert lines_match("try:", "try:") is True
