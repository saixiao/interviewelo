"""Seed content for Typing Racer: real Python idioms of varying length and
symbol density. Classic mode types these whole; Reaction mode splits
multi-line entries into individual lines. `difficulty` is an Elo-scale
content-difficulty rating (same scale as user ratings) used as `D` by the
Elo engine.
"""

SNIPPETS: list[tuple[str, int]] = [
    # --- short idioms, low symbol density ---
    ("nums = [1, 2, 3, 4, 5]", 300),
    ("total = sum(nums)", 300),
    ('d = {"a": 1, "b": 2}', 400),
    ("x, y = y, x", 400),
    ("keys = list(d.keys())", 400),
    ("n = int(input())", 300),
    ("unique = set(nums)", 400),
    ("reversed_list = nums[::-1]", 500),
    ("first, *rest = [1, 2, 3, 4]", 600),
    ("merged = {**dict1, **dict2}", 700),
    ("assert len(nums) > 0", 400),
    ("return dp[-1]", 300),
    ("stack.append(node)", 300),
    ("visited = set()", 300),
    ("memo = {}", 300),
    ("class Solution:", 500),
    ("try:", 300),
    ("if x > 0 and y < 10:", 500),
    ("while left < right:", 500),
    ("for i, val in enumerate(nums):", 600),
    # --- medium: comprehensions, lambdas, f-strings, common APIs ---
    ("squares = [x**2 for x in range(10)]", 700),
    ("evens = [x for x in nums if x % 2 == 0]", 800),
    ("pairs = list(zip(a, b))", 700),
    ("sorted_items = sorted(items, key=lambda x: x[1])", 900),
    ("result = a if condition else b", 700),
    ('s = f"{name}: {value:.2f}"', 800),
    ("flattened = [x for row in matrix for x in row]", 1000),
    ("return [i for i, x in enumerate(nums) if x == target]", 1000),
    ("graph = collections.defaultdict(list)", 800),
    ("heapq.heappush(heap, (-freq, num))", 900),
    ("q = collections.deque()", 600),
    ("count = collections.Counter(words)", 700),
    ("nums.sort(key=lambda x: -x)", 800),
    ("results = [y for x in data if (y := f(x)) is not None]", 1100),
    ("@functools.lru_cache(maxsize=None)", 900),
    ("def __init__(self, val=0, next=None):", 900),
    # --- multi-line snippets (also drive Reaction mode) ---
    (
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for i, num in enumerate(nums):\n"
        "        complement = target - num\n"
        "        if complement in seen:\n"
        "            return [seen[complement], i]\n"
        "        seen[num] = i\n"
        "    return []",
        1400,
    ),
    (
        "def binary_search(nums, target):\n"
        "    left, right = 0, len(nums) - 1\n"
        "    while left <= right:\n"
        "        mid = (left + right) // 2\n"
        "        if nums[mid] == target:\n"
        "            return mid\n"
        "        elif nums[mid] < target:\n"
        "            left = mid + 1\n"
        "        else:\n"
        "            right = mid - 1\n"
        "    return -1",
        1400,
    ),
    (
        "def reverse_list(head):\n"
        "    prev = None\n"
        "    while head:\n"
        "        next_node = head.next\n"
        "        head.next = prev\n"
        "        prev = head\n"
        "        head = next_node\n"
        "    return prev",
        1300,
    ),
    (
        "def dfs(graph, start, visited=None):\n"
        "    if visited is None:\n"
        "        visited = set()\n"
        "    visited.add(start)\n"
        "    for neighbor in graph[start]:\n"
        "        if neighbor not in visited:\n"
        "            dfs(graph, neighbor, visited)\n"
        "    return visited",
        1500,
    ),
    (
        "@functools.lru_cache(maxsize=None)\n"
        "def fib(n):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 2)",
        1000,
    ),
    (
        "def partition(nums, low, high):\n"
        "    pivot = nums[high]\n"
        "    i = low - 1\n"
        "    for j in range(low, high):\n"
        "        if nums[j] <= pivot:\n"
        "            i += 1\n"
        "            nums[i], nums[j] = nums[j], nums[i]\n"
        "    nums[i + 1], nums[high] = nums[high], nums[i + 1]\n"
        "    return i + 1",
        1700,
    ),
    (
        "def max_subarray_sum(nums, k):\n"
        "    window_sum = sum(nums[:k])\n"
        "    max_sum = window_sum\n"
        "    for i in range(k, len(nums)):\n"
        "        window_sum += nums[i] - nums[i - k]\n"
        "        max_sum = max(max_sum, window_sum)\n"
        "    return max_sum",
        1400,
    ),
    (
        "class ListNode:\n"
        "    def __init__(self, val=0, next=None):\n"
        "        self.val = val\n"
        "        self.next = next",
        900,
    ),
    (
        "class Timer:\n"
        "    def __enter__(self):\n"
        "        self.start = time.time()\n"
        "        return self\n"
        "\n"
        "    def __exit__(self, *args):\n"
        "        self.elapsed = time.time() - self.start",
        1300,
    ),
    (
        "def merge_sort(nums):\n"
        "    if len(nums) <= 1:\n"
        "        return nums\n"
        "    mid = len(nums) // 2\n"
        "    left = merge_sort(nums[:mid])\n"
        "    right = merge_sort(nums[mid:])\n"
        "    return merge(left, right)",
        1500,
    ),
    (
        "def retry(times=3):\n"
        "    def decorator(func):\n"
        "        def wrapper(*args, **kwargs):\n"
        "            for attempt in range(times):\n"
        "                try:\n"
        "                    return func(*args, **kwargs)\n"
        "                except Exception:\n"
        "                    continue\n"
        "        return wrapper\n"
        "    return decorator",
        1900,
    ),
    (
        "def is_valid_parens(s):\n"
        "    stack = []\n"
        "    pairs = {')': '(', ']': '[', '}': '{'}\n"
        "    for char in s:\n"
        "        if char in pairs.values():\n"
        "            stack.append(char)\n"
        "        elif not stack or stack.pop() != pairs[char]:\n"
        "            return False\n"
        "    return not stack",
        1600,
    ),
]
