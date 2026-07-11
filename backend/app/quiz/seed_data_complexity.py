"""Code snippets for the complexity quiz category. Each tuple is
(difficulty, language, code, correct_time_key, correct_space_key,
explanation_md). The time/space keys reference app.quiz.constants.BIG_O_CHOICES
keys ("o1", "olog_n", "on", "on_log_n", "on2", "on3", "o2n", "on_fact").

seed.py expands each entry into two quiz_questions rows (dimension="time"
and "space") sharing one group_id, so the frontend renders/submits both
questions for one snippet together.

Starter set spanning the difficulty range; meant to grow to ~75 snippets
(see the quiz-modes phase plan).
"""

SNIPPETS: list[tuple[int, str, str, str, str, str]] = [
    (
        300,
        "python",
        "def total(nums):\n"
        "    result = 0\n"
        "    for n in nums:\n"
        "        result += n\n"
        "    return result",
        "on",
        "o1",
        "A single pass over the n input numbers -- O(n) time. Only one accumulator variable is kept "
        "regardless of input size -- O(1) space.",
    ),
    (
        350,
        "python",
        "def reverse(s):\n"
        "    return s[::-1]",
        "on",
        "on",
        "Slicing builds a new string by copying every character once -- O(n) time. The reversed "
        "string itself is a new n-length allocation -- O(n) space.",
    ),
    (
        450,
        "python",
        "def has_pair_with_sum(nums, target):\n"
        "    left, right = 0, len(nums) - 1\n"
        "    while left < right:\n"
        "        s = nums[left] + nums[right]\n"
        "        if s == target:\n"
        "            return True\n"
        "        elif s < target:\n"
        "            left += 1\n"
        "        else:\n"
        "            right -= 1\n"
        "    return False",
        "on",
        "o1",
        "Two pointers each move inward at most n times total -- O(n) time, on an already-sorted input. "
        "Only the two index variables are extra state -- O(1) space.",
    ),
    (
        500,
        "python",
        "def has_duplicate(nums):\n"
        "    seen = set()\n"
        "    for n in nums:\n"
        "        if n in seen:\n"
        "            return True\n"
        "        seen.add(n)\n"
        "    return False",
        "on",
        "on",
        "One pass with O(1) average-case set lookups/inserts -- O(n) time. The `seen` set can grow to "
        "hold all n elements in the worst case -- O(n) space.",
    ),
    (
        550,
        "python",
        "def two_sum_brute_force(nums, target):\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i + 1, len(nums)):\n"
        "            if nums[i] + nums[j] == target:\n"
        "                return (i, j)\n"
        "    return None",
        "on2",
        "o1",
        "Every pair of indices is checked, roughly n^2/2 comparisons -- O(n^2) time. No data structure "
        "grows with input size, just a couple of index variables -- O(1) space.",
    ),
    (
        600,
        "python",
        "def factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * factorial(n - 1)",
        "on",
        "on",
        "One multiplication per recursive call, n calls deep -- O(n) time. Each call adds a stack "
        "frame that isn't popped until the base case returns, so the call stack itself holds n frames "
        "-- O(n) space.",
    ),
    (
        700,
        "python",
        "def binary_search(sorted_nums, target):\n"
        "    lo, hi = 0, len(sorted_nums) - 1\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if sorted_nums[mid] == target:\n"
        "            return mid\n"
        "        elif sorted_nums[mid] < target:\n"
        "            lo = mid + 1\n"
        "        else:\n"
        "            hi = mid - 1\n"
        "    return -1",
        "olog_n",
        "o1",
        "Each iteration halves the search range, giving O(log n) time. Only a handful of index "
        "variables are used regardless of input size -- O(1) space.",
    ),
    (
        900,
        "python",
        "def fib_memo(n, cache={}):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    if n not in cache:\n"
        "        cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)\n"
        "    return cache[n]",
        "on",
        "on",
        "Memoization means each of the n distinct subproblems is computed once and then reused -- "
        "O(n) time overall despite the naive recursive shape. The cache dict (and recursion depth) "
        "both hold O(n) entries.",
    ),
    (
        1300,
        "python",
        "def merge_sort(arr):\n"
        "    if len(arr) <= 1:\n"
        "        return arr\n"
        "    mid = len(arr) // 2\n"
        "    left = merge_sort(arr[:mid])\n"
        "    right = merge_sort(arr[mid:])\n"
        "    merged = []\n"
        "    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n"
        "        if left[i] <= right[j]:\n"
        "            merged.append(left[i]); i += 1\n"
        "        else:\n"
        "            merged.append(right[j]); j += 1\n"
        "    merged.extend(left[i:]); merged.extend(right[j:])\n"
        "    return merged",
        "on_log_n",
        "on",
        "The array is split in half log n times, and each of the log n levels does O(n) work merging "
        "-- O(n log n) time. The merge step allocates new lists, and the recursion needs O(n) auxiliary "
        "space in total across the merge buffers.",
    ),
    (
        1600,
        "python",
        "def fib(n):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 2)",
        "o2n",
        "on",
        "Without memoization, each call spawns two more, forming a call tree that roughly doubles in "
        "size per level of depth n -- O(2^n) time. The deepest single chain of pending calls is only n "
        "frames, so space is O(n), not O(2^n) -- the call tree is wide but the stack only holds one "
        "root-to-leaf path at a time.",
    ),
    (
        1800,
        "python",
        "def matrix_multiply(a, b, n):\n"
        "    result = [[0] * n for _ in range(n)]\n"
        "    for i in range(n):\n"
        "        for j in range(n):\n"
        "            for k in range(n):\n"
        "                result[i][j] += a[i][k] * b[k][j]\n"
        "    return result",
        "on3",
        "on2",
        "Three nested loops over dimension n each -- O(n^3) time for the naive algorithm. The output "
        "matrix alone holds n^2 entries -- O(n^2) space.",
    ),
    (
        2000,
        "python",
        "def permutations(items):\n"
        "    if len(items) <= 1:\n"
        "        return [items]\n"
        "    result = []\n"
        "    for i in range(len(items)):\n"
        "        rest = items[:i] + items[i + 1:]\n"
        "        for p in permutations(rest):\n"
        "            result.append([items[i]] + p)\n"
        "    return result",
        "on_fact",
        "on_fact",
        "There are n! distinct permutations of n items, and this builds every one of them -- O(n!) "
        "time. All of them are held in `result` simultaneously -- O(n!) space too, since the output "
        "itself is n! lists.",
    ),
]
