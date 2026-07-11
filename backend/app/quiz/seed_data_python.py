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
    (
        "mutability",
        300,
        "Which of these built-in types is mutable?",
        [
            ("a", "tuple"),
            ("b", "str"),
            ("c", "list"),
            ("d", "frozenset"),
        ],
        ["c"],
        False,
        "Lists can be changed in place (append, item assignment, sort). Tuples, strings, and "
        "frozensets are immutable -- operations that look like modification actually build and "
        "return new objects.",
    ),
    (
        "return_none",
        300,
        "What does a Python function return if it finishes without executing a `return` statement?",
        [
            ("a", "0"),
            ("b", "None"),
            ("c", "An empty string"),
            ("d", "It raises a MissingReturnError"),
        ],
        ["b"],
        False,
        "Every function call evaluates to something: falling off the end of the body (or a bare "
        "`return`) implicitly returns None. There is no error for omitting a return statement.",
    ),
    (
        "string_immutability",
        350,
        "s = \"hello\"\ns.upper()\nprint(s)\n\nWhat does this print?",
        [
            ("a", "HELLO"),
            ("b", "hello"),
            ("c", "Hello"),
            ("d", "It raises an AttributeError"),
        ],
        ["b"],
        False,
        "Strings are immutable, so s.upper() cannot modify s -- it returns a new uppercased string "
        "that is discarded here. You'd need `s = s.upper()` to keep the result.",
    ),
    (
        "true_division",
        350,
        "What is the result of `7 / 2` in Python 3?",
        [
            ("a", "3 (an int, truncated)"),
            ("b", "3.5, but only if one operand is written as a float"),
            ("c", "3.5 (a float, always)"),
            ("d", "A TypeError -- ints require // for division"),
        ],
        ["c"],
        False,
        "In Python 3, `/` is true division and always produces a float, even for two ints. "
        "Use `//` when you want floor division (7 // 2 == 3).",
    ),
    (
        "dict_get",
        350,
        "What does `d.get(\"k\", 0)` return when the key \"k\" is not in dict d?",
        [
            ("a", "It raises a KeyError"),
            ("b", "None"),
            ("c", "0"),
            ("d", "It inserts \"k\" with value 0, then returns 0"),
        ],
        ["c"],
        False,
        "dict.get returns the supplied default (here 0) for missing keys instead of raising "
        "KeyError, and unlike defaultdict it does NOT insert anything into the dict.",
    ),
    (
        "sort_vs_sorted",
        400,
        "What does `my_list.sort()` return?",
        [
            ("a", "A new sorted copy of the list"),
            ("b", "None -- it sorts the list in place"),
            ("c", "The list itself, sorted, for chaining"),
            ("d", "An iterator over the sorted elements"),
        ],
        ["b"],
        False,
        "list.sort() mutates the list in place and returns None (a Python convention for in-place "
        "operations), so `x = my_list.sort()` leaves x as None. Use sorted(my_list) to get a new "
        "sorted list back.",
    ),
    (
        "dict_ordering",
        400,
        "When you iterate over a dict in Python 3.7+, in what order do you get the keys?",
        [
            ("a", "Arbitrary order that can change between runs"),
            ("b", "Sorted order"),
            ("c", "Insertion order, guaranteed by the language"),
            ("d", "Hash order, which is deterministic per process"),
        ],
        ["c"],
        False,
        "Since Python 3.7, dicts are guaranteed by the language spec to preserve insertion order "
        "(it was an implementation detail of CPython 3.6's compact dict, then made official).",
    ),
    (
        "range_lazy",
        400,
        "Why does `r = range(10**12)` execute instantly without exhausting memory?",
        [
            ("a", "range returns a lazy sequence object that computes each value on demand"),
            ("b", "CPython allocates the list in compressed form"),
            ("c", "range values are stored on disk when they exceed RAM"),
            ("d", "It doesn't -- this line raises a MemoryError"),
        ],
        ["a"],
        False,
        "A range object stores only start, stop, and step, computing any element (and even "
        "membership tests) arithmetically on demand -- it never materializes the values, no matter "
        "how large the range.",
    ),
    (
        "tuple_swap",
        400,
        "How does `a, b = b, a` swap two variables without a temporary?",
        [
            ("a", "The interpreter special-cases swaps at the C level only for two variables"),
            ("b", "The right side is fully evaluated (packed) before any assignment happens"),
            ("c", "It doesn't work reliably -- a temporary variable is still required"),
            ("d", "Both names are updated simultaneously by the OS"),
        ],
        ["b"],
        False,
        "In tuple assignment the entire right-hand side is evaluated first (conceptually packed "
        "into a tuple), then unpacked into the targets left to right -- so both old values are "
        "captured before either name is rebound.",
    ),
    (
        "numeric_literals",
        400,
        "Which of these is a valid Python int literal for one million?",
        [
            ("a", "1,000,000"),
            ("b", "1 000 000"),
            ("c", "1_000_000"),
            ("d", "1.000.000"),
        ],
        ["c"],
        False,
        "Underscores are allowed as visual separators in numeric literals (PEP 515) and are "
        "ignored by the parser. Commas would create a tuple (1, 0, 0) and spaces or dots are "
        "syntax errors.",
    ),
    (
        "enumerate_start",
        450,
        "How do you loop over `items` with a counter that starts at 1 instead of 0?",
        [
            ("a", "for i, x in enumerate(items, start=1):"),
            ("b", "for i, x in enumerate(items) + 1:"),
            ("c", "for i, x in enumerate(items, base=1):"),
            ("d", "You can't -- enumerate always starts at 0"),
        ],
        ["a"],
        False,
        "enumerate takes an optional second argument (start) for the initial counter value. "
        "It's cleaner than adding 1 to the index inside the loop body.",
    ),
    (
        "none_singleton",
        450,
        "Why is `x is None` the recommended way to test for None, rather than `x == None`?",
        [
            ("a", "== raises a TypeError when either side is None"),
            ("b", "is is faster because it skips the GIL"),
            ("c", "None is a singleton, so identity is exact, while __eq__ can be overridden to lie"),
            ("d", "They are exactly equivalent; it's purely style"),
        ],
        ["c"],
        False,
        "There is exactly one None object, so `is None` is a precise identity check. `== None` "
        "invokes the object's __eq__, which a class can override to return anything (e.g. numpy "
        "arrays return an array, not a bool).",
    ),
    (
        "set_dedup",
        450,
        "What does `set([3, 1, 3, 2, 1])` produce?",
        [
            ("a", "{3, 1, 3, 2, 1} -- sets keep duplicates but hash them"),
            ("b", "A set containing 1, 2, 3 with duplicates removed and no guaranteed order"),
            ("c", "[1, 2, 3] -- a sorted list"),
            ("d", "A ValueError because of the duplicate elements"),
        ],
        ["b"],
        False,
        "Sets store at most one of each value (by hash/equality), so duplicates collapse. Unlike "
        "dicts, sets make no ordering promise -- don't rely on iteration order.",
    ),
    (
        "conditional_expression",
        500,
        "In `x = a if cond else b`, when is `b` evaluated?",
        [
            ("a", "Always -- both branches are evaluated, then one is picked"),
            ("b", "Only when cond is falsy"),
            ("c", "Before cond, due to operator precedence"),
            ("d", "Never -- b is only a type hint for x"),
        ],
        ["b"],
        False,
        "The conditional expression is lazy: cond is evaluated first, then exactly one of the two "
        "branches runs. Side effects in the untaken branch never happen.",
    ),
    (
        "chained_comparison",
        500,
        "What does `1 < x < 10` mean in Python?",
        [
            ("a", "(1 < x) < 10 -- the boolean is compared with 10"),
            ("b", "A syntax error; comparisons can't be chained"),
            ("c", "(1 < x) and (x < 10), with x evaluated only once"),
            ("d", "1 < (x < 10) -- right-associative"),
        ],
        ["c"],
        False,
        "Python chains comparison operators: a OP1 b OP2 c is equivalent to (a OP1 b) and "
        "(b OP2 c) except the middle expression is evaluated just once. This differs from C, "
        "where (1 < x) < 10 compares a 0/1 result against 10.",
    ),
    (
        "dict_membership",
        500,
        "For a dict d, what does the expression `\"k\" in d` test?",
        [
            ("a", "Whether \"k\" is one of d's keys"),
            ("b", "Whether \"k\" is one of d's values"),
            ("c", "Whether \"k\" appears as a key or a value"),
            ("d", "Whether \"k\" is a substring of any key"),
        ],
        ["a"],
        False,
        "Membership on a dict checks keys (an O(1) average hash lookup). To test values you must "
        "say `\"k\" in d.values()`, which is a linear scan.",
    ),
    (
        "zip_shortest",
        500,
        "What does `zip(a, b)` do when a and b have different lengths?",
        [
            ("a", "Raises a ValueError immediately"),
            ("b", "Pads the shorter one with None"),
            ("c", "Stops silently when the shortest input is exhausted"),
            ("d", "Cycles the shorter input to match the longer one"),
        ],
        ["c"],
        False,
        "zip stops at the shortest input, silently dropping the longer one's tail. Python 3.10 "
        "added zip(a, b, strict=True) to raise ValueError on unequal lengths, and "
        "itertools.zip_longest pads instead.",
    ),
    (
        "lambda_limits",
        500,
        "Compared with a `def` function, what is a lambda restricted to?",
        [
            ("a", "A single expression -- no statements like assignment or try"),
            ("b", "At most two parameters"),
            ("c", "It cannot capture variables from enclosing scope"),
            ("d", "It cannot be passed as an argument to another function"),
        ],
        ["a"],
        False,
        "A lambda body must be one expression whose value is the return value; statements "
        "(assignments, loops, try, etc.) are syntax errors. Otherwise lambdas are ordinary "
        "function objects -- they close over variables and pass around like any other.",
    ),
    (
        "bytes_vs_str",
        550,
        "In Python 3, how do you convert between str and bytes?",
        [
            ("a", "They convert implicitly when mixed in an expression"),
            ("b", "str.encode() produces bytes; bytes.decode() produces str, both taking an encoding"),
            ("c", "bytes(s) and str(b) always do the right thing without an encoding"),
            ("d", "Via the codecs in the struct module only"),
        ],
        ["b"],
        False,
        "str is Unicode text and bytes is raw binary; the bridge is an explicit encoding "
        "(e.g. \"hi\".encode(\"utf-8\") / b\"hi\".decode(\"utf-8\")). Mixing them (\"a\" + b\"b\") "
        "raises TypeError, and str(b\"hi\") without an encoding gives the repr \"b'hi'\", a "
        "classic bug.",
    ),
    (
        "single_element_tuple",
        550,
        "Which expression creates a one-element tuple containing 42?",
        [
            ("a", "(42)"),
            ("b", "tuple(42)"),
            ("c", "(42,)"),
            ("d", "[42,]"),
        ],
        ["c"],
        False,
        "The comma, not the parentheses, makes a tuple: (42) is just the int 42 in grouping "
        "parens, and tuple(42) raises TypeError because 42 isn't iterable. `42,` alone would also "
        "work.",
    ),
    (
        "floor_division",
        550,
        "What is `-7 // 2`?",
        [
            ("a", "-3"),
            ("b", "-4"),
            ("c", "-3.5"),
            ("d", "3"),
        ],
        ["b"],
        False,
        "// floors toward negative infinity rather than truncating toward zero: -7 / 2 is -3.5, "
        "which floors to -4. Languages like C truncate to -3, so this trips up people switching "
        "over.",
    ),
    (
        "call_unpacking",
        600,
        "Given `args = [1, 2, 3]`, how do you pass its elements as three separate positional "
        "arguments to f?",
        [
            ("a", "f(args...)"),
            ("b", "f(&args)"),
            ("c", "f(args)"),
            ("d", "f(*args)"),
        ],
        ["d"],
        False,
        "The * unary operator in a call unpacks an iterable into positional arguments "
        "(and ** unpacks a mapping into keyword arguments). f(args) would pass the whole list as "
        "one argument.",
    ),
    (
        "walrus",
        600,
        "What does the walrus operator do in `while (chunk := f.read(1024)):`?",
        [
            ("a", "Assigns f.read(1024) to chunk and uses that value as the loop condition"),
            ("b", "Compares chunk to f.read(1024) for equality"),
            ("c", "Declares chunk's type"),
            ("d", "Creates a lazily-evaluated alias for f.read(1024)"),
        ],
        ["a"],
        False,
        ":= (PEP 572) is an assignment *expression*: it binds the name and evaluates to the "
        "assigned value, letting you assign and test in one place -- here the loop ends when "
        "read() returns an empty (falsy) bytes object.",
    ),
    (
        "fstring_debug",
        600,
        "With x = 42, what does `f\"{x=}\"` produce?",
        [
            ("a", "\"42\""),
            ("b", "\"x=42\""),
            ("c", "\"{x=}\""),
            ("d", "A SyntaxError -- = isn't valid inside an f-string"),
        ],
        ["b"],
        False,
        "The = specifier (Python 3.8+) is a debugging aid: it renders the literal expression "
        "text, an equals sign, and the value's repr -- great for quick print debugging like "
        "f\"{user.id=}\".",
    ),
    (
        "bool_int",
        600,
        "What is `True + True`?",
        [
            ("a", "True"),
            ("b", "A TypeError"),
            ("c", "2"),
            ("d", "\"TrueTrue\""),
        ],
        ["c"],
        False,
        "bool is a subclass of int, with True == 1 and False == 0, so arithmetic works on bools. "
        "This is also why `sum(x > 0 for x in nums)` counts matching elements.",
    ),
    (
        "annotations_runtime",
        600,
        "def f(x: int): ...\n\nWhat does CPython do at runtime if you call f(\"hello\")?",
        [
            ("a", "Raises a TypeError because of the annotation"),
            ("b", "Coerces \"hello\" to an int"),
            ("c", "Emits a RuntimeWarning"),
            ("d", "Nothing -- annotations are stored but not enforced"),
        ],
        ["d"],
        False,
        "Type hints are metadata (stored in f.__annotations__) that the interpreter never checks; "
        "enforcement comes from external tools like mypy/pyright, or explicit runtime validators "
        "like pydantic.",
    ),
    (
        "getattr_default",
        600,
        "What does `getattr(obj, \"color\", \"red\")` return when obj has no `color` attribute?",
        [
            ("a", "It raises an AttributeError"),
            ("b", "\"red\""),
            ("c", "None"),
            ("d", "It creates obj.color = \"red\" and returns it"),
        ],
        ["b"],
        False,
        "The three-argument form of getattr returns the default instead of raising "
        "AttributeError. It does not modify the object -- setattr would be needed for that.",
    ),
    (
        "str_join",
        600,
        "What's the correct way to join the list [\"a\", \"b\", \"c\"] into \"a,b,c\"?",
        [
            ("a", "[\"a\", \"b\", \"c\"].join(\",\")"),
            ("b", "join([\"a\", \"b\", \"c\"], \",\")"),
            ("c", "\",\".join([\"a\", \"b\", \"c\"])"),
            ("d", "[\"a\", \"b\", \"c\"] + \",\""),
        ],
        ["c"],
        False,
        "join is a method on the *separator string*, taking any iterable of strings. Making it a "
        "str method means it works on any iterable (lists, generators, etc.) without every "
        "container needing its own join, but the argument order surprises people from other "
        "languages.",
    ),
    (
        "except_multiple",
        600,
        "How do you handle both ValueError and KeyError with one handler?",
        [
            ("a", "except ValueError, KeyError:"),
            ("b", "except (ValueError, KeyError):"),
            ("c", "except ValueError and KeyError:"),
            ("d", "except [ValueError, KeyError]:"),
        ],
        ["b"],
        False,
        "An except clause takes a single exception type or a *tuple* of types (a list won't "
        "work). `except ValueError and KeyError:` is legal syntax but evaluates the `and`, "
        "catching only KeyError -- a silent bug.",
    ),
    (
        "set_operators",
        620,
        "For two sets a and b, what does `a & b` compute?",
        [
            ("a", "Their union"),
            ("b", "Elements in a but not b"),
            ("c", "Their intersection"),
            ("d", "A bitwise hash combination"),
        ],
        ["c"],
        False,
        "Sets overload the bitwise operators: & is intersection, | is union, - is difference, "
        "and ^ is symmetric difference. Method forms (a.intersection(b)) also accept arbitrary "
        "iterables, not just sets.",
    ),
    (
        "for_else",
        650,
        "When does the `else` block attached to a `for` loop execute?",
        [
            ("a", "When the loop body never ran (empty iterable)"),
            ("b", "When the loop finished without hitting a break"),
            ("c", "After every iteration"),
            ("d", "Only when an exception occurred in the loop"),
        ],
        ["b"],
        False,
        "for/else runs the else block only if the loop ran to completion (including zero "
        "iterations) without break -- the classic use is search loops: break on found, else "
        "handles not-found.",
    ),
    (
        "list_aliasing",
        650,
        "a = [1]\nb = a\na += [2]\n\nWhat is b now?",
        [
            ("a", "[1]"),
            ("b", "[1, 2]"),
            ("c", "[2]"),
            ("d", "It raises a ValueError because b is aliased"),
        ],
        ["b"],
        False,
        "Assignment (`b = a`) copies the reference, not the list, so both names point to one "
        "object -- and += on a list calls __iadd__, which extends that object in place. With "
        "`a = a + [2]` instead, a new list is created and b would remain [1].",
    ),
    (
        "isinstance_vs_type",
        650,
        "Why is `isinstance(x, Animal)` generally preferred over `type(x) == Animal`?",
        [
            ("a", "type() is deprecated in Python 3"),
            ("b", "isinstance is O(1) while type comparison is O(n)"),
            ("c", "isinstance also accepts instances of Animal subclasses (and can take a tuple of types)"),
            ("d", "They behave identically; it's only style"),
        ],
        ["c"],
        False,
        "isinstance respects inheritance -- a Dog instance passes isinstance(x, Animal) but fails "
        "type(x) == Animal -- which is what you almost always want under polymorphism. It also "
        "accepts a tuple: isinstance(x, (int, float)).",
    ),
    (
        "keyword_only",
        700,
        "def f(a, *, b): ...\n\nHow can the parameter b be supplied?",
        [
            ("a", "Only as a keyword argument: f(1, b=2)"),
            ("b", "Positionally or by keyword"),
            ("c", "Only positionally: f(1, 2)"),
            ("d", "It can't be supplied; * makes b internal-only"),
        ],
        ["a"],
        False,
        "A bare * in the parameter list marks everything after it keyword-only, so f(1, 2) raises "
        "TypeError. This is used to force call sites to spell out flag-like arguments "
        "(e.g. sorted(xs, reverse=True)).",
    ),
    (
        "positional_only",
        700,
        "def f(x, /): ...\n\nWhat does the / in the parameter list mean?",
        [
            ("a", "x has a default value of None"),
            ("b", "x is positional-only: f(x=1) raises a TypeError"),
            ("c", "x accepts only numeric types"),
            ("d", "The function is division-overloaded"),
        ],
        ["b"],
        False,
        "Parameters before / (Python 3.8, PEP 570) cannot be passed by keyword. This keeps the "
        "parameter name out of the public API (free to rename later) and matches many C-coded "
        "builtins like len().",
    ),
    (
        "any_all",
        700,
        "How does `any(f(x) for x in items)` behave with respect to evaluation?",
        [
            ("a", "It evaluates f for every item, then checks the results"),
            ("b", "It short-circuits: stops consuming and returns True at the first truthy result"),
            ("c", "It evaluates items in parallel threads"),
            ("d", "It raises if items is empty"),
        ],
        ["b"],
        False,
        "any() returns True as soon as it sees a truthy value, leaving the rest of a lazy "
        "iterable unconsumed (all() mirrors this, stopping at the first falsy value). On an empty "
        "iterable, any() is False and all() is True.",
    ),
    (
        "classmethod_staticmethod",
        700,
        "What distinguishes a @classmethod from a @staticmethod?",
        [
            ("a", "A classmethod receives the class as its implicit first argument; a staticmethod receives nothing implicit"),
            ("b", "A staticmethod can only be called on the class, never an instance"),
            ("c", "A classmethod cannot be inherited"),
            ("d", "There is no difference except naming convention"),
        ],
        ["a"],
        False,
        "classmethod passes cls automatically -- and cls is the *actual* class it was called on, "
        "so alternative constructors like from_json() build subclass instances correctly. A "
        "staticmethod is just a plain function namespaced in the class; both can be called on "
        "instances or the class.",
    ),
    (
        "int_precision",
        720,
        "What happens when a Python int grows past 2**64?",
        [
            ("a", "It silently wraps around like C integers"),
            ("b", "It raises an OverflowError"),
            ("c", "It is automatically converted to a float"),
            ("d", "Nothing special -- Python ints have arbitrary precision"),
        ],
        ["d"],
        False,
        "Python 3 ints are arbitrary-precision: they grow to as many internal digits as needed, "
        "so integer arithmetic never overflows (it just gets slower for huge values). OverflowError "
        "exists mainly for float conversions and C-level interfaces.",
    ),
    (
        "custom_exceptions",
        720,
        "When defining a custom exception class, what should it normally inherit from?",
        [
            ("a", "BaseException, the root of the hierarchy"),
            ("b", "Exception (or a more specific built-in like ValueError)"),
            ("c", "object -- any class can be raised"),
            ("d", "RuntimeError, which is the designated extension point"),
        ],
        ["b"],
        False,
        "Custom errors should derive from Exception so that generic `except Exception:` handlers "
        "catch them. Subclassing BaseException puts you alongside KeyboardInterrupt/SystemExit, "
        "which most handlers deliberately don't catch, and raising a non-exception class is a "
        "TypeError.",
    ),
    (
        "sorted_key",
        730,
        "What does the key= parameter of sorted() expect?",
        [
            ("a", "A two-argument comparison function returning -1/0/1"),
            ("b", "The name of an attribute as a string"),
            ("c", "A one-argument function computing a sort key, called once per element"),
            ("d", "An index into each element"),
        ],
        ["c"],
        False,
        "key= takes a unary function (e.g. len, str.lower, operator.itemgetter(1)); Python calls "
        "it once per element and sorts by the resulting keys -- unlike old-style cmp functions, "
        "which were called O(n log n) times in pairs and were removed in Python 3.",
    ),
    (
        "defaultdict",
        750,
        "d = collections.defaultdict(list)\n\nWhat happens on `d[\"missing\"]` for a key not present?",
        [
            ("a", "list() is called to create a default value, which is inserted under the key and returned"),
            ("b", "It raises a KeyError like a normal dict"),
            ("c", "It returns [] but leaves the dict unchanged"),
            ("d", "It returns None"),
        ],
        ["a"],
        False,
        "defaultdict calls its factory on missing-key *subscript* access, inserting the result -- "
        "which is why d[k].append(v) grouping works without setdefault. Note d.get(\"missing\") "
        "and `\"missing\" in d` do NOT trigger the factory.",
    ),
    (
        "counter",
        750,
        "What does `collections.Counter(\"aabbbc\").most_common(1)` return?",
        [
            ("a", "\"b\""),
            ("b", "[(\"b\", 3)]"),
            ("c", "{\"b\": 3}"),
            ("d", "3"),
        ],
        ["b"],
        False,
        "Counter tallies hashable items into a dict subclass, and most_common(n) returns a *list* "
        "of (element, count) pairs ordered by descending count -- so even for n=1 you get a "
        "one-element list, not the bare element.",
    ),
    (
        "extended_unpacking",
        780,
        "What does `first, *rest = (1, 2, 3, 4)` assign?",
        [
            ("a", "first = 1, rest = (2, 3, 4) -- a tuple, matching the source type"),
            ("b", "first = 1, rest = [2, 3, 4] -- always a list"),
            ("c", "first = 1, rest = an iterator over the remaining items"),
            ("d", "A SyntaxError; * is only allowed in function calls"),
        ],
        ["b"],
        False,
        "Starred assignment (PEP 3132) collects the leftover items into a list regardless of the "
        "source type, and the star can appear in any position: a, *mid, z = seq. An iterator "
        "would be lazy; this is eager.",
    ),
    (
        "shallow_copy",
        800,
        "a = [[1], [2]]\nb = a.copy()\nb[0].append(9)\n\nWhat is a[0] now?",
        [
            ("a", "[1]"),
            ("b", "[1, 9]"),
            ("c", "[9]"),
            ("d", "It raises a RuntimeError"),
        ],
        ["b"],
        False,
        "list.copy() (like a[:] or copy.copy) is shallow: it creates a new outer list whose "
        "elements are the *same* inner list objects, so mutating b[0] mutates a[0]. "
        "copy.deepcopy recursively copies nested structures when you need full independence.",
    ),
    (
        "functools_partial",
        800,
        "parse_binary = functools.partial(int, base=2)\n\nWhat does parse_binary(\"101\") return?",
        [
            ("a", "101"),
            ("b", "5"),
            ("c", "A TypeError -- partial only pre-binds positional arguments"),
            ("d", "2"),
        ],
        ["b"],
        False,
        "partial returns a callable with some arguments frozen -- here it's equivalent to "
        "int(\"101\", base=2), which is 5. It handles both positional and keyword arguments and "
        "is a common alternative to a lambda for callbacks.",
    ),
    (
        "itertools_chain",
        800,
        "What does `itertools.chain(a, b)` do?",
        [
            ("a", "Interleaves elements from a and b alternately"),
            ("b", "Builds a new list containing a's then b's elements"),
            ("c", "Lazily yields all of a's elements, then all of b's, without building a combined container"),
            ("d", "Zips a and b into pairs"),
        ],
        ["c"],
        False,
        "chain produces a single lazy iterator over multiple iterables in sequence -- no "
        "concatenated list is ever materialized, so it works on huge or lazy inputs. "
        "chain.from_iterable does the same for an iterable of iterables (e.g. flattening).",
    ),
    (
        "optional_typing",
        800,
        "In type hints, what does `Optional[int]` mean?",
        [
            ("a", "The argument may be omitted from the call"),
            ("b", "Union[int, None] -- the value is an int or None"),
            ("c", "The value is lazily computed on first access"),
            ("d", "The int may be any size"),
        ],
        ["b"],
        False,
        "Optional[X] is exactly Union[X, None] (spelled `X | None` since 3.10) -- it says the "
        "*value* can be None, and is unrelated to whether the parameter has a default. A "
        "parameter can be optional-to-pass without being Optional-typed, and vice versa.",
    ),
    (
        "await_placement",
        800,
        "Where is the `await` keyword allowed?",
        [
            ("a", "Anywhere, but outside a coroutine it blocks the thread"),
            ("b", "Inside any function, as long as an event loop is running"),
            ("c", "Only inside functions defined with `async def` (it's a SyntaxError elsewhere)"),
            ("d", "Only at module top level"),
        ],
        ["c"],
        False,
        "await is only valid inside async def functions (and async comprehensions); using it in a "
        "regular function is a compile-time SyntaxError, not a runtime error. This is enforced "
        "syntactically because the compiler must generate suspension points.",
    ),
    (
        "bare_raise",
        850,
        "Inside an except block, what does a bare `raise` (no arguments) do?",
        [
            ("a", "Raises a generic RuntimeError"),
            ("b", "Re-raises the exception currently being handled, preserving its original traceback"),
            ("c", "Raises the last exception ever raised anywhere in the program"),
            ("d", "It's a SyntaxError; raise always needs an argument"),
        ],
        ["b"],
        False,
        "Bare raise re-raises the active exception with its traceback intact -- the right way to "
        "log-and-propagate. `raise e` from a caught `except X as e` works too but restarts parts "
        "of the traceback bookkeeping; bare raise is the idiom.",
    ),
    (
        "map_lazy",
        850,
        "What does `map(f, xs)` return in Python 3?",
        [
            ("a", "A list of results"),
            ("b", "A tuple of results"),
            ("c", "A lazy single-use iterator that applies f on demand"),
            ("d", "A copy of xs with f applied in place"),
        ],
        ["c"],
        False,
        "map (and filter) return lazy iterators in Python 3 -- nothing is computed until you "
        "iterate, and once consumed they are exhausted (a second loop over the same map object "
        "yields nothing). Wrap in list() to materialize.",
    ),
    (
        "lru_cache",
        850,
        "What does decorating a function with @functools.lru_cache do?",
        [
            ("a", "Memoizes results keyed by the call arguments, so repeated identical calls skip the body"),
            ("b", "Caches the function's bytecode for faster loading"),
            ("c", "Runs the function in a background thread and caches the future"),
            ("d", "Limits how many times the function may be called"),
        ],
        ["a"],
        False,
        "lru_cache stores results in a dict keyed by the (hashable) arguments, evicting "
        "least-recently-used entries beyond maxsize (default 128). functools.cache is the "
        "unbounded equivalent (lru_cache(maxsize=None)). Beware using it on methods -- it keeps "
        "self alive in the cache.",
    ),
    (
        "string_building",
        850,
        "You need to build a large string from thousands of pieces in a loop. What's the "
        "recommended approach?",
        [
            ("a", "Repeated s += piece, since strings resize in place"),
            ("b", "Collect the pieces in a list and \"\".join(pieces) once at the end"),
            ("c", "Use a bytearray and cast at the end -- strings can't be built incrementally"),
            ("d", "Recursion, concatenating halves"),
        ],
        ["b"],
        False,
        "Strings are immutable, so naive += copies the whole accumulated string each time -- "
        "O(n^2) overall. join computes the final size once and copies each piece once: O(n). "
        "(CPython has a refcount-based in-place optimization that often rescues +=, but it's an "
        "implementation detail; join is the guaranteed-fast, portable idiom.)",
    ),
    (
        "str_vs_repr",
        850,
        "What is the intended difference between __str__ and __repr__?",
        [
            ("a", "__repr__ aims to be unambiguous/for developers; __str__ aims to be readable/for end users"),
            ("b", "__str__ is called by print; __repr__ is only used by the repr() builtin and nothing else"),
            ("c", "__repr__ must return valid Python source or raise"),
            ("d", "They are aliases; defining either defines both"),
        ],
        ["a"],
        False,
        "repr targets developers (ideally eval-able or at least unambiguous, like "
        "datetime.date(2024, 1, 1)); str targets display. If __str__ is missing, str() falls back "
        "to __repr__ (not vice versa), and containers always render their elements with repr -- "
        "which is why print([Point()]) ignores Point.__str__.",
    ),
    (
        "deque",
        850,
        "Why prefer collections.deque over a list for a FIFO queue?",
        [
            ("a", "deque is thread-safe while list is not"),
            ("b", "deque.popleft() is O(1); list.pop(0) is O(n) because all remaining elements shift"),
            ("c", "deque stores elements more compactly than list"),
            ("d", "list.pop(0) is deprecated"),
        ],
        ["b"],
        False,
        "A list is a contiguous array, so removing the front element shifts everything left -- "
        "O(n) per dequeue. deque is a doubly-linked block structure with O(1) append/pop at both "
        "ends (at the cost of O(n) random access by index).",
    ),
    (
        "float_precision",
        900,
        "Why does `0.1 + 0.2 == 0.3` evaluate to False?",
        [
            ("a", "A known CPython rounding bug"),
            ("b", "The == operator compares floats by identity"),
            ("c", "0.1, 0.2, and 0.3 have no exact binary floating-point representation, so tiny errors accumulate"),
            ("d", "Float addition is nondeterministic"),
        ],
        ["c"],
        False,
        "IEEE-754 binary floats can't represent decimal fractions like 0.1 exactly (they're "
        "repeating fractions in base 2), so 0.1 + 0.2 is 0.30000000000000004. Use "
        "math.isclose() for comparisons or decimal.Decimal when exact decimal arithmetic matters "
        "-- this is IEEE-754 behavior, not a Python quirk.",
    ),
    (
        "iterator_protocol",
        900,
        "How does a for loop know that an iterator is exhausted?",
        [
            ("a", "The iterator's __next__ raises StopIteration, which the loop catches"),
            ("b", "__next__ returns None"),
            ("c", "The loop checks len() before each step"),
            ("d", "The iterator sets a .done flag the loop polls"),
        ],
        ["a"],
        False,
        "The iteration protocol signals exhaustion with the StopIteration exception from "
        "__next__ -- there's no sentinel return value (None is a legitimate element). The for "
        "statement catches it silently; calling next() yourself lets it propagate unless you pass "
        "a default: next(it, None).",
    ),
    (
        "dataclass_frozen",
        900,
        "p = FrozenPoint(1, 2)  # @dataclass(frozen=True)\np.x = 5\n\nWhat happens?",
        [
            ("a", "x is updated; frozen only affects new attributes"),
            ("b", "dataclasses.FrozenInstanceError is raised"),
            ("c", "A silent no-op"),
            ("d", "A DeprecationWarning, then the assignment succeeds"),
        ],
        ["b"],
        False,
        "frozen=True makes the generated class raise FrozenInstanceError from __setattr__ / "
        "__delattr__ after __init__. Combined with eq=True (the default) it also generates "
        "__hash__, so frozen dataclass instances are hashable and usable as dict keys.",
    ),
    (
        "modulo_sign",
        900,
        "What is `-7 % 3` in Python?",
        [
            ("a", "-1"),
            ("b", "1"),
            ("c", "2"),
            ("d", "-2"),
        ],
        ["c"],
        False,
        "Python's % takes the sign of the *divisor* (unlike C, where it follows the dividend): "
        "-7 = 3 * (-3) + 2, consistent with floor division so that (a // b) * b + a % b == a "
        "always holds. This is why `index % length` safely wraps negative indices.",
    ),
    (
        "functools_wraps",
        950,
        "Why should a decorator apply @functools.wraps(func) to its wrapper function?",
        [
            ("a", "It makes the wrapper faster by inlining the wrapped call"),
            ("b", "Without it, the decorator silently fails on methods"),
            ("c", "It's required for the decorator syntax to work at all"),
            ("d", "It copies func's __name__, __doc__, etc. onto the wrapper so introspection and debugging see the real function"),
        ],
        ["d"],
        False,
        "A wrapper is a different function object, so without wraps every decorated function "
        "reports __name__ == \"wrapper\" and loses its docstring -- breaking help(), logging, "
        "pickling, and test discovery. wraps copies the metadata and sets __wrapped__, which "
        "tools like inspect.unwrap use to reach the original.",
    ),
    (
        "enum_alias",
        950,
        "class Color(Enum):\n    RED = 1\n    CRIMSON = 1\n\nWhat is Color.CRIMSON?",
        [
            ("a", "A ValueError is raised at class definition"),
            ("b", "An alias -- the very same member object as Color.RED"),
            ("c", "A distinct member that happens to compare equal to RED"),
            ("d", "An IntEnum is required for duplicate values"),
        ],
        ["b"],
        False,
        "A second name with an equal value becomes an *alias* for the first member: "
        "Color.CRIMSON is Color.RED, and iteration over Color yields only canonical members "
        "(aliases are skipped). Decorating the class with @enum.unique turns duplicates into a "
        "ValueError instead.",
    ),
    (
        "try_else",
        950,
        "In try/except/else/finally, when does the `else` block run?",
        [
            ("a", "When the try block raised an exception that no except clause matched"),
            ("b", "Always, just before finally"),
            ("c", "Only when the try block completed without raising"),
            ("d", "It's a syntax error to combine else with except"),
        ],
        ["c"],
        False,
        "else runs only on a clean try block, before finally. Its value over just putting the "
        "code at the end of try is scoping the except clauses precisely: exceptions raised in the "
        "else block are NOT caught by the except clauses above it.",
    ),
    (
        "dataclass_post_init",
        950,
        "What is __post_init__ in a dataclass for?",
        [
            ("a", "It replaces __init__ entirely when defined"),
            ("b", "It runs after the generated __init__ assigns the fields, for validation or derived attributes"),
            ("c", "It runs once per class, after the class object is created"),
            ("d", "It is called before pickling an instance"),
        ],
        ["b"],
        False,
        "The generated __init__ assigns each field, then calls __post_init__ if defined -- the "
        "hook for validation or computing derived fields without giving up the generated "
        "constructor. Fields declared with field(init=False) are typically filled in here, and "
        "InitVar pseudo-fields are passed to it as arguments.",
    ),
    (
        "cpu_parallelism",
        950,
        "In standard CPython, what's the right tool for parallelizing a CPU-bound pure-Python workload?",
        [
            ("a", "threading.Thread -- one thread per core"),
            ("b", "asyncio with one task per chunk"),
            ("c", "multiprocessing / ProcessPoolExecutor -- separate processes, each with its own interpreter and GIL"),
            ("d", "Increasing sys.setrecursionlimit"),
        ],
        ["c"],
        False,
        "Threads and asyncio tasks share one GIL, so pure-Python CPU work in them is serialized -- "
        "they help only when tasks spend time waiting (I/O). Separate processes each have their "
        "own interpreter and GIL and truly run on multiple cores, at the cost of "
        "pickling data between processes.",
    ),
    (
        "bisect",
        950,
        "What does `bisect.bisect_left(a, x)` return for a sorted list a?",
        [
            ("a", "The index where x could be inserted to keep a sorted, found by binary search"),
            ("b", "True/False for whether x is in a"),
            ("c", "The element closest to x"),
            ("d", "A new sorted list with x inserted"),
        ],
        ["a"],
        False,
        "bisect_left binary-searches in O(log n) and returns the leftmost insertion point (bisect_right "
        "returns the rightmost, after any equal elements); insort actually inserts. The list must "
        "already be sorted -- bisect never checks, and gives garbage answers on unsorted input.",
    ),
    (
        "sort_stability",
        1000,
        "Python's sort is guaranteed 'stable'. What does that mean, and what does it enable?",
        [
            ("a", "It never raises on incomparable elements"),
            ("b", "Equal-keyed elements keep their original relative order, enabling multi-key sorts by sorting in passes from least to most significant key"),
            ("c", "It always runs in O(n log n) worst case"),
            ("d", "It produces the same result regardless of the key function"),
        ],
        ["b"],
        False,
        "Stability means ties preserve input order. So to sort by department, then salary within "
        "department, you can sort by salary first and then by department -- the second (stable) "
        "sort won't scramble the salary ordering among equal departments.",
    ),
    (
        "decorator_order",
        1000,
        "@a\n@b\ndef f(): ...\n\nWhat is this equivalent to?",
        [
            ("a", "f = a(b(f)) -- the decorator nearest the def applies first"),
            ("b", "f = b(a(f)) -- top decorator applies first"),
            ("c", "f = a(f); f = b(f) run independently on the original f"),
            ("d", "The order is unspecified"),
        ],
        ["a"],
        False,
        "Stacked decorators apply bottom-up: b wraps the raw function, then a wraps b's result. "
        "Order matters in practice -- e.g. @lru_cache above @log caches the logging wrapper, "
        "while @log above @lru_cache logs every call including cache hits.",
    ),
    (
        "asyncio_gather",
        1000,
        "results = await asyncio.gather(fetch(1), fetch(2), fetch(3))\n\nWhat does gather do here?",
        [
            ("a", "Runs the three coroutines strictly one after another"),
            ("b", "Runs them concurrently and returns their results in completion order"),
            ("c", "Runs them concurrently and returns their results in argument order"),
            ("d", "Returns three Task objects you must await individually"),
        ],
        ["c"],
        False,
        "gather schedules all awaitables concurrently on the loop and, when all complete, returns "
        "a list of results matching the argument order (not completion order). By default the "
        "first exception propagates immediately; return_exceptions=True collects errors as "
        "results instead.",
    ),
    (
        "contextlib_suppress",
        1000,
        "with contextlib.suppress(FileNotFoundError):\n    os.remove(path)\n\nWhat does this do?",
        [
            ("a", "Retries os.remove until it stops raising"),
            ("b", "Silently swallows a FileNotFoundError from the block; other exceptions still propagate"),
            ("c", "Logs the exception and re-raises it"),
            ("d", "Converts the exception into a warning"),
        ],
        ["b"],
        False,
        "suppress is the context-manager equivalent of try/except-pass for the listed exception "
        "types -- more explicit about intent and scoped exactly to the with block. Anything not "
        "listed propagates normally, and execution resumes *after* the with block, not at the "
        "next statement inside it.",
    ),
    (
        "namedtuple_vs_dataclass",
        1000,
        "What's a key behavioral difference between a typing.NamedTuple class and a regular @dataclass?",
        [
            ("a", "NamedTuple instances are immutable tuples -- they support indexing/unpacking and can't be mutated; dataclasses are mutable regular objects by default"),
            ("b", "NamedTuple can't have default values"),
            ("c", "Dataclasses can't define methods"),
            ("d", "NamedTuple fields are untyped"),
        ],
        ["a"],
        False,
        "A NamedTuple subclass IS a tuple: immutable, hashable by default, iterable, unpackable, "
        "and comparable to plain tuples of the same values. A dataclass is an ordinary class with "
        "generated methods -- mutable unless frozen=True, and never index-accessible by position.",
    ),
    (
        "abstractmethod",
        1000,
        "class Base(ABC):\n    @abstractmethod\n    def run(self): ...\n\nWhen does Python stop you from using a subclass that never implements run()?",
        [
            ("a", "At class definition time, with a TypeError"),
            ("b", "At instantiation time -- creating an instance raises TypeError"),
            ("c", "At call time -- calling run() raises NotImplementedError"),
            ("d", "Never; abstractmethod is documentation only"),
        ],
        ["b"],
        False,
        "ABCs allow *defining* incomplete subclasses (they may themselves be abstract), but "
        "instantiating any class with unimplemented abstract methods raises TypeError. Note this "
        "is enforced by ABCMeta at instance creation -- nothing happens at call time, unlike the "
        "raise-NotImplementedError pattern.",
    ),
    (
        "sys_modules_cache",
        1000,
        "A module is imported by two different files in the same process. How many times does its "
        "top-level code execute?",
        [
            ("a", "Twice -- once per import statement"),
            ("b", "Once -- the module object is cached in sys.modules and reused"),
            ("c", "Zero -- top-level code only runs via `python -m`"),
            ("d", "Depends on whether the imports use `import x` or `from x import y`"),
        ],
        ["b"],
        False,
        "The first import executes the module body and stores the module object in sys.modules; "
        "every later import (in any file, either syntax) just fetches the cached object. This is "
        "also why module-level state acts as a process-wide singleton, and why importlib.reload "
        "exists for forcing re-execution.",
    ),
    (
        "nonlocal",
        1050,
        "def counter():\n    n = 0\n    def inc():\n        n += 1\n        return n\n    return inc\n\nCalling the returned inc() raises UnboundLocalError. What one-line fix makes it work?",
        [
            ("a", "Add `global n` inside inc"),
            ("b", "Add `nonlocal n` inside inc"),
            ("c", "Rename n inside inc to avoid the clash"),
            ("d", "Declare n with `let n = 0`"),
        ],
        ["b"],
        False,
        "Assignment makes n local to inc unless declared otherwise; nonlocal binds it to the "
        "nearest enclosing function scope (counter's n). global would look in the module scope, "
        "where no n exists. Reading a closure variable needs no declaration -- only rebinding "
        "does.",
    ),
    (
        "dict_mutation_iteration",
        1050,
        "What happens if you add a new key to a dict while iterating over it with `for k in d:`?",
        [
            ("a", "The new key is included later in the same iteration"),
            ("b", "RuntimeError: dictionary changed size during iteration"),
            ("c", "The new key is silently skipped"),
            ("d", "Undefined behavior that may corrupt the dict"),
        ],
        ["b"],
        False,
        "Dict iterators detect size changes and raise RuntimeError rather than risk iterating a "
        "rehashed table. Mutating *values* of existing keys is fine; for structural changes, "
        "iterate over a snapshot (`for k in list(d):`) or collect changes and apply them after "
        "the loop.",
    ),
    (
        "dataclass_mutable_default",
        1050,
        "@dataclass\nclass Bag:\n    items: list = []\n\nWhat happens?",
        [
            ("a", "It works, but all instances share one list"),
            ("b", "ValueError at class definition: mutable default; use field(default_factory=list)"),
            ("c", "Each instance gets its own empty list"),
            ("d", "TypeError at first instantiation"),
        ],
        ["b"],
        False,
        "dataclasses explicitly guards against the shared-mutable-default trap: a default of type "
        "list, dict, or set raises ValueError when the class is created. "
        "field(default_factory=list) calls the factory per instance, giving each its own list.",
    ),
    (
        "exception_chaining",
        1100,
        "What does `raise ConfigError(\"bad config\") from err` do, compared with a plain raise inside an except block?",
        [
            ("a", "Sets the new exception's __cause__ to err, and the traceback shows 'The above exception was the direct cause...'"),
            ("b", "Discards err entirely"),
            ("c", "Re-raises err with ConfigError's message prepended"),
            ("d", "Raises both exceptions as a group"),
        ],
        ["a"],
        False,
        "raise ... from sets explicit chaining (__cause__), marking the original as the direct "
        "cause. Without it you still get *implicit* chaining (__context__, 'During handling..., "
        "another exception occurred'), and `raise X from None` suppresses the chain entirely -- "
        "useful when the original is an implementation detail.",
    ),
    (
        "match_no_fallthrough",
        1100,
        "In a match statement, what happens after the first matching case block finishes?",
        [
            ("a", "Execution falls through to the next case unless you break"),
            ("b", "The match statement ends -- exactly one case runs, no break needed"),
            ("c", "All matching cases run in order"),
            ("d", "The match re-evaluates from the top"),
        ],
        ["b"],
        False,
        "match/case (PEP 634) checks patterns top to bottom and runs only the first match -- "
        "there's no C-style fallthrough and `break` isn't part of the syntax. `case _:` is the "
        "conventional catch-all wildcard, and a match with no matching case simply does nothing "
        "(no error).",
    ),
    (
        "relative_imports",
        1100,
        "`from . import helpers` raises \"ImportError: attempted relative import with no known parent package\". What's the usual cause?",
        [
            ("a", "helpers.py has a syntax error"),
            ("b", "The file using it was run directly as a script, so it has no package context"),
            ("c", "Relative imports were removed in Python 3"),
            ("d", "The package is missing an __init__.py in site-packages"),
        ],
        ["b"],
        False,
        "Relative imports resolve against the module's __package__, which is empty when a file "
        "inside a package is executed directly (python pkg/mod.py). Run it as a module from the "
        "package root instead -- python -m pkg.mod -- or use absolute imports.",
    ),
    (
        "new_vs_init",
        1150,
        "What's the division of labor between __new__ and __init__?",
        [
            ("a", "__new__ creates and returns the instance; __init__ initializes an already-created instance and must return None"),
            ("b", "__init__ creates the instance; __new__ is a deprecated alias"),
            ("c", "__new__ runs on the first instantiation only, __init__ on every one"),
            ("d", "They are alternatives -- defining both is an error"),
        ],
        ["a"],
        False,
        "__new__ is the (static) constructor receiving cls and returning the new object; "
        "__init__ then initializes it. You mostly need __new__ when subclassing immutables like "
        "str or tuple, whose state must exist before __init__. If __new__ returns an object "
        "that isn't an instance of cls, __init__ is skipped entirely.",
    ),
    (
        "decorator_factory",
        1150,
        "To support `@retry(times=3)` decorating a function, what must `retry` be?",
        [
            ("a", "A function taking (func, times) that returns the wrapper"),
            ("b", "A function taking times that returns a decorator, which takes func and returns the wrapper -- three layers"),
            ("c", "A class with a __get__ method"),
            ("d", "Any function -- Python passes func and times together automatically"),
        ],
        ["b"],
        False,
        "@retry(times=3) evaluates retry(times=3) *first*, and whatever it returns is used as the "
        "decorator. So retry is a decorator factory: outer takes the arguments, middle takes the "
        "function, inner is the wrapper that runs at call time.",
    ),
    (
        "bare_except",
        1150,
        "What's the practical difference between `except:` and `except Exception:`?",
        [
            ("a", "None -- bare except is shorthand for except Exception"),
            ("b", "Bare except also catches BaseException subclasses like KeyboardInterrupt and SystemExit, so it can block Ctrl-C and clean shutdown"),
            ("c", "Bare except is faster because it skips the type check"),
            ("d", "except Exception also catches warnings"),
        ],
        ["b"],
        False,
        "KeyboardInterrupt and SystemExit deliberately derive from BaseException, *not* "
        "Exception, precisely so that `except Exception:` handlers let them through. A bare "
        "except swallows them too, which is why a bare except around a loop can make a program "
        "un-interruptible.",
    ),
    (
        "base_exceptions",
        1200,
        "Which of these derive from BaseException but NOT from Exception? (select all that apply)",
        [
            ("a", "KeyboardInterrupt"),
            ("b", "ValueError"),
            ("c", "SystemExit"),
            ("d", "GeneratorExit"),
            ("e", "StopIteration"),
        ],
        ["a", "c", "d"],
        True,
        "KeyboardInterrupt, SystemExit, and GeneratorExit sit directly under BaseException so "
        "that ordinary `except Exception:` handlers don't accidentally swallow Ctrl-C, "
        "interpreter shutdown, or generator cleanup. ValueError and StopIteration are regular "
        "Exception subclasses.",
    ),
    (
        "daemon_threads",
        1200,
        "What happens to a thread started with daemon=True when the main program exits?",
        [
            ("a", "The interpreter waits for it to finish, like any thread"),
            ("b", "It is killed abruptly -- no finally blocks or cleanup guaranteed to run"),
            ("c", "It gets 30 seconds to finish, then is killed"),
            ("d", "It keeps the process alive until it completes"),
        ],
        ["b"],
        False,
        "The interpreter exits when only daemon threads remain, terminating them without running "
        "their finally clauses or releasing their resources. Non-daemon threads are joined "
        "implicitly at shutdown. Use daemon threads only for work that's safe to drop mid-flight.",
    ),
    (
        "blocking_event_loop",
        1200,
        "Inside an asyncio coroutine, what does calling `time.sleep(5)` (instead of `await asyncio.sleep(5)`) do?",
        [
            ("a", "Blocks the entire event loop -- no other task runs for 5 seconds"),
            ("b", "Sleeps only the current task; others continue"),
            ("c", "Raises a RuntimeError -- blocking calls are detected"),
            ("d", "Automatically defers to a thread pool"),
        ],
        ["a"],
        False,
        "The event loop runs all tasks on one thread and can only switch at await points, so any "
        "synchronous blocking call freezes everything scheduled on the loop. Use the async "
        "equivalent, or push genuinely blocking work through "
        "asyncio.to_thread()/run_in_executor().",
    ),
    (
        "unbound_local",
        1250,
        "x = 5\n\ndef f():\n    print(x)\n    x = 1\n\nCalling f() raises UnboundLocalError on the print line. Why?",
        [
            ("a", "print cannot access globals from inside a function"),
            ("b", "The assignment anywhere in the body makes x local for the WHOLE function, so the earlier read finds an unassigned local"),
            ("c", "Python executes assignments before prints within a block"),
            ("d", "x = 1 shadows the global only after the line executes, so this should actually print 5"),
        ],
        ["b"],
        False,
        "Scope is decided per-name at compile time for the whole function: because x is assigned "
        "somewhere in f, every reference to x in f is the local slot -- including reads that "
        "execute before the assignment. `global x` (or reading under a different name) fixes it.",
    ),
    (
        "small_int_cache",
        1250,
        "a = 100\nb = 100\n\n`a is b` is True here, but the same test with two large runtime-computed ints (e.g. 10**6) may be False. Why?",
        [
            ("a", "CPython pre-allocates and reuses the ints -5 through 256, so small values are the same object; larger ints are separate objects"),
            ("b", "is compares values for ints below 1000"),
            ("c", "Large ints are stored as floats internally"),
            ("d", "The behavior is random per process"),
        ],
        ["a"],
        False,
        "Small ints are interned singletons in CPython, so identity 'works' for them by accident; "
        "outside the cache (and absent compile-time constant folding), equal ints are distinct "
        "objects. It's an implementation detail -- always compare numbers with ==, never is.",
    ),
    (
        "type_checking_guard",
        1250,
        "What is the `if TYPE_CHECKING:` idiom (from the typing module) for?",
        [
            ("a", "Enabling runtime type enforcement in debug builds"),
            ("b", "Guarding imports needed only for type annotations -- the block is skipped at runtime but read by type checkers, avoiding import cycles and startup cost"),
            ("c", "Marking code that mypy should ignore"),
            ("d", "Switching between typed and untyped versions of a module"),
        ],
        ["b"],
        False,
        "typing.TYPE_CHECKING is False at runtime but treated as True by static type checkers. "
        "Imports placed under it exist only for annotations -- the standard fix for circular "
        "imports caused purely by type hints (combined with string annotations or `from "
        "__future__ import annotations` so the names aren't evaluated at runtime).",
    ),
    (
        "itertools_groupby",
        1250,
        "Why does `itertools.groupby(data, key=k)` usually require sorting data by k first?",
        [
            ("a", "groupby raises ValueError on unsorted input"),
            ("b", "groupby only groups *consecutive* elements with equal keys, so unsorted input yields multiple fragments per key"),
            ("c", "Sorting is needed to make the keys hashable"),
            ("d", "It doesn't -- groupby builds a dict internally"),
        ],
        ["b"],
        False,
        "groupby is a streaming operator (like Unix uniq): it starts a new group every time the "
        "key changes, without any lookback. On unsorted input you get a separate group per run of "
        "equal keys. Sort by the same key first for SQL-style grouping -- or use a "
        "defaultdict(list) if you don't need laziness.",
    ),
    (
        "round_half_even",
        1300,
        "What is `round(2.5)` in Python 3?",
        [
            ("a", "3"),
            ("b", "2"),
            ("c", "2.5"),
            ("d", "It raises a ValueError for ambiguous halves"),
        ],
        ["b"],
        False,
        "Python 3 uses banker's rounding (round-half-to-even): exact halves go to the nearest "
        "even value, so round(2.5) == 2 and round(3.5) == 4. This eliminates the systematic "
        "upward bias of always rounding halves up across many operations; use decimal with "
        "ROUND_HALF_UP if you need schoolbook behavior.",
    ),
    (
        "assert_stripped",
        1300,
        "Why shouldn't `assert` be used to validate untrusted input in production code?",
        [
            ("a", "assert is slower than an if/raise"),
            ("b", "Running Python with -O removes assert statements entirely, silently deleting the validation"),
            ("c", "AssertionError cannot carry a message"),
            ("d", "assert only works inside test files"),
        ],
        ["b"],
        False,
        "The -O (optimize) flag compiles asserts out, so any input checking, security guard, or "
        "side effect inside one simply vanishes in optimized runs. Asserts are for internal "
        "invariants that should be impossible to violate; real validation needs explicit "
        "raise statements.",
    ),
    (
        "dunder_call",
        1300,
        "What does implementing __call__ on a class let you do?",
        [
            ("a", "Call instances like functions: obj(args) invokes obj.__call__(args)"),
            ("b", "Call the class without arguments"),
            ("c", "Intercept method lookups on the instance"),
            ("d", "Make the class awaitable"),
        ],
        ["a"],
        False,
        "__call__ makes instances callable, which is how you build function-like objects with "
        "state -- a common way to write decorators as classes or reusable predicates. "
        "(Classes themselves are callable because their *metaclass* defines __call__.)",
    ),
    (
        "name_mangling",
        1350,
        "Inside `class Foo`, what does the attribute name `__secret` (two leading underscores, no trailing) become?",
        [
            ("a", "It stays __secret but becomes inaccessible outside the class"),
            ("b", "_Foo__secret -- the compiler textually rewrites it with the class name"),
            ("c", "A property with no setter"),
            ("d", "A compile error unless declared in __slots__"),
        ],
        ["b"],
        False,
        "Name mangling is a compile-time rewrite of __name identifiers (with at most one trailing "
        "underscore) inside a class body to _ClassName__name. Its purpose is avoiding accidental "
        "clashes with subclass attributes -- not privacy or security, since _Foo__secret remains "
        "plainly accessible.",
    ),
    (
        "array_module",
        1350,
        "For storing a million floats, what does `array.array('d', ...)` give you over a plain list?",
        [
            ("a", "Faster arbitrary-type storage with the same memory use"),
            ("b", "Contiguous raw C doubles -- far less memory than a list of Python float objects, but restricted to one primitive type"),
            ("c", "Automatic vectorized math like numpy"),
            ("d", "Nothing; array is a deprecated alias for list"),
        ],
        ["b"],
        False,
        "A list stores pointers to full Python float objects (~24+ bytes each plus the pointer); "
        "array packs raw 8-byte machine values contiguously. The trade-off is homogeneity -- one "
        "typecode per array -- and elements are boxed back into Python objects on access, so "
        "compute-heavy work still wants numpy.",
    ),
    (
        "gil_io_release",
        1350,
        "The GIL serializes Python bytecode, so why do threads still speed up I/O-bound programs in CPython?",
        [
            ("a", "The OS bypasses the GIL for network sockets"),
            ("b", "CPython releases the GIL around blocking I/O system calls, letting other threads run while one waits"),
            ("c", "I/O threads are secretly processes"),
            ("d", "They don't -- only asyncio helps I/O-bound code"),
        ],
        ["b"],
        False,
        "C-level code wraps blocking operations (socket reads, file I/O, time.sleep, many C "
        "extension computations like hashlib or numpy inner loops) in GIL-release sections. While "
        "one thread waits in the kernel, others execute bytecode -- so threading works well for "
        "I/O-bound loads and poorly only for pure-Python CPU work.",
    ),
    (
        "singledispatch",
        1350,
        "What does @functools.singledispatch dispatch on?",
        [
            ("a", "The runtime type of the FIRST positional argument"),
            ("b", "The declared type annotations of all arguments"),
            ("c", "The number of arguments"),
            ("d", "The return type"),
        ],
        ["a"],
        False,
        "singledispatch creates a generic function: you @func.register implementations per type, "
        "and calls route by the class of the first argument (respecting inheritance via MRO). "
        "It's single dispatch by design -- other arguments never influence the choice. "
        "singledispatchmethod is the variant that skips over self.",
    ),
    (
        "async_context_manager",
        1350,
        "What must an object implement to be used with `async with`?",
        [
            ("a", "__enter__ and __exit__ returning coroutines"),
            ("b", "__aenter__ and __aexit__, both awaitable"),
            ("c", "__await__ only"),
            ("d", "__aiter__ and __anext__"),
        ],
        ["b"],
        False,
        "async with drives the asynchronous context protocol: it awaits __aenter__ on entry and "
        "__aexit__ on exit, so setup/teardown can themselves suspend (e.g. acquiring a connection "
        "from an async pool). A regular __enter__/__exit__ object won't work in async with, and "
        "vice versa.",
    ),
    (
        "hash_eq_contract",
        1400,
        "If you define __eq__ so that a == b, what must also hold for a and b to behave correctly as dict keys?",
        [
            ("a", "hash(a) == hash(b) -- equal objects must have equal hashes"),
            ("b", "id(a) == id(b)"),
            ("c", "hash(a) != hash(b), to avoid collisions"),
            ("d", "Both must be instances of the same class"),
        ],
        ["a"],
        False,
        "Dicts and sets locate keys by hash first, then confirm with ==. If equal objects hash "
        "differently, one key can be 'in' the dict yet unfindable -- silent corruption. The "
        "converse isn't required: unequal objects MAY share a hash (a collision), costing only "
        "performance.",
    ),
    (
        "default_hash",
        1400,
        "A user-defined class defines neither __eq__ nor __hash__. Are its instances usable as dict keys?",
        [
            ("a", "No -- classes must define __hash__ to be hashable"),
            ("b", "Yes -- they get identity-based equality and an id-derived hash, so each instance is its own distinct key"),
            ("c", "Only if the class has no mutable attributes"),
            ("d", "Yes, hashed by their attribute values"),
        ],
        ["b"],
        False,
        "object provides defaults: __eq__ is identity and __hash__ derives from id(), which are "
        "trivially consistent. So arbitrary objects work as dict keys out of the box -- but two "
        "'equal-looking' instances are different keys, since equality is identity until you "
        "override __eq__.",
    ),
    (
        "lru_cache_hashable",
        1400,
        "@functools.lru_cache\ndef f(xs): ...\n\nWhat happens when you call f([1, 2])?",
        [
            ("a", "The list is converted to a tuple for the cache key"),
            ("b", "TypeError: unhashable type -- cache keys are built from the arguments, which must be hashable"),
            ("c", "The call works but is never cached"),
            ("d", "The cache keys on the list's id"),
        ],
        ["b"],
        False,
        "lru_cache stores results in a dict keyed by the argument values, so every argument must "
        "be hashable -- lists, dicts, and sets raise TypeError at call time. Convert to tuples/"
        "frozensets at the call boundary, or restructure so the cached function takes hashable "
        "inputs.",
    ),
    (
        "async_iteration",
        1400,
        "What protocol does `async for x in obj:` require of obj?",
        [
            ("a", "__iter__ returning a coroutine"),
            ("b", "__aiter__ returning an async iterator whose __anext__ coroutine raises StopAsyncIteration when done"),
            ("c", "__next__ defined with async def"),
            ("d", "Being an asyncio.Queue or subclass"),
        ],
        ["b"],
        False,
        "Async iteration mirrors the sync protocol with awaitable steps: __aiter__ (sync method) "
        "returns the async iterator, whose __anext__ is awaited per step and signals exhaustion "
        "with StopAsyncIteration -- a separate exception because StopIteration has special "
        "meaning inside coroutines.",
    ),
    (
        "yield_from_delegation",
        1400,
        "Beyond being shorter than `for v in sub: yield v`, what does `yield from sub` additionally do?",
        [
            ("a", "Nothing -- it is exactly that loop"),
            ("b", "It runs the subgenerator in a separate thread"),
            ("c", "It transparently forwards send(), throw(), and close() to the subgenerator, and the expression evaluates to the subgenerator's return value"),
            ("d", "It flattens nested iterables recursively"),
        ],
        ["c"],
        False,
        "yield from (PEP 380) establishes a full delegation channel: values sent or exceptions "
        "thrown into the outer generator reach the inner one directly, and when the inner "
        "generator returns, its return value becomes the value of the yield from expression -- "
        "none of which the manual loop provides.",
    ),
    (
        "super_mro",
        1450,
        "In a diamond hierarchy (D inherits B and C, both inherit A), what does `super().m()` inside B.m resolve to when called on a D instance?",
        [
            ("a", "A.m, always -- super refers to B's declared base"),
            ("b", "C.m -- super follows the instance's MRO, so the 'next' class after B can be a sibling"),
            ("c", "It raises because the hierarchy is ambiguous"),
            ("d", "B.m recursively"),
        ],
        ["b"],
        False,
        "super() means 'next in the MRO of the *instance's* type', not 'my parent'. For D(B, C), "
        "the MRO is D, B, C, A -- so B's super call lands on C. That's what makes cooperative "
        "multiple inheritance work: each class calls super().m() once and every class in the "
        "diamond runs exactly once.",
    ),
    (
        "finally_return",
        1450,
        "def f():\n    try:\n        return 1\n    finally:\n        return 2\n\nWhat does f() return, and what's the hidden danger of this pattern?",
        [
            ("a", "1 -- try's return wins; no danger"),
            ("b", "2 -- and a return in finally also silently swallows any in-flight exception from the try block"),
            ("c", "It raises a SyntaxError; two returns aren't allowed"),
            ("d", "2, but only when no exception occurred"),
        ],
        ["b"],
        False,
        "finally always runs last, so its return replaces the pending one -- and if the try block "
        "had raised, that exception is discarded too, because the return supersedes it. The same "
        "applies to break/continue in finally; it's a well-known enough footgun that recent "
        "Python versions warn about it.",
    ),
    (
        "getsizeof",
        1450,
        "nums = [list(range(1000)) for _ in range(100)]\n\nWhy does sys.getsizeof(nums) report only ~800 bytes?",
        [
            ("a", "getsizeof is shallow: it measures just the outer list object (header + 100 pointers), not the objects it references"),
            ("b", "CPython compresses nested lists"),
            ("c", "getsizeof reports kilobytes, not bytes"),
            ("d", "The inner lists live in a separate memory pool that isn't counted"),
        ],
        ["a"],
        False,
        "getsizeof measures one object's own footprint only -- for containers, the pointer array "
        "and header, never the referenced elements. Deep measurement requires recursing over "
        "references yourself (e.g. via gc.get_referents), and shared objects make even that "
        "definition slippery.",
    ),
    (
        "processpool_pickle",
        1450,
        "Why does `ProcessPoolExecutor().submit(lambda: 42)` fail?",
        [
            ("a", "Lambdas can't be called without arguments"),
            ("b", "Work sent to a process pool is pickled for transport to the worker process, and lambdas (like local/nested functions) can't be pickled"),
            ("c", "The GIL prevents lambdas from crossing process boundaries"),
            ("d", "submit only accepts async functions"),
        ],
        ["b"],
        False,
        "Processes don't share memory, so the callable and its arguments are serialized with "
        "pickle -- which serializes functions by *reference* (module.qualname), so lambdas, "
        "closures, and functions defined inside other functions fail. Use module-level functions "
        "(with functools.partial for pre-bound args) for pool work.",
    ),
    (
        "protocol_structural",
        1450,
        "class Renderer(Protocol):\n    def render(self) -> str: ...\n\nHow does a class satisfy this typing.Protocol?",
        [
            ("a", "By inheriting from Renderer"),
            ("b", "By registering with Renderer.register()"),
            ("c", "Just by having a compatible render() method -- structural (duck) typing, no inheritance needed"),
            ("d", "By passing an isinstance check at construction"),
        ],
        ["c"],
        False,
        "Protocols (PEP 544) bring duck typing to static checking: any class whose shape matches "
        "-- right methods, compatible signatures -- is assignable where the Protocol is expected, "
        "even third-party classes that never heard of it. This is the static-typing counterpart "
        "of 'if it quacks'; nominal inheritance is what ABCs do instead.",
    ),
    (
        "bool_protocol",
        1500,
        "How does `bool(obj)` decide truthiness for an instance of a user-defined class?",
        [
            ("a", "It calls __bool__ if defined; otherwise falls back to __len__ (0 means False); if neither exists, the object is always truthy"),
            ("b", "It compares the object to None"),
            ("c", "All user-defined instances are truthy, no protocol involved"),
            ("d", "It calls __eq__(False)"),
        ],
        ["a"],
        False,
        "Truthiness is a two-step protocol: __bool__ wins if present, then __len__ (which is why "
        "empty containers are falsy without defining __bool__), then a default of True. This "
        "fallback chain is also why a custom collection gets sensible if-statement behavior for "
        "free just by implementing __len__.",
    ),
    (
        "del_finalizer",
        1500,
        "Why is __del__ a poor place to release critical resources like file handles or locks?",
        [
            ("a", "Its timing is nondeterministic (cycles delay it; interpreter shutdown may skip or half-run it) and exceptions inside it are ignored"),
            ("b", "It's only called when gc.collect() is invoked manually"),
            ("c", "Defining __del__ makes instances unhashable"),
            ("d", "It runs in a separate thread without access to instance attributes"),
        ],
        ["a"],
        False,
        "Refcounting usually runs __del__ promptly, but reference cycles defer it to the cyclic "
        "GC, and at interpreter shutdown modules may already be torn down (globals set to None) "
        "-- plus exceptions in __del__ are swallowed and just printed. Deterministic cleanup "
        "belongs in context managers or explicit close() calls. __del__ also delays collection "
        "of cyclic garbage that contains it.",
    ),
    (
        "generator_priming",
        1500,
        "g = coroutine_style_gen()\ng.send(5)\n\nWhy does this raise \"TypeError: can't send non-None value to a just-started generator\"?",
        [
            ("a", "send() is only valid on async generators"),
            ("b", "The generator hasn't run to its first yield yet, so there's no suspended yield expression to receive the value"),
            ("c", "5 isn't iterable"),
            ("d", "send() must always be preceded by close()"),
        ],
        ["b"],
        False,
        "A sent value becomes the result of the yield expression where the generator is paused -- "
        "but a fresh generator is paused at the top of its body, before any yield. You must prime "
        "it with next(g) (equivalently g.send(None)) to advance to the first yield before sending "
        "real values.",
    ),
    (
        "reflected_operators",
        1500,
        "For `a + b`, when does Python call `type(b).__radd__(a)`?",
        [
            ("a", "Always, before trying __add__"),
            ("b", "When type(a) has no __add__ or its __add__ returns NotImplemented (and reflected-first if type(b) is a proper subclass of type(a) overriding __radd__)"),
            ("c", "Only when a and b are the same type"),
            ("d", "Never -- __radd__ is only used by sum()"),
        ],
        ["b"],
        False,
        "Binary operators try the left operand's method first; returning NotImplemented (not "
        "raising!) hands control to the right operand's reflected method. The subclass exception "
        "lets subclasses refine behavior when mixed with their base. If both return "
        "NotImplemented, Python raises TypeError.",
    ),
    (
        "asyncio_lock",
        1500,
        "What does asyncio.Lock protect against, and how does it differ from threading.Lock?",
        [
            ("a", "It prevents coroutines from interleaving through a critical section across await points; acquiring suspends the coroutine rather than blocking the thread, and it is not thread-safe"),
            ("b", "It's a drop-in thread-safe replacement for threading.Lock"),
            ("c", "It prevents the GIL from being released"),
            ("d", "It locks the event loop so only one task can be scheduled"),
        ],
        ["a"],
        False,
        "Even single-threaded async code has race conditions: a task can be suspended mid-"
        "critical-section at any await, letting another task see inconsistent state. "
        "asyncio.Lock serializes that -- `async with lock:` suspends contenders without blocking "
        "the loop -- but offers no protection across OS threads.",
    ),
    (
        "gather_exceptions",
        1500,
        "What changes when you pass return_exceptions=True to asyncio.gather?",
        [
            ("a", "Exceptions are retried once before propagating"),
            ("b", "Exceptions from tasks are returned in the results list (in position) instead of being raised, so all tasks' outcomes are collected"),
            ("c", "All tasks are cancelled when the first exception occurs"),
            ("d", "Exceptions are logged and replaced with None"),
        ],
        ["b"],
        False,
        "By default gather propagates the first exception to the awaiter (while the other tasks "
        "keep running in the background). With return_exceptions=True nothing propagates: each "
        "slot in the result list holds either the task's result or the exception object itself, "
        "which you then check with isinstance.",
    ),
    (
        "match_class_patterns",
        1500,
        "match point:\n    case Point(x=0, y=0): ...\n\nWhat does this class pattern actually check?",
        [
            ("a", "That point was constructed by calling Point(x=0, y=0)"),
            ("b", "isinstance(point, Point) and point.x == 0 and point.y == 0"),
            ("c", "That point is the class Point itself with class attributes x=0, y=0"),
            ("d", "Structural equality with a new Point(0, 0) instance via __eq__"),
        ],
        ["b"],
        False,
        "Class patterns are isinstance checks plus attribute sub-patterns -- no constructor runs "
        "and __eq__ on the whole object is never called. Positional patterns like Point(0, 0) "
        "additionally require the class to define __match_args__ mapping positions to attribute "
        "names (dataclasses generate it automatically).",
    ),
    (
        "itertools_tee",
        1550,
        "a, b = itertools.tee(source_iter)\n\nWhat's the rule about source_iter afterward, and the memory caveat?",
        [
            ("a", "source_iter must not be used again (tee consumes from it), and if a and b are consumed at very different rates, tee buffers the gap in memory"),
            ("b", "source_iter is unaffected; tee makes independent copies up front"),
            ("c", "tee only works on lists, so there is no caveat"),
            ("d", "a and b share position -- advancing one advances the other"),
        ],
        ["a"],
        False,
        "tee wraps the original iterator and pulls from it on demand, so touching the original "
        "afterwards silently steals items from the tees. Internally items consumed by one tee but "
        "not the other are buffered -- diverge far enough and you've effectively built the list "
        "anyway.",
    ),
    (
        "async_generators",
        1550,
        "What does an `async def` function containing a `yield` define?",
        [
            ("a", "A coroutine that returns a list"),
            ("b", "A SyntaxError -- yield is not allowed in async def"),
            ("c", "An async generator, consumed with `async for`, which may await between yields"),
            ("d", "A regular generator that can only run inside an event loop"),
        ],
        ["c"],
        False,
        "async def + yield makes an async generator (PEP 525): each step of `async for` resumes "
        "it, and it can await arbitrary async work between yields -- ideal for streaming rows "
        "from an async DB cursor. Calling it returns the generator immediately; nothing runs "
        "until iteration.",
    ),
    (
        "exception_groups",
        1550,
        "What problem do ExceptionGroup and BaseExceptionGroup (Python 3.11) solve?",
        [
            ("a", "Grouping exception classes into modules"),
            ("b", "Raising and handling MULTIPLE unrelated exceptions at once -- e.g. several concurrent tasks in an asyncio.TaskGroup failing together"),
            ("c", "Deduplicating repeated exceptions in a loop"),
            ("d", "Chaining an exception to its cause"),
        ],
        ["b"],
        False,
        "Concurrency creates situations where several operations fail independently and no single "
        "exception can represent the outcome. ExceptionGroup packages them into one raisable "
        "object with a tree structure, and the except* syntax exists specifically to unpack and "
        "handle them by type.",
    ),
    (
        "iadd_fallback",
        1550,
        "What does `x += y` do when type(x) does not define __iadd__?",
        [
            ("a", "Raises TypeError -- augmented assignment requires __iadd__"),
            ("b", "Falls back to x = x + y (via __add__/__radd__), rebinding the name to a new object"),
            ("c", "Mutates x through __setattr__"),
            ("d", "Calls __add__ but discards the result"),
        ],
        ["b"],
        False,
        "Augmented assignment prefers the in-place hook but degrades gracefully to the plain "
        "operator plus rebinding. That's why += mutates a list (list has __iadd__) but creates a "
        "new object for tuples, strings, and ints -- same syntax, different aliasing behavior "
        "depending on the type.",
    ),
    (
        "eq_disables_hash",
        1600,
        "You define __eq__ on a class but not __hash__. What happens when you put an instance in a set?",
        [
            ("a", "It works, using the default id-based hash"),
            ("b", "TypeError: unhashable type -- defining __eq__ sets __hash__ to None unless you also define it"),
            ("c", "It works but lookups are O(n)"),
            ("d", "It works only for frozen instances"),
        ],
        ["b"],
        False,
        "Python cuts the default id-based __hash__ when you override __eq__, because "
        "identity-hash would violate the equal-objects-equal-hashes contract for your new "
        "equality. You must supply a __hash__ consistent with __eq__ (hash the same fields you "
        "compare) -- or inherit unhashability for mutable objects, which is often correct.",
    ),
    (
        "generator_close",
        1600,
        "What does calling gen.close() do inside a suspended generator?",
        [
            ("a", "Raises GeneratorExit at the paused yield; the generator must exit (finally blocks run), and yielding again causes a RuntimeError"),
            ("b", "Sets an internal flag the generator can poll"),
            ("c", "Immediately frees the frame without running any generator code"),
            ("d", "Raises StopIteration inside the generator"),
        ],
        ["a"],
        False,
        "close() injects GeneratorExit at the suspension point so try/finally cleanup inside the "
        "generator runs deterministically -- this also happens automatically when a generator is "
        "garbage-collected. A generator that catches GeneratorExit and yields anyway gets "
        "RuntimeError('generator ignored GeneratorExit').",
    ),
    (
        "getattr_vs_getattribute",
        1600,
        "When is __getattr__ called, versus __getattribute__?",
        [
            ("a", "__getattr__ only when normal attribute lookup FAILS; __getattribute__ unconditionally for every attribute access"),
            ("b", "They're aliases from Python 2"),
            ("c", "__getattr__ for instance attributes, __getattribute__ for class attributes"),
            ("d", "__getattribute__ only for dunder methods"),
        ],
        ["a"],
        False,
        "__getattr__ is the miss-handler -- cheap to use for proxies and lazy attributes. "
        "__getattribute__ intercepts *everything*, which makes it powerful but perilous: reading "
        "any self.attr inside it recurses infinitely unless you delegate via "
        "object.__getattribute__(self, name).",
    ),
    (
        "importlib_reload",
        1600,
        "After importlib.reload(mod), why can objects created before the reload still behave 'old'?",
        [
            ("a", "reload is asynchronous and may not have finished"),
            ("b", "Existing instances still reference the OLD class objects, and names imported elsewhere via `from mod import X` still point at the old objects -- reload only re-executes the module into its existing namespace"),
            ("c", "reload only refreshes the module's docstring and metadata"),
            ("d", "The bytecode cache (.pyc) must be deleted first"),
        ],
        ["b"],
        False,
        "reload re-runs the source in the same module object, rebinding mod's attributes -- but "
        "nothing rewrites references already handed out: instances keep their __class__, and "
        "from-imports in other modules were direct object references, not live links. This is "
        "why reload-based hot-reloading is so leaky in practice.",
    ),
    (
        "typing_overload",
        1600,
        "What role do @typing.overload-decorated definitions play at RUNTIME?",
        [
            ("a", "Python dispatches among them by argument types"),
            ("b", "None -- they're stubs for the type checker; the single non-overload implementation defined after them is what actually runs"),
            ("c", "They're compiled into a C switch statement"),
            ("d", "The last overload defined wins for all calls"),
        ],
        ["b"],
        False,
        "overload declares multiple signatures (e.g. different return types per argument type) "
        "purely for static analysis; each stub's body is conventionally `...`. The real "
        "implementation must follow and handle all cases itself -- for actual runtime dispatch "
        "you'd use functools.singledispatch instead.",
    ),
    (
        "match_capture_pattern",
        1600,
        "MAX = 100\nmatch n:\n    case MAX: print(\"at limit\")\n\nWhy does this print \"at limit\" for EVERY n?",
        [
            ("a", "A bare name in a case is a CAPTURE pattern -- it matches anything and rebinds MAX to n; value patterns require dotted names like Limits.MAX or literals"),
            ("b", "match compares by identity and small ints are interned"),
            ("c", "MAX is treated as a wildcard because it's uppercase"),
            ("d", "It doesn't -- this raises a SyntaxError"),
        ],
        ["a"],
        False,
        "In pattern-matching, a plain identifier never means 'compare to this variable' -- it's a "
        "binding target, like a parameter (so this also clobbers the global MAX name in the "
        "match's scope). To match against a constant, use a literal, a dotted name "
        "(SomeClass.MAX), or a guard: `case x if x == MAX:`.",
    ),
    (
        "typevar_bound",
        1650,
        "def clone(x: Animal) -> Animal: ...\nversus\ndef clone(x: T) -> T: ...  # T = TypeVar('T', bound=Animal)\n\nWhat does the TypeVar version express that the first can't?",
        [
            ("a", "That x may also be None"),
            ("b", "That the return type is the SAME specific subtype as the argument -- clone(dog) is a Dog, not just some Animal"),
            ("c", "That the function accepts any type at all"),
            ("d", "Nothing; they are equivalent to a checker"),
        ],
        ["b"],
        False,
        "A bound TypeVar links occurrences: whatever subtype of Animal flows in binds T, and the "
        "return is that same type. With the plain annotation, clone(dog).bark() fails type "
        "checking because the result is only known to be Animal. This is the core use of "
        "generics in signatures.",
    ),
    (
        "except_star",
        1650,
        "How does `except*` differ from a regular `except` clause?",
        [
            ("a", "It matches exceptions inside an ExceptionGroup by type, extracting the matching subgroup -- and multiple except* clauses can EACH run for one raised group"),
            ("b", "It catches exceptions from all threads"),
            ("c", "It's a wildcard that catches everything"),
            ("d", "It re-raises automatically after handling"),
        ],
        ["a"],
        False,
        "except* splits an ExceptionGroup: each clause receives the subgroup matching its type "
        "(always wrapped in a group), unmatched exceptions re-raise as a remaining group "
        "afterward. Unlike regular except, several clauses can all execute for a single raise -- "
        "one per matching exception type in the group.",
    ),
    (
        "generator_throw",
        1650,
        "What does gen.throw(ValueError(\"boom\")) do to a suspended generator?",
        [
            ("a", "Raises ValueError inside the generator at the yield where it's paused; if the generator catches it and yields again, that yielded value is returned by throw()"),
            ("b", "Schedules the exception for the next call to next()"),
            ("c", "Terminates the generator unconditionally without running its code"),
            ("d", "Raises ValueError in the CALLER, tagged with the generator's traceback"),
        ],
        ["a"],
        False,
        "throw() resumes the generator with an exception instead of a value, as if the paused "
        "yield expression raised it. The generator can catch it and continue (throw returns the "
        "next yielded value), let it propagate to the caller, or return (raising StopIteration) "
        "-- the mechanism behind yield-from's exception forwarding.",
    ),
    (
        "slots_inheritance",
        1700,
        "class Base:\n    pass\n\nclass Point(Base):\n    __slots__ = ('x', 'y')\n\nWhy do Point instances still consume as much memory as ordinary objects?",
        [
            ("a", "Slots require the @slotted class decorator to activate"),
            ("b", "Because Base lacks __slots__, every instance still gets a __dict__ through inheritance -- slots only pay off when the entire hierarchy declares them"),
            ("c", "Two-element slots are below the optimization threshold"),
            ("d", "They don't; slots always save memory regardless of bases"),
        ],
        ["b"],
        False,
        "__slots__ works by *omitting* __dict__ from the instance layout, but any slot-less "
        "ancestor reintroduces it -- so the subclass gets both slot descriptors AND a dict, "
        "gaining nothing (and arbitrary attribute assignment quietly works again, hiding the "
        "regression). Every class in the chain needs __slots__, using () for those with no new "
        "attributes.",
    ),
    (
        "init_subclass",
        1700,
        "What is `__init_subclass__` for, and when does it run?",
        [
            ("a", "It runs on the parent class each time a SUBCLASS is defined, receiving the new class -- enabling registration/validation patterns without a metaclass"),
            ("b", "It initializes inherited attributes on each new instance"),
            ("c", "It's called the first time a subclass is instantiated"),
            ("d", "It replaces __init__ in abstract classes"),
        ],
        ["a"],
        False,
        "__init_subclass__ (PEP 487, implicitly a classmethod) hooks class creation from the "
        "*parent's* side: a plugin base can auto-register every subclass at definition time, or "
        "enforce that required attributes exist. It also receives extra class-definition keyword "
        "arguments (class Foo(Base, key=...)), and covers most classic metaclass use cases with "
        "far less machinery.",
    ),
    (
        "runtime_checkable",
        1750,
        "What does isinstance(obj, SomeProtocol) require and actually verify?",
        [
            ("a", "It requires the protocol be decorated @runtime_checkable, and then it checks only that the required members EXIST -- signatures and types are not verified"),
            ("b", "It fully type-checks obj against the protocol at runtime"),
            ("c", "It always raises TypeError; protocols never support isinstance"),
            ("d", "It checks that obj's class inherits from the protocol"),
        ],
        ["a"],
        False,
        "Protocols support isinstance only when marked @runtime_checkable, and the runtime check "
        "is shallow: hasattr-style presence of each member. A class with a render() taking "
        "completely wrong parameters still passes. Full structural verification only happens "
        "statically, in the type checker.",
    ),
    (
        "switch_interval",
        1750,
        "What does sys.setswitchinterval(0.001) tune in CPython?",
        [
            ("a", "How often the cyclic garbage collector runs"),
            ("b", "How long a thread may keep running bytecode before the interpreter asks it to release the GIL so another thread can be scheduled (default 5ms)"),
            ("c", "The asyncio event loop's tick rate"),
            ("d", "The OS process scheduler priority"),
        ],
        ["b"],
        False,
        "The switch interval governs preemption granularity between CPU-bound threads under the "
        "GIL: smaller values mean more responsive switching but more overhead. It has no effect "
        "on GIL releases around blocking I/O, which happen immediately regardless -- and no "
        "effect on multiprocessing, which doesn't share a GIL.",
    ),
    (
        "future_annotations",
        1750,
        "What does `from __future__ import annotations` change?",
        [
            ("a", "It enables runtime type enforcement of annotations"),
            ("b", "All annotations in the module are stored as strings instead of being evaluated at definition time -- so forward references and not-yet-imported names work"),
            ("c", "It back-ports match/case syntax"),
            ("d", "It makes annotations mandatory on all functions"),
        ],
        ["b"],
        False,
        "With PEP 563 semantics, `def f(x: Node) -> Node:` no longer evaluates Node when the def "
        "runs -- annotations become strings in __annotations__, resolvable on demand via "
        "typing.get_type_hints(). This fixes forward/self references and annotation-driven import "
        "cycles, but code that inspects annotations as live objects must resolve them explicitly.",
    ),
    (
        "variance",
        1800,
        "def feed_all(animals: list[Animal]) -> None: ...\n\nWhy does a type checker reject passing a list[Dog] here, even though Dog subclasses Animal?",
        [
            ("a", "A bug -- list[Dog] should be accepted"),
            ("b", "list is invariant because it's mutable: feed_all could legally append a Cat into what the caller believes is a list[Dog]. Read-only Sequence[Animal] is covariant and would accept it"),
            ("c", "Generics never permit subtypes in any position"),
            ("d", "Dog must explicitly inherit list[Animal]"),
        ],
        ["b"],
        False,
        "Mutability forces invariance: accepting list[Dog] as list[Animal] would let the function "
        "insert any Animal, corrupting the caller's list. Declaring the parameter as an immutable "
        "view (Sequence, Iterable, Mapping for dicts) restores the natural covariance -- a good "
        "habit for parameters generally.",
    ),
    (
        "pep479",
        1800,
        "Since Python 3.7 (PEP 479), what happens when a StopIteration is raised INSIDE a generator's body (e.g. from a bare next() call)?",
        [
            ("a", "It silently ends the generator, as in old Python"),
            ("b", "It is converted into a RuntimeError instead of terminating the generator"),
            ("c", "It propagates to the caller as StopIteration"),
            ("d", "The generator restarts from the beginning"),
        ],
        ["b"],
        False,
        "StopIteration leaking from a generator used to be indistinguishable from normal "
        "exhaustion, silently truncating iteration -- a nasty bug class. PEP 479 makes it a loud "
        "RuntimeError; a generator should finish via return. Inside generators, give next() a "
        "default or catch StopIteration explicitly.",
    ),
    (
        "tuple_augmented_assignment",
        1800,
        "t = ([1],)\nt[0] += [2]\n\nWhat is the outcome?",
        [
            ("a", "TypeError is raised, AND t[0] has still become [1, 2]"),
            ("b", "TypeError is raised and t is unchanged"),
            ("c", "It works: tuples allow in-place mutation of their elements"),
            ("d", "t becomes ([2],)"),
        ],
        ["a"],
        False,
        "t[0] += [2] executes in two steps: the list's __iadd__ mutates it in place and returns "
        "it, then Python attempts t.__setitem__(0, result) -- which tuples forbid. The exception "
        "comes from the second step, after the mutation already happened: a vivid demo that "
        "augmented assignment is read-modify-STORE.",
    ),
    (
        "iter_sentinel",
        1850,
        "What does the two-argument form `iter(fn, sentinel)` do?",
        [
            ("a", "Iterates fn's attributes until it hits sentinel"),
            ("b", "Returns an iterator that CALLS fn() repeatedly, yielding each result until one equals the sentinel (which is not yielded)"),
            ("c", "Pads fn's output with sentinel values"),
            ("d", "It's a deprecated alias for itertools.takewhile"),
        ],
        ["b"],
        False,
        "This turns any zero-argument callable into an iterator with a stop condition -- the "
        "classic idiom is `for block in iter(lambda: f.read(8192), b\"\"):` to read a file in "
        "chunks until EOF. Comparison with the sentinel uses ==, and the sentinel itself is never "
        "produced.",
    ),
    (
        "set_name_hook",
        1850,
        "What is the descriptor method `__set_name__(self, owner, name)` for, and when is it invoked?",
        [
            ("a", "It's called once at CLASS CREATION time for each descriptor assigned in the class body, telling the descriptor which class owns it and what attribute name it was bound to"),
            ("b", "It's called every time the attribute is reassigned on an instance"),
            ("c", "It renames the descriptor's class"),
            ("d", "It's invoked by dataclasses only"),
        ],
        ["a"],
        False,
        "Before __set_name__ (PEP 487), a validator descriptor couldn't know its own attribute "
        "name without repeating it (x = Positive('x')) or using a metaclass. Now type's "
        "construction calls __set_name__ on every descriptor found in the namespace, so it can "
        "store the name and stash per-instance data under e.g. '_x' automatically.",
    ),
    (
        "id_semantics",
        1900,
        "What does Python actually guarantee about the value returned by id(obj)?",
        [
            ("a", "It's the object's memory address in every implementation"),
            ("b", "It's unique and constant only for the object's LIFETIME -- after the object dies, its id may be reused by a new object"),
            ("c", "It's globally unique for the life of the process"),
            ("d", "It's stable across program runs for the same literal"),
        ],
        ["b"],
        False,
        "The language spec promises uniqueness only among simultaneously-alive objects. CPython "
        "returns the memory address (an implementation detail), and allocators aggressively reuse "
        "memory -- so `id(SomeClass()) == id(SomeClass())` is often True because the first "
        "instance dies before the second is allocated at the same address.",
    ),
    (
        "getrefcount",
        1900,
        "Why does `sys.getrefcount(x)` report a count one higher than the number of references you can account for?",
        [
            ("a", "CPython pads all refcounts by one to avoid zero"),
            ("b", "The call itself creates a temporary reference: x is bound to the function's parameter for the duration of the call"),
            ("c", "The GIL holds a reference to every live object"),
            ("d", "getrefcount includes weak references"),
        ],
        ["b"],
        False,
        "Passing x as an argument increments its refcount while the call is in flight, so the "
        "minimum you'll ever see for a temporary is 2 (in 3.11+ often more, due to internal "
        "call-machinery references). It's a diagnostic curiosity, not a precision tool -- and "
        "immortal objects like None report huge fixed values in 3.12+.",
    ),
    (
        "dict_collision",
        1950,
        "Two different keys in a dict happen to have equal hashes. What happens on lookup?",
        [
            ("a", "The lookup still works: the dict probes to the candidate slot(s) and uses == to distinguish the keys; collisions cost performance, not correctness"),
            ("b", "The second insertion overwrites the first"),
            ("c", "A HashCollisionError is raised"),
            ("d", "Both keys become inaccessible"),
        ],
        ["a"],
        False,
        "Hashes pick the probe sequence; equality confirms the match, so colliding keys coexist "
        "fine (hash(-1) == hash(-2) == -2 in CPython, yet both work as keys). This is also why "
        "`__hash__` may legally be coarse -- and why an attacker feeding many colliding keys "
        "degrades dicts toward O(n), which is why str hashing is randomized per process.",
    ),
    (
        "generator_return_value",
        1950,
        "def g():\n    yield 1\n    return 42\n\nWhere does the 42 go when the generator finishes?",
        [
            ("a", "It's lost; return values in generators are discarded silently"),
            ("b", "It's yielded as the final item"),
            ("c", "It's attached to the StopIteration exception (StopIteration.value) -- and becomes the value of a `yield from g()` expression in a delegating generator"),
            ("d", "return with a value is a SyntaxError inside a generator"),
        ],
        ["c"],
        False,
        "A generator's return raises StopIteration carrying the value; plain for loops swallow "
        "it, but `result = yield from g()` receives it -- the mechanism PEP 380 added so "
        "generators can compute results for their delegators, and the foundation the pre-"
        "async/await generator-based coroutines were built on.",
    ),
    (
        "eq_notimplemented",
        2000,
        "For `a == b`, both a's and b's __eq__ return NotImplemented. What does the expression evaluate to?",
        [
            ("a", "It raises TypeError, like < does in the same situation"),
            ("b", "NotImplemented"),
            ("c", "Python falls back to identity: True iff a is b"),
            ("d", "False, unconditionally"),
        ],
        ["c"],
        False,
        "Equality has a final fallback that ordering comparisons lack: when neither operand's "
        "__eq__ claims the comparison, == degrades to `is` (and != to `is not`) rather than "
        "raising. That's why comparing unrelated objects with == is always safe, while a < b "
        "between unrelated types raises TypeError.",
    ),
    (
        "dict_missing",
        2000,
        "You define __missing__(self, key) on a dict subclass. Which operations invoke it?",
        [
            ("a", "Only d[key] (dict.__getitem__) when the key is absent -- d.get(key) and `key in d` never call it"),
            ("b", "Every failed key operation, including get() and membership tests"),
            ("c", "Only iteration over missing keys"),
            ("d", "It's called for every lookup, hit or miss"),
        ],
        ["a"],
        False,
        "__missing__ is a hook wired specifically into dict.__getitem__'s miss path -- it's how "
        "defaultdict is implemented (its factory logic lives in __missing__). get(), in, and "
        "setdefault() bypass it entirely, which surprises people who expect subclass-wide "
        "default behavior.",
    ),
    (
        "mro_conflict",
        2000,
        "class A: pass\nclass B(A): pass\nclass C(A, B): pass\n\nWhat happens at the definition of C?",
        [
            ("a", "TypeError: no consistent MRO -- listing A before B contradicts B being a subclass of A"),
            ("b", "It works; the MRO is C, A, B"),
            ("c", "It works; duplicate ancestors are deduplicated automatically"),
            ("d", "A DeprecationWarning, then depth-first resolution"),
        ],
        ["a"],
        False,
        "C3 linearization must honor two constraints simultaneously: bases appear in the order "
        "listed (A before B), and every subclass precedes its ancestors (B before A). They're "
        "contradictory here, so class creation itself fails -- the fix is writing C(B, A), "
        "most-derived first.",
    ),
    (
        "free_threaded_build",
        2000,
        "What is the 'free-threaded' CPython build introduced by PEP 703 (Python 3.13)?",
        [
            ("a", "The new default interpreter with the GIL removed"),
            ("b", "A separate, opt-in build of CPython without a GIL, using techniques like biased reference counting and per-object locks -- threads can run Python code in parallel, and C extensions must explicitly declare support"),
            ("c", "A JIT compiler that eliminates bytecode"),
            ("d", "A mode where each thread gets its own sub-interpreter"),
        ],
        ["b"],
        False,
        "Free-threading makes refcounting and internal structures thread-safe without a global "
        "lock, so CPU-bound threads finally scale across cores -- at some single-thread overhead. "
        "It ships alongside the regular GIL build (python3.13t), and extensions signal "
        "compatibility via Py_mod_gil; incompatible ones re-enable the GIL at import.",
    ),
    (
        "cached_property",
        2000,
        "How does functools.cached_property cache, and why does it fail on a class that defines __slots__?",
        [
            ("a", "It keeps a global WeakKeyDictionary; slots break weak references"),
            ("b", "It stores the computed value in the instance's __dict__ under its own name -- being a non-data descriptor, the dict entry then shadows it on later reads. With __slots__ there's no instance __dict__ to write into"),
            ("c", "It caches on the class, so slots are irrelevant; the real conflict is with inheritance"),
            ("d", "It memoizes via lru_cache keyed on self"),
        ],
        ["b"],
        False,
        "cached_property implements only __get__: the first access computes the value and plants "
        "it in instance.__dict__, and because instance dicts take precedence over non-data "
        "descriptors, subsequent reads never reach the descriptor at all -- zero steady-state "
        "overhead. That design hard-requires a mutable __dict__, which __slots__ removes.",
    ),
    (
        "data_descriptors",
        2050,
        "What's the precedence difference between data and non-data descriptors during attribute lookup?",
        [
            ("a", "A DATA descriptor (defines __set__ or __delete__) on the class beats an instance __dict__ entry; a NON-DATA descriptor (only __get__) is shadowed by one"),
            ("b", "Non-data descriptors always win because they're checked first"),
            ("c", "Precedence is alphabetical by attribute name"),
            ("d", "Instance __dict__ always wins over any descriptor"),
        ],
        ["a"],
        False,
        "object.__getattribute__'s order is: data descriptor on the type, then instance __dict__, "
        "then non-data descriptor/class attribute. That's why assigning over a property raises or "
        "routes through its setter (property defines __set__), while functions -- non-data "
        "descriptors -- can be shadowed per-instance, and cached_property exploits exactly that.",
    ),
    (
        "nan_containment",
        2100,
        "nan = float(\"nan\")\nnan == nan is False, yet `nan in [nan]` is True. Why?",
        [
            ("a", "Lists cache comparison results"),
            ("b", "in coerces NaN to None first"),
            ("c", "Container operations like __contains__ (and list equality) short-circuit with an IDENTITY check before calling ==, so the same NaN object matches itself"),
            ("d", "IEEE-754 requires containment checks to treat NaN as equal to itself"),
        ],
        ["c"],
        False,
        "CPython's rich-comparison helper for containers tests `x is y or x == y` per element as "
        "an optimization, deliberately assuming identity implies equality -- NaN is the famous "
        "violator. The same shortcut makes [nan] == [nan] True while nan == nan is False; a "
        "*different* NaN object would not be found.",
    ),
    (
        "str_hash_caching",
        2100,
        "What does a CPython str object do the first time hash() is called on it?",
        [
            ("a", "It computes the hash and CACHES it in a field of the string object, so every later hash() -- e.g. repeated dict lookups -- is a constant-time field read"),
            ("b", "Nothing special; the hash is recomputed on every call"),
            ("c", "It registers the string in the global intern table"),
            ("d", "It memoizes the hash in a process-wide dict keyed by the string's id"),
        ],
        ["a"],
        False,
        "Unicode objects carry a hash slot initialized to -1 (\"not yet computed\"); the first "
        "hash() fills it and subsequent calls just read it -- safe only because strings are "
        "immutable. Combined with per-process hash randomization (PYTHONHASHSEED), this is why "
        "string-keyed dict access stays fast even for long keys used repeatedly.",
    ),
    (
        "task_references",
        2100,
        "asyncio.create_task(job())  # fire-and-forget\n\nWhy is discarding the returned Task dangerous?",
        [
            ("a", "The event loop keeps only a WEAK reference to running tasks, so an unreferenced task can be garbage-collected and vanish mid-execution"),
            ("b", "Unreferenced tasks run at lower priority"),
            ("c", "The task's exceptions are raised in the main thread"),
            ("d", "It isn't; create_task pins the task until completion"),
        ],
        ["a"],
        False,
        "This is a documented asyncio gotcha: the loop does not own your tasks. Hold a strong "
        "reference until done -- e.g. add to a set and discard in a done-callback, or use "
        "asyncio.TaskGroup (3.11+), which keeps references and propagates failures for you. "
        "Fire-and-forget tasks also silently swallow exceptions until GC logs them.",
    ),
    (
        "module_getattr",
        2150,
        "PEP 562 lets a MODULE define __getattr__ at top level. When is it called and what's it for?",
        [
            ("a", "On every attribute access on the module, replacing normal lookup"),
            ("b", "Only when a module attribute is NOT found normally -- enabling lazy submodule imports and clean deprecation warnings for old names"),
            ("c", "Only during `from mod import *`"),
            ("d", "It's called at import time to build the module namespace"),
        ],
        ["b"],
        False,
        "Module __getattr__(name) is the miss-handler for module attribute lookup, mirroring the "
        "class-level protocol: heavyweight submodules can be imported on first touch, and "
        "renamed/removed attributes can emit DeprecationWarning then return the replacement. "
        "PEP 562 also allows module __dir__ to match.",
    ),
    (
        "closure_cells",
        2150,
        "How does CPython implement closures at the object level?",
        [
            ("a", "The inner function stores a copy of each captured value at definition time"),
            ("b", "Captured variables live in CELL objects shared between the enclosing frame and the inner function's __closure__ tuple; reads and nonlocal writes go through the cell"),
            ("c", "The enclosing frame is kept alive whole, and lookups walk the frame chain at call time"),
            ("d", "Captured names are compiled into module-level globals"),
        ],
        ["b"],
        False,
        "Variables captured by an inner function are promoted to cells (visible as "
        "fn.__closure__[i].cell_contents); both scopes read/write the SAME cell, which is why "
        "closures see later rebindings (late binding, the loop-variable lambda gotcha) and why "
        "nonlocal works -- it writes through the shared cell rather than a local slot.",
    ),
    (
        "metaclass_call",
        2200,
        "To make `Config()` always return one shared instance (a singleton), which method is the most direct interception point?",
        [
            ("a", "__call__ on Config's METACLASS -- it's what runs when the class object is called, wrapping the __new__/__init__ sequence"),
            ("b", "__call__ on Config itself"),
            ("c", "__init__ on Config, returning the cached instance"),
            ("d", "__init_subclass__ on Config"),
        ],
        ["a"],
        False,
        "Instantiation IS a call on the class object, dispatched to type(Config).__call__ -- "
        "override that in a metaclass to consult a cache before invoking type.__call__. "
        "Config.__call__ would affect calling *instances*, and __init__ can't change what gets "
        "returned (its return value must be None); only __new__ or the metaclass can substitute "
        "the object.",
    ),
    (
        "str_concat_optimization",
        2250,
        "s += t in a loop is 'supposed' to be O(n^2) for immutable strings, yet in CPython it's often fast. Why -- and why not rely on it?",
        [
            ("a", "CPython interns all intermediate strings"),
            ("b", "When the target holds the ONLY reference (refcount 1), CPython mutates/resizes the string in place instead of copying -- an implementation detail that breaks if another reference exists, and doesn't exist in some other implementations"),
            ("c", "The compiler rewrites the loop into a join at parse time"),
            ("d", "Small strings are stored in a rope structure"),
        ],
        ["b"],
        False,
        "unicode_concatenate checks the refcount: with no other holders, 'immutability' can't be "
        "observed, so it reallocs in place, amortizing to roughly O(n). Alias the accumulator "
        "(or run on a runtime without the hack, or historically GIL-free builds where refcounts "
        "aren't as simple) and you're back to quadratic -- str.join remains the guaranteed "
        "linear idiom.",
    ),
    (
        "slots_weakref",
        2250,
        "weakref.ref(obj) raises \"TypeError: cannot create weak reference\" for instances of a __slots__ class. What's the fix?",
        [
            ("a", "Add '__weakref__' to __slots__ -- slotted layouts omit the weak-reference pointer unless you reserve it"),
            ("b", "Weak references fundamentally require a __dict__; remove __slots__"),
            ("c", "Register the class with weakref.enable(cls)"),
            ("d", "Use weakref.proxy, which doesn't need object support"),
        ],
        ["a"],
        False,
        "Weak-referenceability normally comes from a hidden __weakref__ slot in the instance "
        "layout; declaring __slots__ builds a minimal layout without it. Reserving '__weakref__' "
        "(in exactly one class of the hierarchy, or it's a TypeError/conflict) restores support "
        "at the cost of one pointer per instance -- same idea as adding '__dict__' back "
        "explicitly.",
    ),
    (
        "gc_freeze",
        2350,
        "What is gc.freeze() for?",
        [
            ("a", "It permanently disables garbage collection"),
            ("b", "It moves every currently-tracked object into a 'permanent generation' the collector never scans -- used before fork() so GC in child processes doesn't touch (and copy-on-write-invalidate) memory pages shared with the parent"),
            ("c", "It pins objects so id() stays stable"),
            ("d", "It compacts the heap to reduce fragmentation"),
        ],
        ["b"],
        False,
        "In pre-fork servers, child processes share the parent's memory copy-on-write; the cyclic "
        "collector writing GC headers (and collections moving objects between generations) "
        "dirties those shared pages, ballooning real memory. freeze() after warm-up parks "
        "existing objects out of the collector's reach -- a technique popularized by "
        "Instagram's CPython fleet. gc.unfreeze() reverses it.",
    ),
    (
        "metaclass_prepare",
        2400,
        "What does a metaclass's __prepare__ method control?",
        [
            ("a", "The MAPPING object used as the namespace while the class body executes -- returning an ordered or validating mapping lets you observe definition order or forbid duplicate names before the class exists"),
            ("b", "Which base classes are permitted"),
            ("c", "The memory layout of instances"),
            ("d", "Whether the class is pickled by reference or by value"),
        ],
        ["a"],
        False,
        "Class creation runs the body's code against a namespace that __prepare__(name, bases, "
        "**kwds) supplies (default: a plain dict); the filled mapping is then passed to the "
        "metaclass's __new__. Enum uses exactly this -- a custom mapping that intercepts each "
        "member assignment -- and pre-3.6 ordered-attribute tricks lived here before dicts "
        "preserved insertion order.",
    ),
    (
        "specializing_interpreter",
        2450,
        "What does CPython 3.11's 'specializing adaptive interpreter' (PEP 659) do?",
        [
            ("a", "Compiles hot functions to native machine code"),
            ("b", "At runtime, it rewrites individual bytecodes in hot code into type-specialized variants based on observed operands (e.g. BINARY_OP for two ints), with guards that de-specialize if assumptions stop holding"),
            ("c", "Reorders bytecode at import time based on profiles from previous runs"),
            ("d", "Replaces the stack machine with a register machine"),
        ],
        ["b"],
        False,
        "It's inline caching without a JIT: generic instructions 'quicken' into fast paths "
        "(specialized attribute loads, int/float arithmetic, exact-dict subscripts) after warming "
        "up, guarded so misses fall back and eventually re-adapt. A major slice of the 3.11 "
        "'Faster CPython' speedup -- and the groundwork the 3.13+ experimental JIT builds on.",
    ),
    (
        "pymalloc",
        2500,
        "Which allocations does CPython's pymalloc allocator handle, and how?",
        [
            ("a", "All Python objects, via a compacting generational heap"),
            ("b", "Requests of 512 bytes or less, served from size-class pools carved out of larger arenas -- bigger requests fall through to the system malloc"),
            ("c", "Only ints and floats, via freelists"),
            ("d", "Nothing by default; it must be enabled with -X pymalloc"),
        ],
        ["b"],
        False,
        "Most Python objects are small and die young, so pymalloc optimizes exactly that case: "
        "arenas (256 KiB) are divided into 4 KiB pools, each pool dedicated to one size class "
        "(8-byte steps up to 512), making alloc/free of small objects a few pointer operations "
        "with no per-object syscalls. Separate from this, some types (floats, tuples, lists) "
        "keep their own freelists to recycle recently-freed objects even faster.",
    ),
]
