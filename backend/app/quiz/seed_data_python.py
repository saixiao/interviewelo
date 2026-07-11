"""Python-language-feature trivia for the python_trivia quiz category.

Each tuple is (topic, difficulty, prompt_md, choices, correct_keys,
multi_select, explanation_md). `choices` is a list of (key, label) pairs;
`correct_keys` references those keys and is always a list, even for
single-select. `difficulty` is Elo-scale, same convention as
approach_prompts.difficulty.

This is a starter set spanning the difficulty range so adaptive selection
has something to widen/narrow around immediately; the bank is meant to grow
to ~150-200 questions (see the quiz-modes phase plan).
"""

QUESTIONS: list[tuple[str, int, str, list[tuple[str, str]], list[str], bool, str]] = [
    (
        "equality",
        300,
        "What does `is` compare in Python, as opposed to `==`?",
        [
            ("a", "Object identity (same object in memory)"),
            ("b", "Value equality using __eq__"),
            ("c", "Type equality only"),
            ("d", "Hash equality"),
        ],
        ["a"],
        False,
        "`is` checks whether two names refer to the exact same object (id(a) == id(b)); "
        "`==` calls __eq__ and checks value equality, which types can customize.",
    ),
    (
        "f_strings",
        320,
        "When is the expression inside an f-string like f'{x + 1}' evaluated?",
        [
            ("a", "At function definition time"),
            ("b", "At runtime, when the f-string literal is executed"),
            ("c", "At import time, once, and cached"),
            ("d", "Never -- f-strings are only for simple variable substitution"),
        ],
        ["b"],
        False,
        "f-strings are syntactic sugar for building a string at the point they execute -- "
        "the embedded expression is evaluated every time that line runs, just like any other expression.",
    ),
    (
        "mutable_defaults",
        450,
        "def add(item, bucket=[]): bucket.append(item); return bucket\n\n"
        "What's the problem with this function?",
        [
            ("a", "The default list is created once at function-definition time and shared across calls"),
            ("b", "Lists can't be used as function parameters"),
            ("c", "append() doesn't work on default arguments"),
            ("d", "There is no problem, this is idiomatic Python"),
        ],
        ["a"],
        False,
        "Default argument values are evaluated exactly once, when the `def` statement runs -- "
        "so every call that doesn't pass `bucket` explicitly shares and mutates the same list object.",
    ),
    (
        "truthiness",
        500,
        "Which of these evaluate to False in a boolean context? (select all that apply)",
        [
            ("a", "[]"),
            ("b", "{}"),
            ("c", "0.0"),
            ("d", "\"0\" (the string containing a zero character)"),
            ("e", "None"),
        ],
        ["a", "b", "c", "e"],
        True,
        "Empty containers, 0/0.0, None, and False are all falsy. A non-empty string is always truthy "
        "regardless of its contents, so \"0\" is truthy -- a common gotcha.",
    ),
    (
        "args_kwargs",
        500,
        "In `def f(*args, **kwargs)`, what type is `args` inside the function body?",
        [
            ("a", "A tuple"),
            ("b", "A list"),
            ("c", "A dict"),
            ("d", "A generator"),
        ],
        ["a"],
        False,
        "*args collects extra positional arguments into a tuple; **kwargs collects extra keyword "
        "arguments into a dict.",
    ),
    (
        "generators",
        700,
        "What's the key difference between a list comprehension and an equivalent generator expression?",
        [
            ("a", "The generator computes items lazily, one at a time, instead of building the whole list up front"),
            ("b", "The generator expression is faster to iterate to completion"),
            ("c", "List comprehensions cannot contain conditionals"),
            ("d", "Generator expressions can only be used inside function calls"),
        ],
        ["a"],
        False,
        "A generator expression yields items on demand and holds only the current state in memory, "
        "trading some per-item overhead for not materializing the whole sequence -- valuable when the "
        "sequence is large or infinite.",
    ),
    (
        "gil",
        900,
        "What does the Global Interpreter Lock (GIL) actually prevent in CPython?",
        [
            ("a", "More than one native thread from executing Python bytecode at the same instant"),
            ("b", "Multiple processes from running Python at the same time"),
            ("c", "Any use of the `threading` module"),
            ("d", "Async coroutines from running concurrently"),
        ],
        ["a"],
        False,
        "The GIL serializes execution of Python bytecode across threads within one process -- "
        "so CPU-bound multithreading in CPython doesn't get real parallelism, while I/O-bound threads "
        "still benefit since the GIL is released during blocking I/O. multiprocessing sidesteps it by "
        "using separate processes/interpreters.",
    ),
    (
        "context_managers",
        950,
        "What must an object implement to be usable in a `with` statement?",
        [
            ("a", "__enter__ and __exit__"),
            ("b", "__init__ and __del__"),
            ("c", "__call__"),
            ("d", "__iter__ and __next__"),
        ],
        ["a"],
        False,
        "The context manager protocol is __enter__ (runs on entering the `with` block, its return value "
        "is bound by `as`) and __exit__ (always runs on exit, even if an exception was raised, and can "
        "suppress it by returning True).",
    ),
    (
        "closures",
        1000,
        "def make_counters():\n"
        "    counters = []\n"
        "    for i in range(3):\n"
        "        counters.append(lambda: i)\n"
        "    return counters\n\n"
        "What do `[c() for c in make_counters()]` return?",
        [
            ("a", "[2, 2, 2]"),
            ("b", "[0, 1, 2]"),
            ("c", "[0, 0, 0]"),
            ("d", "A TypeError"),
        ],
        ["a"],
        False,
        "Closures capture the variable `i`, not its value at lambda-creation time. By the time the "
        "lambdas are called, the loop has finished and `i` is 2 in the enclosing scope for all of them. "
        "The usual fix is a default argument: `lambda i=i: i`.",
    ),
    (
        "asyncio",
        1100,
        "What allows an `asyncio` event loop to run many coroutines on a single OS thread?",
        [
            ("a", "Coroutines voluntarily yield control at `await` points, letting the loop schedule other work"),
            ("b", "The event loop spawns a hidden OS thread per coroutine"),
            ("c", "The GIL is disabled while asyncio runs"),
            ("d", "Coroutines are preempted by the OS scheduler like threads"),
        ],
        ["a"],
        False,
        "asyncio is cooperative concurrency: a coroutine only gives up control at an `await`, so the "
        "loop can interleave many coroutines on one thread as long as none of them block synchronously.",
    ),
    (
        "slots",
        1400,
        "Defining `__slots__ = ('x', 'y')` on a class primarily trades away what, in exchange for lower "
        "per-instance memory use?",
        [
            ("a", "A per-instance __dict__ (and the ability to add arbitrary new attributes)"),
            ("b", "The ability to define methods"),
            ("c", "Inheritance"),
            ("d", "Support for properties"),
        ],
        ["a"],
        False,
        "Without __slots__, each instance normally gets its own __dict__ for attribute storage. "
        "__slots__ replaces that with fixed, fast attribute descriptors, saving memory at the cost of "
        "no arbitrary extra attributes (and some multiple-inheritance restrictions).",
    ),
    (
        "mro",
        1500,
        "What determines the order Python searches base classes when resolving an attribute under "
        "multiple inheritance?",
        [
            ("a", "The Method Resolution Order (MRO), computed via C3 linearization"),
            ("b", "Alphabetical order of class names"),
            ("c", "The order attributes were defined in the subclass"),
            ("d", "Depth-first search with no consistent ordering guarantee"),
        ],
        ["a"],
        False,
        "CPython uses C3 linearization to compute a consistent MRO (visible via `Cls.__mro__`) so "
        "`super()` calls follow a well-defined, monotonic order even in diamond-shaped hierarchies.",
    ),
    (
        "descriptors",
        1700,
        "`property` is built on top of which lower-level protocol?",
        [
            ("a", "The descriptor protocol (__get__/__set__/__delete__)"),
            ("b", "Metaclasses"),
            ("c", "Abstract base classes"),
            ("d", "The context manager protocol"),
        ],
        ["a"],
        False,
        "property() returns a descriptor object implementing __get__/__set__/__delete__; accessing "
        "`instance.attr` triggers the descriptor's __get__ instead of a plain dict lookup, which is how "
        "computed/validated attributes work.",
    ),
    (
        "string_interning",
        1800,
        "Why can `a = \"hello\"; b = \"hello\"; a is b` be True even though `is` checks identity, not value?",
        [
            ("a", "CPython interns certain string literals (e.g. short identifier-like ones), so equal literals can share one object"),
            ("b", "Strings are always the same object in Python"),
            ("c", "== and is are the same operator for strings"),
            ("d", "This is always False and the premise is wrong"),
        ],
        ["a"],
        False,
        "CPython caches/interns some string literals as a memory optimization (compile-time constant "
        "folding + an interning cache for identifier-like strings), so two separately written identical "
        "literals sometimes are the same object -- but this is an implementation detail, not something "
        "to rely on; use == for value comparison.",
    ),
    (
        "metaclasses",
        2000,
        "A metaclass in Python is best described as:",
        [
            ("a", "The class of a class -- it controls how classes themselves are constructed"),
            ("b", "A base class every class must inherit from"),
            ("c", "A decorator applied to methods"),
            ("d", "A synonym for abstract base class"),
        ],
        ["a"],
        False,
        "Just as an instance's class controls its behavior, a class's metaclass (default `type`) "
        "controls how the class object itself is created -- overriding __new__/__init__ on a metaclass "
        "lets you customize class creation (e.g. auto-registering subclasses, enforcing interfaces).",
    ),
    (
        "gc_refcounting",
        2100,
        "CPython's primary memory management mechanism is reference counting. What is the separate "
        "cyclic garbage collector needed for?",
        [
            ("a", "Reclaiming objects involved in reference cycles, which never hit a refcount of zero on their own"),
            ("b", "Reclaiming all objects, since refcounting alone never frees anything"),
            ("c", "Compacting the heap to reduce fragmentation"),
            ("d", "Nothing -- CPython has no separate garbage collector"),
        ],
        ["a"],
        False,
        "Refcounting frees an object the instant its count hits zero, but two objects that reference "
        "each other keep each other's count above zero forever -- the generational cycle-detecting "
        "collector (the `gc` module) periodically finds and breaks these cycles.",
    ),
    (
        "weakref",
        2200,
        "What's the main use case for the `weakref` module?",
        [
            ("a", "Holding a reference to an object without preventing it from being garbage collected"),
            ("b", "Making an object thread-safe"),
            ("c", "Forcing immediate garbage collection"),
            ("d", "Creating a deep copy that ignores reference cycles"),
        ],
        ["a"],
        False,
        "A weak reference lets you refer to an object (e.g. in a cache) without keeping it alive -- once "
        "all strong references are gone, the object can still be collected, and the weakref then reports "
        "it's gone rather than keeping it around.",
    ),
]
