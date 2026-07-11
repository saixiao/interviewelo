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
    (
        300,
        "python",
        "def middle_element(nums):\n"
        "    return nums[len(nums) // 2]",
        "o1",
        "o1",
        "List indexing and `len()` are both constant-time operations, so no work scales with input "
        "size -- O(1) time. No new structures are allocated -- O(1) space.",
    ),
    (
        320,
        "python",
        "def index_of(nums, target):\n"
        "    for i in range(len(nums)):\n"
        "        if nums[i] == target:\n"
        "            return i\n"
        "    return -1",
        "on",
        "o1",
        "Linear search may examine every one of the n elements before finding the target (or giving "
        "up) -- O(n) time. Only the loop index is stored -- O(1) space.",
    ),
    (
        340,
        "python",
        "def maximum(nums):\n"
        "    best = nums[0]\n"
        "    for n in nums:\n"
        "        if n > best:\n"
        "            best = n\n"
        "    return best",
        "on",
        "o1",
        "One comparison per element over a single pass -- O(n) time. A single `best` variable is the "
        "only extra state -- O(1) space.",
    ),
    (
        360,
        "python",
        "def count_vowels(s):\n"
        "    count = 0\n"
        "    for ch in s:\n"
        "        if ch in 'aeiou':\n"
        "            count += 1\n"
        "    return count",
        "on",
        "o1",
        "One pass over the string, and the membership test against the fixed 5-character string "
        "'aeiou' is constant work per character -- O(n) time. Just one counter -- O(1) space.",
    ),
    (
        400,
        "python",
        "def is_sorted(nums):\n"
        "    for i in range(len(nums) - 1):\n"
        "        if nums[i] > nums[i + 1]:\n"
        "            return False\n"
        "    return True",
        "on",
        "o1",
        "In the worst case (a sorted list) all n-1 adjacent pairs are compared -- O(n) time. Only the "
        "loop index is kept -- O(1) space.",
    ),
    (
        420,
        "python",
        "def min_and_max(nums):\n"
        "    lo = hi = nums[0]\n"
        "    for n in nums:\n"
        "        if n < lo:\n"
        "            lo = n\n"
        "        if n > hi:\n"
        "            hi = n\n"
        "    return lo, hi",
        "on",
        "o1",
        "A single pass with two comparisons per element -- O(n) time. Two scalar variables regardless "
        "of input size -- O(1) space.",
    ),
    (
        450,
        "python",
        "def squares(nums):\n"
        "    return [x * x for x in nums]",
        "on",
        "on",
        "One multiplication per element -- O(n) time. The comprehension builds a brand-new n-element "
        "list rather than mutating the input, so the output allocation makes it O(n) space.",
    ),
    (
        480,
        "python",
        "def is_palindrome(s):\n"
        "    i, j = 0, len(s) - 1\n"
        "    while i < j:\n"
        "        if s[i] != s[j]:\n"
        "            return False\n"
        "        i += 1\n"
        "        j -= 1\n"
        "    return True",
        "on",
        "o1",
        "The two pointers meet in the middle after n/2 comparisons -- O(n) time. No copy of the "
        "string is made, just two indices -- O(1) space (contrast with checking `s == s[::-1]`, "
        "which would allocate an n-character copy).",
    ),
    (
        520,
        "python",
        "def reverse_in_place(nums):\n"
        "    i, j = 0, len(nums) - 1\n"
        "    while i < j:\n"
        "        nums[i], nums[j] = nums[j], nums[i]\n"
        "        i += 1\n"
        "        j -= 1",
        "on",
        "o1",
        "n/2 swaps as the pointers converge -- O(n) time. The list is mutated in place with no new "
        "allocation -- O(1) space, unlike a slicing reverse which copies all n elements.",
    ),
    (
        560,
        "python",
        "def word_counts(words):\n"
        "    counts = {}\n"
        "    for w in words:\n"
        "        counts[w] = counts.get(w, 0) + 1\n"
        "    return counts",
        "on",
        "on",
        "One dict get/set (O(1) average) per word over a single pass -- O(n) time. The `counts` dict "
        "can hold one entry per distinct word, up to n entries when all words differ -- O(n) space.",
    ),
    (
        600,
        "python",
        "def intersection(a, b):\n"
        "    seen = set(a)\n"
        "    return [x for x in b if x in seen]",
        "on",
        "on",
        "Building the set is one pass over `a` and the comprehension is one pass over `b` with O(1) "
        "average membership checks -- O(n) time for total input size n. The set (and the result list) "
        "can hold up to n elements -- O(n) space.",
    ),
    (
        640,
        "python",
        "def merge(a, b):\n"
        "    result = []\n"
        "    i = j = 0\n"
        "    while i < len(a) and j < len(b):\n"
        "        if a[i] <= b[j]:\n"
        "            result.append(a[i])\n"
        "            i += 1\n"
        "        else:\n"
        "            result.append(b[j])\n"
        "            j += 1\n"
        "    result.extend(a[i:])\n"
        "    result.extend(b[j:])\n"
        "    return result",
        "on",
        "on",
        "The merge step of merge sort in isolation: each element of the two sorted inputs is appended "
        "exactly once, so for total input size n it is O(n) time. The merged output list holds all n "
        "elements -- O(n) space.",
    ),
    (
        660,
        "python",
        "def print_pairs(nums):\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i + 1, len(nums)):\n"
        "            print(nums[i], nums[j])",
        "on2",
        "o1",
        "The nested loops visit every unordered pair, about n^2/2 iterations -- O(n^2) time. Nothing "
        "is stored -- each pair is printed and discarded, so space stays O(1).",
    ),
    (
        680,
        "python",
        "def bubble_sort(nums):\n"
        "    n = len(nums)\n"
        "    for i in range(n):\n"
        "        for j in range(n - 1 - i):\n"
        "            if nums[j] > nums[j + 1]:\n"
        "                nums[j], nums[j + 1] = nums[j + 1], nums[j]",
        "on2",
        "o1",
        "The nested loops always perform about n^2/2 comparisons (there is no early exit) -- O(n^2) "
        "time. Sorting happens by swapping in place -- O(1) space.",
    ),
    (
        700,
        "python",
        "def move_zeroes(nums):\n"
        "    write = 0\n"
        "    for read in range(len(nums)):\n"
        "        if nums[read] != 0:\n"
        "            nums[write], nums[read] = nums[read], nums[write]\n"
        "            write += 1",
        "on",
        "o1",
        "A single read pointer sweeps the list once, swapping non-zero values forward -- O(n) time. "
        "The rearrangement is done in place with two index variables -- O(1) space.",
    ),
    (
        720,
        "python",
        "def selection_sort(nums):\n"
        "    n = len(nums)\n"
        "    for i in range(n):\n"
        "        smallest = i\n"
        "        for j in range(i + 1, n):\n"
        "            if nums[j] < nums[smallest]:\n"
        "                smallest = j\n"
        "        nums[i], nums[smallest] = nums[smallest], nums[i]",
        "on2",
        "o1",
        "Finding each minimum scans the remaining suffix, giving n + (n-1) + ... + 1 comparisons "
        "regardless of input order -- O(n^2) time. Only index variables and in-place swaps -- O(1) "
        "space.",
    ),
    (
        750,
        "python",
        "def digit_sum(n):\n"
        "    total = 0\n"
        "    while n > 0:\n"
        "        total += n % 10\n"
        "        n //= 10\n"
        "    return total",
        "olog_n",
        "o1",
        "Each iteration strips one decimal digit, and a number n has about log10(n) digits -- O(log n) "
        "time. Two scalar variables -- O(1) space.",
    ),
    (
        780,
        "python",
        "def insertion_sort(nums):\n"
        "    for i in range(1, len(nums)):\n"
        "        key = nums[i]\n"
        "        j = i - 1\n"
        "        while j >= 0 and nums[j] > key:\n"
        "            nums[j + 1] = nums[j]\n"
        "            j -= 1\n"
        "        nums[j + 1] = key",
        "on2",
        "o1",
        "In the worst case (reverse-sorted input) each element shifts past all elements before it, "
        "about n^2/2 moves -- O(n^2) time. Shifting happens inside the input list -- O(1) space.",
    ),
    (
        800,
        "python",
        "def middle_node(head):\n"
        "    slow = fast = head\n"
        "    while fast is not None and fast.next is not None:\n"
        "        slow = slow.next\n"
        "        fast = fast.next.next\n"
        "    return slow",
        "on",
        "o1",
        "The fast pointer traverses the whole n-node list while the slow pointer covers half -- O(n) "
        "time. Only two node references are held, no matter how long the list is -- O(1) space.",
    ),
    (
        820,
        "python",
        "def is_anagram(a, b):\n"
        "    return sorted(a) == sorted(b)",
        "on_log_n",
        "on",
        "Each call to `sorted()` is a comparison sort costing O(n log n), which dominates the final "
        "O(n) equality check. `sorted()` returns a new n-element list for each string (it does not "
        "sort in place) -- O(n) space.",
    ),
    (
        850,
        "python",
        "def first_unique_char(s):\n"
        "    counts = {}\n"
        "    for ch in s:\n"
        "        counts[ch] = counts.get(ch, 0) + 1\n"
        "    for i, ch in enumerate(s):\n"
        "        if counts[ch] == 1:\n"
        "            return i\n"
        "    return -1",
        "on",
        "on",
        "Two sequential passes with O(1) average dict operations each -- O(n) time. The counts dict "
        "can hold one entry per distinct character, up to n when all characters differ -- O(n) space.",
    ),
    (
        880,
        "python",
        "def contains_duplicate_sorted(nums):\n"
        "    ordered = sorted(nums)\n"
        "    for i in range(len(ordered) - 1):\n"
        "        if ordered[i] == ordered[i + 1]:\n"
        "            return True\n"
        "    return False",
        "on_log_n",
        "on",
        "The sort-based duplicate check is dominated by the O(n log n) comparison sort; the adjacent "
        "scan afterwards is only O(n). `sorted()` allocates a new n-element list -- O(n) space "
        "(contrast with the hash-set approach: O(n) time but the same O(n) space).",
    ),
    (
        900,
        "python",
        "def all_pairs(nums):\n"
        "    pairs = []\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i + 1, len(nums)):\n"
        "            pairs.append((nums[i], nums[j]))\n"
        "    return pairs",
        "on2",
        "on2",
        "The nested loops produce about n^2/2 pairs -- O(n^2) time. Unlike a version that just prints "
        "each pair, every pair is stored in `pairs`, so the output itself is O(n^2) space.",
    ),
    (
        920,
        "python",
        "def prefix_sums(nums):\n"
        "    prefix = [0]\n"
        "    for n in nums:\n"
        "        prefix.append(prefix[-1] + n)\n"
        "    return prefix",
        "on",
        "on",
        "One addition and one append per element -- O(n) time. The prefix array holds n+1 running "
        "totals -- O(n) space.",
    ),
    (
        950,
        "python",
        "def max_window_sum(nums, k):\n"
        "    window = 0\n"
        "    for i in range(k):\n"
        "        window += nums[i]\n"
        "    best = window\n"
        "    for i in range(k, len(nums)):\n"
        "        window += nums[i] - nums[i - k]\n"
        "        if window > best:\n"
        "            best = window\n"
        "    return best",
        "on",
        "o1",
        "The sliding window adds each entering element and subtracts each leaving one exactly once, "
        "so the whole list is touched O(n) times total -- no re-summing of the window. Only the "
        "running `window` and `best` scalars are stored -- O(1) space.",
    ),
    (
        950,
        "python",
        "def first_occurrence(sorted_nums, target):\n"
        "    lo, hi = 0, len(sorted_nums) - 1\n"
        "    result = -1\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if sorted_nums[mid] == target:\n"
        "            result = mid\n"
        "            hi = mid - 1\n"
        "        elif sorted_nums[mid] < target:\n"
        "            lo = mid + 1\n"
        "        else:\n"
        "            hi = mid - 1\n"
        "    return result",
        "olog_n",
        "o1",
        "Even on a match the search keeps going left, but every iteration still halves the range, so "
        "it is O(log n) time like plain binary search. A few index variables -- O(1) space.",
    ),
    (
        1000,
        "python",
        "def max_subarray(nums):\n"
        "    best = current = nums[0]\n"
        "    for i in range(1, len(nums)):\n"
        "        current = max(nums[i], current + nums[i])\n"
        "        best = max(best, current)\n"
        "    return best",
        "on",
        "o1",
        "Kadane's algorithm: one constant-time decision per element (extend the running subarray or "
        "restart) in a single pass -- O(n) time. Two scalars carry all the state -- O(1) space, no DP "
        "table needed.",
    ),
    (
        1000,
        "python",
        "def reverse_list(head):\n"
        "    prev = None\n"
        "    current = head\n"
        "    while current is not None:\n"
        "        nxt = current.next\n"
        "        current.next = prev\n"
        "        prev = current\n"
        "        current = nxt\n"
        "    return prev",
        "on",
        "o1",
        "Each of the n nodes has its pointer flipped exactly once -- O(n) time. The reversal rewires "
        "the existing nodes in place using three references -- O(1) space (no new list, no recursion "
        "stack).",
    ),
    (
        1050,
        "python",
        "def transpose(matrix):\n"
        "    n = len(matrix)\n"
        "    result = [[0] * n for _ in range(n)]\n"
        "    for i in range(n):\n"
        "        for j in range(n):\n"
        "            result[j][i] = matrix[i][j]\n"
        "    return result",
        "on2",
        "on2",
        "Every cell of the n x n matrix is copied once -- O(n^2) time. A whole new n x n matrix is "
        "allocated for the result -- O(n^2) space (an in-place transpose of a square matrix could do "
        "it in O(1) extra).",
    ),
    (
        1050,
        "python",
        "def climb_stairs(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    ways = [0] * (n + 1)\n"
        "    ways[0] = ways[1] = 1\n"
        "    for i in range(2, n + 1):\n"
        "        ways[i] = ways[i - 1] + ways[i - 2]\n"
        "    return ways[n]",
        "on",
        "on",
        "Bottom-up tabulation fills each of the n+1 table slots once with constant work -- O(n) time. "
        "The full `ways` table is kept even though only the last two entries are ever read -- O(n) "
        "space.",
    ),
    (
        1100,
        "python",
        "def has_zero_triplet(nums):\n"
        "    n = len(nums)\n"
        "    for i in range(n):\n"
        "        for j in range(i + 1, n):\n"
        "            for k in range(j + 1, n):\n"
        "                if nums[i] + nums[j] + nums[k] == 0:\n"
        "                    return True\n"
        "    return False",
        "on3",
        "o1",
        "Three nested loops enumerate every triple of indices, about n^3/6 checks in the worst case "
        "-- O(n^3) time. Only loop indices are stored -- O(1) space.",
    ),
    (
        1100,
        "python",
        "def product_except_self(nums):\n"
        "    n = len(nums)\n"
        "    result = [1] * n\n"
        "    left = 1\n"
        "    for i in range(n):\n"
        "        result[i] = left\n"
        "        left *= nums[i]\n"
        "    right = 1\n"
        "    for i in range(n - 1, -1, -1):\n"
        "        result[i] *= right\n"
        "        right *= nums[i]\n"
        "    return result",
        "on",
        "on",
        "Two linear passes accumulate prefix and suffix products -- O(n) time, avoiding the O(n^2) "
        "pair-wise approach. The n-element output array is the only structure that grows with input "
        "-- O(n) space.",
    ),
    (
        1150,
        "python",
        "def climb_stairs(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    prev, curr = 1, 1\n"
        "    for _ in range(2, n + 1):\n"
        "        prev, curr = curr, prev + curr\n"
        "    return curr",
        "on",
        "o1",
        "Same recurrence as the tabulated version, computed in n-1 loop iterations -- O(n) time. "
        "Because each step only needs the previous two values, two rolling variables replace the "
        "whole DP table -- O(1) space instead of O(n).",
    ),
    (
        1150,
        "python",
        "def majority_element(nums):\n"
        "    candidate = None\n"
        "    count = 0\n"
        "    for n in nums:\n"
        "        if count == 0:\n"
        "            candidate = n\n"
        "        count += 1 if n == candidate else -1\n"
        "    return candidate",
        "on",
        "o1",
        "Boyer-Moore voting makes one constant-time update per element in a single pass -- O(n) time. "
        "It tracks just a candidate and a counter, unlike the frequency-map approach which would use "
        "O(n) space -- here space is O(1).",
    ),
    (
        1200,
        "python",
        "def has_cycle(head):\n"
        "    slow = fast = head\n"
        "    while fast is not None and fast.next is not None:\n"
        "        slow = slow.next\n"
        "        fast = fast.next.next\n"
        "        if slow is fast:\n"
        "            return True\n"
        "    return False",
        "on",
        "o1",
        "Floyd's tortoise-and-hare: once both pointers are inside a cycle the fast one gains a step "
        "per iteration, so they meet within O(n) steps -- O(n) time. Two pointers replace the "
        "visited-set approach, which would cost O(n) space -- here space is O(1).",
    ),
    (
        1200,
        "python",
        "def longest_distinct_run(nums):\n"
        "    seen = set()\n"
        "    left = 0\n"
        "    best = 0\n"
        "    for right in range(len(nums)):\n"
        "        while nums[right] in seen:\n"
        "            seen.remove(nums[left])\n"
        "            left += 1\n"
        "        seen.add(nums[right])\n"
        "        best = max(best, right - left + 1)\n"
        "    return best",
        "on",
        "on",
        "Despite the nested while, each element is added to and removed from the window at most once, "
        "so total work is amortized O(n) time. The `seen` set can grow to hold all n elements when "
        "they are all distinct -- O(n) space.",
    ),
    (
        1250,
        "python",
        "def integer_sqrt(n):\n"
        "    lo, hi = 0, n\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if mid * mid <= n:\n"
        "            lo = mid + 1\n"
        "        else:\n"
        "            hi = mid - 1\n"
        "    return hi",
        "olog_n",
        "o1",
        "Binary search on the answer: the candidate range [0, n] halves each iteration -- O(log n) "
        "time even though there is no array. Three integer variables -- O(1) space.",
    ),
    (
        1250,
        "python",
        "def height(node):\n"
        "    if node is None:\n"
        "        return 0\n"
        "    return 1 + max(height(node.left), height(node.right))",
        "on",
        "on",
        "Every one of the n tree nodes is visited exactly once -- O(n) time. The recursion stack "
        "grows to the tree's height, which for a completely skewed tree is n frames -- O(n) space in "
        "the worst case (O(log n) only if the tree happens to be balanced).",
    ),
    (
        1300,
        "python",
        "def sort_scores(scores):\n"
        "    counts = [0] * 101\n"
        "    for s in scores:\n"
        "        counts[s] += 1\n"
        "    result = []\n"
        "    for value in range(101):\n"
        "        result.extend([value] * counts[value])\n"
        "    return result",
        "on",
        "on",
        "Counting sort over the fixed 0-100 score range: one tallying pass plus a rebuild pass over "
        "101 buckets -- O(n + 101) = O(n) time, beating comparison sorts. The 101-slot counts array "
        "is O(1), but the rebuilt output list holds all n scores -- O(n) space.",
    ),
    (
        1350,
        "python",
        "def inorder(root):\n"
        "    result = []\n"
        "    def visit(node):\n"
        "        if node is not None:\n"
        "            visit(node.left)\n"
        "            result.append(node.val)\n"
        "            visit(node.right)\n"
        "    visit(root)\n"
        "    return result",
        "on",
        "on",
        "Each of the n nodes is visited once with constant work -- O(n) time. The output list holds "
        "all n values, and the recursion stack can additionally reach depth n on a skewed tree -- "
        "O(n) space.",
    ),
    (
        1350,
        "python",
        "from collections import deque\n"
        "\n"
        "def level_order(root):\n"
        "    if root is None:\n"
        "        return []\n"
        "    result = []\n"
        "    queue = deque([root])\n"
        "    while queue:\n"
        "        node = queue.popleft()\n"
        "        result.append(node.val)\n"
        "        if node.left is not None:\n"
        "            queue.append(node.left)\n"
        "        if node.right is not None:\n"
        "            queue.append(node.right)\n"
        "    return result",
        "on",
        "on",
        "BFS enqueues and dequeues each of the n nodes exactly once with O(1) deque operations -- "
        "O(n) time. The queue can hold an entire level (up to n/2 nodes in a complete tree) and the "
        "result holds all n values -- O(n) space.",
    ),
    (
        1400,
        "python",
        "import heapq\n"
        "\n"
        "def heap_sort(nums):\n"
        "    heap = list(nums)\n"
        "    heapq.heapify(heap)\n"
        "    return [heapq.heappop(heap) for _ in range(len(nums))]",
        "on_log_n",
        "on",
        "`heapify` is O(n), but each of the n `heappop` calls costs O(log n) to sift the heap back "
        "down, so the pops dominate -- O(n log n) time. The input is copied into `heap` and a "
        "separate n-element sorted list is built -- O(n) space.",
    ),
    (
        1400,
        "python",
        "def unique_paths(n):\n"
        "    dp = [[1] * n for _ in range(n)]\n"
        "    for i in range(1, n):\n"
        "        for j in range(1, n):\n"
        "            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]\n"
        "    return dp[n - 1][n - 1]",
        "on2",
        "on2",
        "Counting monotone paths through an n x n grid: each of the n^2 cells is filled once with "
        "constant work -- O(n^2) time. The full 2D table is materialized -- O(n^2) space (a single "
        "rolling row would cut this to O(n)).",
    ),
    (
        1450,
        "python",
        "def preorder(root):\n"
        "    if root is None:\n"
        "        return []\n"
        "    result = []\n"
        "    stack = [root]\n"
        "    while stack:\n"
        "        node = stack.pop()\n"
        "        result.append(node.val)\n"
        "        if node.right is not None:\n"
        "            stack.append(node.right)\n"
        "        if node.left is not None:\n"
        "            stack.append(node.left)\n"
        "    return result",
        "on",
        "on",
        "The explicit stack replaces recursion, but each of the n nodes is still pushed and popped "
        "exactly once -- O(n) time. The stack plus the n-element result list scale with the tree "
        "size -- O(n) space.",
    ),
    (
        1450,
        "python",
        "def spiral_order(matrix):\n"
        "    n = len(matrix)\n"
        "    result = []\n"
        "    top, bottom, left, right = 0, n - 1, 0, n - 1\n"
        "    while top <= bottom and left <= right:\n"
        "        for j in range(left, right + 1):\n"
        "            result.append(matrix[top][j])\n"
        "        top += 1\n"
        "        for i in range(top, bottom + 1):\n"
        "            result.append(matrix[i][right])\n"
        "        right -= 1\n"
        "        if top <= bottom:\n"
        "            for j in range(right, left - 1, -1):\n"
        "                result.append(matrix[bottom][j])\n"
        "            bottom -= 1\n"
        "        if left <= right:\n"
        "            for i in range(bottom, top - 1, -1):\n"
        "                result.append(matrix[i][left])\n"
        "            left += 1\n"
        "    return result",
        "on2",
        "on2",
        "For an n x n matrix the spiral visits each of the n^2 cells exactly once -- O(n^2) time in "
        "the side length n. All n^2 values are appended to the output list -- O(n^2) space.",
    ),
    (
        1500,
        "python",
        "def power(base, exp):\n"
        "    if exp == 0:\n"
        "        return 1\n"
        "    half = power(base, exp // 2)\n"
        "    if exp % 2 == 0:\n"
        "        return half * half\n"
        "    return half * half * base",
        "olog_n",
        "olog_n",
        "Fast exponentiation: the exponent n halves on every call, so there are O(log n) calls with "
        "constant work each -- O(log n) time. Each call makes exactly one recursive call, so the "
        "stack is a single chain of O(log n) frames -- O(log n) space.",
    ),
    (
        1500,
        "python",
        "def search_rotated(nums, target):\n"
        "    lo, hi = 0, len(nums) - 1\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if nums[mid] == target:\n"
        "            return mid\n"
        "        if nums[lo] <= nums[mid]:\n"
        "            if nums[lo] <= target < nums[mid]:\n"
        "                hi = mid - 1\n"
        "            else:\n"
        "                lo = mid + 1\n"
        "        else:\n"
        "            if nums[mid] < target <= nums[hi]:\n"
        "                lo = mid + 1\n"
        "            else:\n"
        "                hi = mid - 1\n"
        "    return -1",
        "olog_n",
        "o1",
        "At least one half of any rotated sorted range is itself sorted, so each iteration can still "
        "discard half the range -- O(log n) time despite the rotation. Just index variables -- O(1) "
        "space.",
    ),
    (
        1550,
        "python",
        "def power(base, exp):\n"
        "    result = 1\n"
        "    while exp > 0:\n"
        "        if exp % 2 == 1:\n"
        "            result *= base\n"
        "        base *= base\n"
        "        exp //= 2\n"
        "    return result",
        "olog_n",
        "o1",
        "Iterative binary exponentiation halves the exponent n each loop iteration -- O(log n) time. "
        "Unlike the recursive version, which stacks O(log n) frames, this keeps only two scalars -- "
        "O(1) space.",
    ),
    (
        1550,
        "python",
        "def search_sorted_matrix(matrix, target):\n"
        "    n = len(matrix)\n"
        "    row, col = 0, n - 1\n"
        "    while row < n and col >= 0:\n"
        "        value = matrix[row][col]\n"
        "        if value == target:\n"
        "            return True\n"
        "        elif value > target:\n"
        "            col -= 1\n"
        "        else:\n"
        "            row += 1\n"
        "    return False",
        "on",
        "o1",
        "Staircase search on an n x n matrix with sorted rows and columns: starting at the top-right, "
        "every step permanently eliminates a row or a column, so at most 2n steps -- O(n) time in the "
        "side length n (not O(n^2)). Two index variables -- O(1) space.",
    ),
    (
        1600,
        "python",
        "def count_components(n, adj):\n"
        "    visited = set()\n"
        "    components = 0\n"
        "    for start in range(n):\n"
        "        if start in visited:\n"
        "            continue\n"
        "        components += 1\n"
        "        stack = [start]\n"
        "        visited.add(start)\n"
        "        while stack:\n"
        "            node = stack.pop()\n"
        "            for neighbor in adj[node]:\n"
        "                if neighbor not in visited:\n"
        "                    visited.add(neighbor)\n"
        "                    stack.append(neighbor)\n"
        "    return components",
        "on",
        "on",
        "DFS pushes each vertex once and scans each adjacency list once, so total work is O(V + E) -- "
        "linear in the size of the graph input, i.e. O(n). The visited set and stack can hold every "
        "vertex -- O(n) space.",
    ),
    (
        1600,
        "python",
        "def longest_increasing_subsequence(nums):\n"
        "    n = len(nums)\n"
        "    if n == 0:\n"
        "        return 0\n"
        "    lengths = [1] * n\n"
        "    for i in range(1, n):\n"
        "        for j in range(i):\n"
        "            if nums[j] < nums[i]:\n"
        "                lengths[i] = max(lengths[i], lengths[j] + 1)\n"
        "    return max(lengths)",
        "on2",
        "on",
        "For each position i the inner loop re-examines all j < i, about n^2/2 comparisons -- O(n^2) "
        "time for this classic DP formulation. The one-dimensional `lengths` table holds one entry "
        "per element -- O(n) space.",
    ),
    (
        1650,
        "python",
        "def count_palindromic_substrings(s):\n"
        "    n = len(s)\n"
        "    count = 0\n"
        "    for center in range(2 * n - 1):\n"
        "        left = center // 2\n"
        "        right = left + center % 2\n"
        "        while left >= 0 and right < n and s[left] == s[right]:\n"
        "            count += 1\n"
        "            left -= 1\n"
        "            right += 1\n"
        "    return count",
        "on2",
        "o1",
        "There are 2n-1 palindrome centers and each expansion can run up to n/2 steps (e.g. a string "
        "of all identical characters) -- O(n^2) time in the worst case. Only counters and indices "
        "are stored, no DP table -- O(1) space.",
    ),
    (
        1650,
        "python",
        "def min_path_sum(grid):\n"
        "    n = len(grid)\n"
        "    for i in range(n):\n"
        "        for j in range(n):\n"
        "            if i == 0 and j == 0:\n"
        "                continue\n"
        "            if i == 0:\n"
        "                grid[i][j] += grid[i][j - 1]\n"
        "            elif j == 0:\n"
        "                grid[i][j] += grid[i - 1][j]\n"
        "            else:\n"
        "                grid[i][j] += min(grid[i - 1][j], grid[i][j - 1])\n"
        "    return grid[n - 1][n - 1]",
        "on2",
        "o1",
        "Each of the n^2 cells of the n x n grid is updated once with constant work -- O(n^2) time. "
        "The DP writes its results directly into the input grid instead of allocating a table, so "
        "extra space is O(1) -- the in-place counterpart of the usual O(n^2)-space version.",
    ),
    (
        1700,
        "python",
        "def rotate_90(matrix):\n"
        "    n = len(matrix)\n"
        "    for i in range(n):\n"
        "        for j in range(i + 1, n):\n"
        "            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n"
        "    for row in matrix:\n"
        "        row.reverse()",
        "on2",
        "o1",
        "Transpose-then-reverse touches each of the n^2 cells a constant number of times -- O(n^2) "
        "time in the side length n. Both the transpose swaps and `row.reverse()` mutate the matrix "
        "in place -- O(1) space, versus O(n^2) for building a rotated copy.",
    ),
    (
        1700,
        "python",
        "from collections import deque\n"
        "\n"
        "def shortest_path_length(adj, start, goal):\n"
        "    dist = {start: 0}\n"
        "    queue = deque([start])\n"
        "    while queue:\n"
        "        node = queue.popleft()\n"
        "        if node == goal:\n"
        "            return dist[node]\n"
        "        for neighbor in adj[node]:\n"
        "            if neighbor not in dist:\n"
        "                dist[neighbor] = dist[node] + 1\n"
        "                queue.append(neighbor)\n"
        "    return -1",
        "on",
        "on",
        "BFS on an unweighted adjacency-list graph visits each vertex and scans each edge at most "
        "once -- O(V + E), linear in the input size n. The dist map and queue can grow to hold every "
        "vertex -- O(n) space.",
    ),
    (
        1750,
        "python",
        "def diameter(root):\n"
        "    best = 0\n"
        "    def height(node):\n"
        "        nonlocal best\n"
        "        if node is None:\n"
        "            return 0\n"
        "        left = height(node.left)\n"
        "        right = height(node.right)\n"
        "        best = max(best, left + right)\n"
        "        return 1 + max(left, right)\n"
        "    height(root)\n"
        "    return best",
        "on",
        "on",
        "A single post-order pass computes each node's height once and updates the diameter as a side "
        "effect -- O(n) time, avoiding the naive recompute-height-per-node O(n^2). The recursion "
        "stack can reach depth n on a skewed tree -- O(n) worst-case space.",
    ),
    (
        1800,
        "python",
        "def has_cycle(n, adj):\n"
        "    state = [0] * n\n"
        "    def dfs(node):\n"
        "        state[node] = 1\n"
        "        for neighbor in adj[node]:\n"
        "            if state[neighbor] == 1:\n"
        "                return True\n"
        "            if state[neighbor] == 0 and dfs(neighbor):\n"
        "                return True\n"
        "        state[node] = 2\n"
        "        return False\n"
        "    return any(state[v] == 0 and dfs(v) for v in range(n))",
        "on",
        "on",
        "Three-color DFS for a directed graph: each vertex is fully explored once and each edge "
        "checked once -- O(V + E), linear in the input size n. The state array plus a recursion "
        "stack that can span all n vertices -- O(n) space.",
    ),
    (
        1800,
        "python",
        "def hanoi(n, source, spare, target):\n"
        "    if n == 0:\n"
        "        return\n"
        "    hanoi(n - 1, source, target, spare)\n"
        "    print(source, '->', target)\n"
        "    hanoi(n - 1, spare, source, target)",
        "o2n",
        "on",
        "Tower of Hanoi obeys T(n) = 2T(n-1) + 1 = 2^n - 1 moves, each printed once -- O(2^n) time. "
        "Although the call tree has 2^n nodes, the stack only ever holds one root-to-leaf chain of n "
        "pending calls -- O(n) space.",
    ),
    (
        1850,
        "python",
        "def longest_palindromic_subsequence(s):\n"
        "    n = len(s)\n"
        "    if n == 0:\n"
        "        return 0\n"
        "    dp = [[0] * n for _ in range(n)]\n"
        "    for i in range(n - 1, -1, -1):\n"
        "        dp[i][i] = 1\n"
        "        for j in range(i + 1, n):\n"
        "            if s[i] == s[j]:\n"
        "                dp[i][j] = dp[i + 1][j - 1] + 2\n"
        "            else:\n"
        "                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])\n"
        "    return dp[0][n - 1]",
        "on2",
        "on2",
        "Interval DP over every (i, j) substring pair: about n^2/2 cells, each filled with constant "
        "work -- O(n^2) time. The full n x n table is materialized -- O(n^2) space.",
    ),
    (
        1900,
        "python",
        "from collections import deque\n"
        "\n"
        "def topological_order(n, adj):\n"
        "    indegree = [0] * n\n"
        "    for node in range(n):\n"
        "        for neighbor in adj[node]:\n"
        "            indegree[neighbor] += 1\n"
        "    queue = deque(v for v in range(n) if indegree[v] == 0)\n"
        "    order = []\n"
        "    while queue:\n"
        "        node = queue.popleft()\n"
        "        order.append(node)\n"
        "        for neighbor in adj[node]:\n"
        "            indegree[neighbor] -= 1\n"
        "            if indegree[neighbor] == 0:\n"
        "                queue.append(neighbor)\n"
        "    return order",
        "on",
        "on",
        "Kahn's algorithm: computing in-degrees scans every edge once, and the main loop dequeues "
        "each vertex once and decrements along each edge once -- O(V + E), linear in the input size "
        "n. The indegree array, queue, and output order all scale with the vertex count -- O(n) "
        "space.",
    ),
    (
        1950,
        "python",
        "def subsets(nums):\n"
        "    result = [[]]\n"
        "    for n in nums:\n"
        "        result += [subset + [n] for subset in result]\n"
        "    return result",
        "o2n",
        "o2n",
        "Each element doubles the number of subsets built so far, ending with all 2^n subsets -- "
        "O(2^n) time (the copying makes it O(n * 2^n) in fine detail, still exponential and keyed as "
        "2^n). All 2^n subsets are held in `result` simultaneously -- O(2^n) space.",
    ),
    (
        2050,
        "python",
        "def count_subsets_with_sum(nums, target):\n"
        "    def count(i, remaining):\n"
        "        if i == len(nums):\n"
        "            return 1 if remaining == 0 else 0\n"
        "        return count(i + 1, remaining) + count(i + 1, remaining - nums[i])\n"
        "    return count(0, target)",
        "o2n",
        "on",
        "Each element branches into include/exclude with no memoization, so the call tree has 2^n "
        "leaves -- O(2^n) time. Unlike the subset-generating version, nothing is stored: the stack "
        "holds only one include/exclude path of depth n at a time -- O(n) space.",
    ),
    (
        2150,
        "python",
        "def all_pairs_shortest(dist):\n"
        "    n = len(dist)\n"
        "    result = [row[:] for row in dist]\n"
        "    for k in range(n):\n"
        "        for i in range(n):\n"
        "            for j in range(n):\n"
        "                if result[i][k] + result[k][j] < result[i][j]:\n"
        "                    result[i][j] = result[i][k] + result[k][j]\n"
        "    return result",
        "on3",
        "on2",
        "Floyd-Warshall relaxes every (i, j) pair through every intermediate vertex k -- three nested "
        "loops over n vertices, O(n^3) time. The copied distance matrix holds n^2 entries -- O(n^2) "
        "space.",
    ),
    (
        2300,
        "python",
        "def count_n_queens(n):\n"
        "    cols, diag1, diag2 = set(), set(), set()\n"
        "    def place(row):\n"
        "        if row == n:\n"
        "            return 1\n"
        "        total = 0\n"
        "        for col in range(n):\n"
        "            if col in cols or row + col in diag1 or row - col in diag2:\n"
        "                continue\n"
        "            cols.add(col)\n"
        "            diag1.add(row + col)\n"
        "            diag2.add(row - col)\n"
        "            total += place(row + 1)\n"
        "            cols.remove(col)\n"
        "            diag1.remove(row + col)\n"
        "            diag2.remove(row - col)\n"
        "        return total\n"
        "    return place(0)",
        "on_fact",
        "on",
        "Row-by-row backtracking: the first row has n column choices, the next at most n-1, and so "
        "on, so even with the O(1) set-based pruning the search tree is bounded by n * (n-1) * ... "
        "-- O(n!) time. The three sets and the recursion stack each hold at most n entries, since "
        "state is undone on backtrack -- O(n) space.",
    ),
    (
        2450,
        "python",
        "from itertools import permutations\n"
        "\n"
        "def shortest_tour(dist):\n"
        "    n = len(dist)\n"
        "    if n == 1:\n"
        "        return 0\n"
        "    best = None\n"
        "    for order in permutations(range(1, n)):\n"
        "        cost = dist[0][order[0]]\n"
        "        for i in range(len(order) - 1):\n"
        "            cost += dist[order[i]][order[i + 1]]\n"
        "        cost += dist[order[-1]][0]\n"
        "        if best is None or cost < best:\n"
        "            best = cost\n"
        "    return best",
        "on_fact",
        "on",
        "Brute-force TSP evaluates all (n-1)! visiting orders, each costing O(n) to sum -- O(n!) "
        "time. Crucially, `itertools.permutations` is a lazy generator yielding one n-1 length tuple "
        "at a time and only `best` is retained, so space is O(n), not O(n!).",
    ),
]
