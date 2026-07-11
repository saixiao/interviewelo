"""Seed content for the Quick-Fire Approach round. `difficulty` is an
Elo-scale content-difficulty rating (same scale as user ratings), roughly
anchored to easy=800, medium=1400, hard=2000 per CLAUDE.md. `grading_notes_md`
is the intended optimal approach the judge grades against -- never sent to
the client.
"""

PROMPTS: list[tuple[str, int, str, str]] = [
    (
        "Two Sum",
        700,
        "Given an array of integers `nums` and an integer `target`, return the indices of the "
        "two numbers that add up to `target`. Assume exactly one solution exists.",
        "Single pass with a hash map from value -> index. For each num, check if "
        "`target - num` is already in the map; if so return the pair, otherwise insert num. "
        "O(n) time, O(n) space. A correct answer should not describe the O(n^2) brute-force "
        "nested-loop approach as the primary solution (mentioning it as a naive baseline before "
        "improving is fine).",
    ),
    (
        "Valid Parentheses",
        600,
        "Given a string containing just the characters `(`, `)`, `{`, `}`, `[`, `]`, determine if "
        "the input string is valid (every opening bracket is closed by the same type, in the "
        "correct order).",
        "Use a stack. Push opening brackets; on a closing bracket, pop and check it matches the "
        "expected opener -- if the stack is empty or it doesn't match, the string is invalid. "
        "At the end the stack must be empty. O(n) time, O(n) space. Edge cases: empty string is "
        "valid, unmatched closing bracket with empty stack, leftover openers at the end.",
    ),
    (
        "Reverse a Linked List",
        700,
        "Given the head of a singly linked list, reverse the list and return the new head.",
        "Iterative approach: walk the list with `prev = None`, `curr = head`; at each step save "
        "`next = curr.next`, set `curr.next = prev`, then advance `prev = curr`, `curr = next`. "
        "Return `prev` at the end. O(n) time, O(1) space. A recursive O(n) time / O(n) space "
        "(call stack) solution is also correct and should be credited. Edge cases: empty list, "
        "single-node list.",
    ),
    (
        "Maximum Subarray",
        1000,
        "Given an integer array `nums`, find the contiguous subarray with the largest sum and "
        "return that sum.",
        "Kadane's algorithm: track `current_sum` and `best_sum`. At each element, "
        "`current_sum = max(num, current_sum + num)` (start a new subarray if the running sum "
        "would hurt more than the element alone), then `best_sum = max(best_sum, current_sum)`. "
        "O(n) time, O(1) space. Must handle all-negative arrays correctly (answer is the least "
        "negative single element, not 0).",
    ),
    (
        "Merge Two Sorted Lists",
        800,
        "Merge two sorted linked lists into one sorted linked list by splicing the nodes together.",
        "Use a dummy head node and a tail pointer. Repeatedly compare the current nodes of both "
        "lists, attach the smaller to `tail.next`, and advance that list's pointer. When one list "
        "is exhausted, attach the remainder of the other. O(n+m) time, O(1) extra space (reuses "
        "existing nodes). Edge cases: one or both lists empty.",
    ),
    (
        "Best Time to Buy and Sell Stock",
        800,
        "Given an array `prices` where `prices[i]` is the price on day i, find the maximum profit "
        "from buying on one day and selling on a later day (or 0 if no profit is possible).",
        "Single pass tracking the minimum price seen so far and the best profit so far. At each "
        "day, update `max_profit = max(max_profit, price - min_price_so_far)`, then update "
        "`min_price_so_far`. O(n) time, O(1) space. The key insight to look for: you never need "
        "to consider selling before the current minimum, so a single forward pass suffices "
        "instead of checking all pairs (O(n^2)).",
    ),
    (
        "Contains Duplicate",
        400,
        "Given an integer array, return true if any value appears at least twice, false if every "
        "element is distinct.",
        "Insert elements into a hash set one at a time; if an element is already present, return "
        "true immediately. O(n) time, O(n) space. An acceptable alternative: sort the array "
        "(O(n log n)) and check adjacent elements for equality, trading space for time -- should "
        "still be credited but the hash-set approach is preferred.",
    ),
    (
        "Group Anagrams",
        1100,
        "Given an array of strings, group the anagrams together (words made of the same letters "
        "in a different order).",
        "Use a hash map keyed by a canonical form of each word -- either the sorted character "
        "string or a 26-length letter-count tuple -- mapping to a list of original words with "
        "that key. One pass building the map, O(n * k log k) time if sorting each word of length "
        "k (or O(n*k) with counting), O(n*k) space. The canonicalization step is the key insight.",
    ),
    (
        "Number of Islands",
        1300,
        "Given a 2D grid of '1's (land) and '0's (water), count the number of islands (connected "
        "groups of land, connected horizontally or vertically).",
        "Scan every cell; whenever an unvisited '1' is found, increment the island count and run "
        "DFS or BFS from that cell, marking every connected land cell as visited (e.g. by "
        "flipping to '0' or using a separate visited set) so it isn't recounted. O(rows*cols) "
        "time and space. Must handle all four directions and not revisit cells.",
    ),
    (
        "Binary Search",
        500,
        "Given a sorted array of integers and a target value, return the index of the target, or "
        "-1 if it's not present.",
        "Standard binary search with `left`/`right` pointers, computing `mid = (left+right)//2` "
        "and narrowing the range based on comparison with `target`. O(log n) time, O(1) space. "
        "Correct loop condition (`left <= right`) and correct updates (`left = mid+1` / "
        "`right = mid-1`, not `mid`) to avoid infinite loops.",
    ),
    (
        "Climbing Stairs",
        700,
        "You can climb 1 or 2 steps at a time. Given `n` steps total, how many distinct ways are "
        "there to reach the top?",
        "This is Fibonacci in disguise: `ways(n) = ways(n-1) + ways(n-2)` (the last move is either "
        "a 1-step or a 2-step). Solve bottom-up with O(1) extra space by tracking only the last "
        "two values, achieving O(n) time, O(1) space -- an O(n) space DP array is also correct "
        "but not optimal. Base cases `ways(1)=1`, `ways(2)=2` should be handled correctly.",
    ),
    (
        "Linked List Cycle",
        800,
        "Given the head of a linked list, determine if the list has a cycle (a node's `next` "
        "eventually points back to a previous node in the list).",
        "Floyd's cycle detection (tortoise and hare): two pointers starting at head, `slow` moves "
        "one step and `fast` moves two steps per iteration. If they ever meet, there's a cycle; "
        "if `fast` reaches null, there isn't. O(n) time, O(1) space -- this is the key advantage "
        "over a hash-set-of-visited-nodes approach, which is O(n) space and also acceptable but "
        "not optimal.",
    ),
    (
        "Product of Array Except Self",
        1200,
        "Given an integer array `nums`, return an array where each element is the product of all "
        "other elements, without using division and in O(n) time.",
        "Two passes without division: build a `prefix` array where `prefix[i]` is the product of "
        "all elements before i, then a `suffix` product computed while iterating from the right, "
        "multiplying into the result as you go so the final output array holds `prefix[i] * "
        "suffix[i]`. Can be done with O(1) extra space beyond the output array by reusing it for "
        "prefixes then folding in suffixes in a second reverse pass. O(n) time.",
    ),
    (
        "Longest Substring Without Repeating Characters",
        1200,
        "Given a string, find the length of the longest substring without repeating characters.",
        "Sliding window with a hash set (or hash map of char -> last-seen index). Expand the "
        "window's right edge; if the new character is already in the window, shrink the left "
        "edge past its previous occurrence (using the map of last-seen indices avoids an inner "
        "while loop). Track the max window size seen. O(n) time, O(min(n, charset)) space. Must "
        "correctly move the left pointer to *after* the duplicate's previous position, not just "
        "to it.",
    ),
    (
        "Valid Anagram",
        400,
        "Given two strings, determine if the second is an anagram of the first (same letters, "
        "same counts, different order allowed).",
        "Count character frequencies in one string (hash map or fixed-size array for lowercase "
        "letters), then decrement while scanning the second string; if any count goes negative or "
        "a character isn't present, it's not an anagram. Also check lengths match first as a "
        "cheap early exit. O(n) time, O(1) or O(k) space depending on alphabet size. Sorting both "
        "strings and comparing (O(n log n)) is also correct but not optimal.",
    ),
    (
        "Merge Intervals",
        1300,
        "Given an array of intervals `[start, end]`, merge all overlapping intervals and return "
        "the non-overlapping intervals that cover all the input ranges.",
        "Sort intervals by start time, then do a single pass: keep a running 'current merged "
        "interval'; if the next interval's start is <= the current merged interval's end, extend "
        "the end (`max` of the two ends); otherwise push the current merged interval to the "
        "result and start a new one. O(n log n) time (dominated by the sort), O(n) space for the "
        "result. Sorting by start is the essential first step -- without it the single pass "
        "doesn't work.",
    ),
    (
        "Kth Largest Element in an Array",
        1300,
        "Given an integer array and an integer k, find the kth largest element in the array "
        "(the kth largest, not the kth distinct element).",
        "Optimal approaches: a min-heap of size k (push each element, pop the smallest once size "
        "exceeds k; the heap's remaining minimum is the answer), giving O(n log k) time, O(k) "
        "space -- or Quickselect for average O(n) time, O(1) extra space (worst case O(n^2) "
        "without randomization). Sorting the whole array (O(n log n)) and indexing is correct but "
        "not optimal for large n with small k.",
    ),
    (
        "Course Schedule (Cycle Detection in a Graph)",
        1500,
        "Given `numCourses` and a list of prerequisite pairs `[a, b]` meaning you must take b "
        "before a, determine if it's possible to finish all courses (i.e. the prerequisite graph "
        "has no cycle).",
        "Build a directed graph from prerequisites and run cycle detection: either DFS with a "
        "three-color/visited-state scheme (unvisited / in current recursion stack / fully done) "
        "to catch back-edges, or Kahn's algorithm (topological sort via BFS on in-degrees) -- if "
        "you can process all nodes via repeatedly removing zero-in-degree nodes, there's no "
        "cycle; if nodes remain, there is. O(V+E) time and space. Must distinguish 'visited in "
        "this DFS path' from 'visited overall' to correctly detect cycles vs. just revisiting a "
        "finished node via a different path.",
    ),
    (
        "Longest Increasing Subsequence",
        1600,
        "Given an integer array, return the length of the longest strictly increasing "
        "subsequence (elements don't need to be contiguous).",
        "O(n^2) DP: `dp[i]` = length of the longest increasing subsequence ending at index i, "
        "computed as `1 + max(dp[j] for j < i if nums[j] < nums[i])`, answer is `max(dp)`. The "
        "optimal O(n log n) approach maintains a `tails` array where `tails[k]` is the smallest "
        "possible tail value of an increasing subsequence of length k+1, using binary search to "
        "find where each new element belongs (patience sorting) -- crediting either approach, "
        "but flagging the O(n log n) one only if the candidate correctly describes binary search "
        "over the tails array, not just says 'it can be optimized'.",
    ),
    (
        "Word Search",
        1500,
        "Given a 2D grid of characters and a word, determine if the word can be constructed from "
        "letters of sequentially adjacent cells (horizontally or vertically), using each cell at "
        "most once.",
        "Backtracking DFS from every cell matching the word's first letter: at each step, try all "
        "four directions, mark the current cell as visited (e.g. temporarily overwrite it or use "
        "a visited set) before recursing on the next character, then unmark it on backtrack "
        "(explicit backtracking is required, not just visited-forever marking, since a cell can "
        "be reused on a different path). Base case: matched all characters, return true. Worst "
        "case O(rows*cols*4^L) where L is word length, due to branching at each step.",
    ),
]
