"""Broad engineering-knowledge trivia for the systems_trivia quiz category:
concurrency, databases, distributed systems, data lakes, big data, AI agents,
AI serving infra, AI tuning/eval, harnesses, plus classic system-design
fundamentals (CAP, caching, load balancing, queues).

Same tuple shape as seed_data_python.py: (topic, difficulty, prompt_md,
choices, correct_keys, multi_select, explanation_md).

Starter set spanning the difficulty range; meant to grow to ~150-200
questions (see the quiz-modes phase plan).
"""

QUESTIONS: list[tuple[str, int, str, list[tuple[str, str]], list[str], bool, str]] = [
    (
        "caching",
        350,
        "What is 'cache invalidation' widely considered one of the hardest problems in computer science?",
        [
            ("a", "Because deciding when cached data is stale enough to refresh is subtle and error-prone"),
            ("b", "Because caches are always slower than the database"),
            ("c", "Because caches can only store strings"),
            ("d", "It isn't hard -- caches invalidate themselves automatically"),
        ],
        ["a"],
        False,
        "There's no free lunch: too aggressive invalidation loses the caching benefit, too lax and "
        "users see stale data -- and the 'right' staleness tolerance differs per piece of data.",
    ),
    (
        "load_balancing",
        400,
        "What does a load balancer using 'round robin' do?",
        [
            ("a", "Sends each new request to the next server in a fixed rotation"),
            ("b", "Sends every request to whichever server has the least CPU load"),
            ("c", "Sends all traffic to one server until it fails"),
            ("d", "Randomly drops a fraction of requests to reduce load"),
        ],
        ["a"],
        False,
        "Round robin is the simplest load-balancing strategy: cycle through the pool of servers in "
        "order. It doesn't account for actual server load, which is why weighted or least-connections "
        "strategies exist for uneven backends.",
    ),
    (
        "concurrency",
        450,
        "What's the difference between concurrency and parallelism?",
        [
            ("a", "Concurrency is structuring a program to deal with many things at once; parallelism is actually doing many things at the same instant"),
            ("b", "They're exactly the same thing"),
            ("c", "Concurrency requires multiple CPUs; parallelism doesn't"),
            ("d", "Parallelism only applies to distributed systems, concurrency only to single machines"),
        ],
        ["a"],
        False,
        "A single-core machine can be concurrent (interleaving tasks) without being parallel (executing "
        "them simultaneously) -- parallelism needs multiple execution units, concurrency is a program-"
        "structure concept independent of hardware.",
    ),
    (
        "databases",
        500,
        "What guarantee does a database transaction's 'atomicity' provide?",
        [
            ("a", "All of the transaction's operations happen, or none of them do"),
            ("b", "The transaction runs faster than non-transactional operations"),
            ("c", "Two transactions can never touch the same row"),
            ("d", "The transaction is encrypted at rest"),
        ],
        ["a"],
        False,
        "Atomicity is the 'A' in ACID: a transaction is all-or-nothing -- if any part fails, the whole "
        "thing rolls back, so the database never ends up in a half-applied state.",
    ),
    (
        "databases",
        600,
        "Why does adding a database index speed up reads but slow down writes?",
        [
            ("a", "Every write must also update the index's data structure, not just the table"),
            ("b", "Indexes make the table itself smaller"),
            ("c", "Indexes are only used for writes, not reads"),
            ("d", "It doesn't -- indexes have no effect on writes"),
        ],
        ["a"],
        False,
        "An index (typically a B-tree) is extra structure kept in sync with the table -- reads use it to "
        "avoid scanning every row, but every insert/update/delete now has to maintain that structure too.",
    ),
    (
        "message_queues",
        700,
        "What problem do message queues (e.g. Kafka, SQS, RabbitMQ) primarily solve between services?",
        [
            ("a", "Decoupling producers and consumers so they don't need to be online/fast at the same time"),
            ("b", "Making all network calls synchronous"),
            ("c", "Replacing the need for a database"),
            ("d", "Guaranteeing zero message loss with no configuration required"),
        ],
        ["a"],
        False,
        "A queue lets a producer publish work without waiting on a consumer to process it right away -- "
        "buffering load spikes, allowing independent scaling/deploys, and surviving a consumer being "
        "temporarily down.",
    ),
    (
        "cap_theorem",
        900,
        "Under a network partition, the CAP theorem says a distributed data store must choose between:",
        [
            ("a", "Consistency and Availability"),
            ("b", "Consistency and Durability"),
            ("c", "Availability and Latency"),
            ("d", "Partition tolerance and Scalability"),
        ],
        ["a"],
        False,
        "CAP theorem: when a network partition happens (and partitions are a fact of distributed "
        "systems), you must pick between Consistency (every read sees the latest write) and "
        "Availability (every request gets a response) -- you can't have both during the partition.",
    ),
    (
        "concurrency",
        1000,
        "What is a 'race condition'?",
        [
            ("a", "A bug where the correctness of a result depends on the unpredictable timing/ordering of concurrent operations"),
            ("b", "A CPU running too many threads at once"),
            ("c", "A deadlock between two processes"),
            ("d", "A network request that times out"),
        ],
        ["a"],
        False,
        "A race condition happens when multiple threads/processes access shared state without proper "
        "synchronization, so the outcome depends on scheduling -- often correct 99% of the time and "
        "wrong under just the right (or wrong) interleaving.",
    ),
    (
        "distributed_systems",
        1100,
        "In distributed systems, what does 'idempotent' mean for an operation like an API request?",
        [
            ("a", "Performing it multiple times has the same effect as performing it once"),
            ("b", "It always returns the same response body"),
            ("c", "It can never fail"),
            ("d", "It only works over HTTPS"),
        ],
        ["a"],
        False,
        "Idempotency matters for retries: if a client times out and resends a request, an idempotent "
        "endpoint (e.g. 'set balance to $50', or a request carrying a dedup key) won't double-apply the "
        "effect the way a naive 'add $50' would.",
    ),
    (
        "big_data",
        1150,
        "In the MapReduce model, what does the 'shuffle' phase do?",
        [
            ("a", "Routes all mapper output for a given key to the same reducer"),
            ("b", "Randomly reorders the input data before mapping"),
            ("c", "Compresses the final output"),
            ("d", "Retries failed mapper tasks"),
        ],
        ["a"],
        False,
        "Between map and reduce, the shuffle/sort phase partitions and transfers intermediate "
        "key-value pairs across the cluster so that every value for a given key ends up at the same "
        "reducer, which is what makes the reduce step's aggregation correct.",
    ),
    (
        "data_lakes",
        1200,
        "What's the key structural difference between a data lake and a data warehouse?",
        [
            ("a", "A data lake stores raw data in its native format (schema-on-read); a warehouse stores structured, transformed data (schema-on-write)"),
            ("b", "A data lake can only store images and video"),
            ("c", "A data warehouse has no concept of tables"),
            ("d", "There is no difference, the terms are interchangeable"),
        ],
        ["a"],
        False,
        "Data lakes prioritize ingesting everything cheaply and deciding the schema at query time; "
        "warehouses require upfront ETL into a defined schema, trading ingestion flexibility for "
        "query performance/governance.",
    ),
    (
        "ai_agents",
        1250,
        "In an LLM 'agent' architecture, what is the core loop that distinguishes it from a single "
        "prompt-response call?",
        [
            ("a", "The model repeatedly chooses actions/tools, observes results, and decides the next step until a goal is met"),
            ("b", "The model is fine-tuned once and never called again"),
            ("c", "Multiple separate models vote on a single answer simultaneously"),
            ("d", "The prompt is simply longer than a normal chat message"),
        ],
        ["a"],
        False,
        "Agent frameworks wrap an LLM in a loop -- plan/act/observe -- where the model can invoke tools "
        "(search, code execution, APIs), see the results, and decide whether to continue, retry, or "
        "finish, rather than producing one final answer from a single forward pass.",
    ),
    (
        "distributed_systems",
        1300,
        "What problem does a consensus algorithm like Raft or Paxos solve?",
        [
            ("a", "Getting a cluster of nodes to agree on a single value/log order despite failures"),
            ("b", "Encrypting traffic between nodes"),
            ("c", "Load balancing HTTP requests"),
            ("d", "Compressing data before replication"),
        ],
        ["a"],
        False,
        "Consensus protocols let a set of unreliable nodes agree on an ordered sequence of operations "
        "(e.g. a replicated log) even if some nodes crash or messages are delayed -- the foundation for "
        "strongly-consistent replicated systems.",
    ),
    (
        "ai_serving_infra",
        1400,
        "Why do LLM inference servers (e.g. vLLM) use 'continuous batching' instead of simple static "
        "batching?",
        [
            ("a", "Because requests finish generating at different token lengths, so slotting in new requests as others finish keeps GPU utilization high"),
            ("b", "Because it reduces the model's parameter count"),
            ("c", "Because it removes the need for a GPU entirely"),
            ("d", "Because it guarantees identical latency for every request"),
        ],
        ["a"],
        False,
        "Static batches wait for the slowest sequence in the batch before starting a new one, wasting "
        "GPU time on finished sequences. Continuous (in-flight) batching swaps completed sequences out "
        "and new ones in at each decoding step, which is a major throughput win.",
    ),
    (
        "ai_serving_infra",
        1450,
        "What does KV-cache refer to in transformer inference serving?",
        [
            ("a", "Cached key/value projections from previous tokens, reused so each new token isn't recomputed from scratch"),
            ("b", "A cache of user API keys for authentication"),
            ("c", "A disk cache of model checkpoint files"),
            ("d", "A cache mapping prompts to final responses"),
        ],
        ["a"],
        False,
        "Autoregressive generation would otherwise recompute attention over the whole sequence at every "
        "step; caching each layer's key/value tensors for prior tokens turns that into an O(1)-per-step "
        "append, at the cost of memory proportional to sequence length and batch size.",
    ),
    (
        "ai_tuning_eval",
        1500,
        "What's the main practical difference between full fine-tuning and LoRA (Low-Rank Adaptation)?",
        [
            ("a", "LoRA freezes the base model weights and trains small low-rank adapter matrices instead of all parameters"),
            ("b", "LoRA requires more GPU memory than full fine-tuning"),
            ("c", "Full fine-tuning cannot change the model's behavior at all"),
            ("d", "LoRA only works on vision models, not language models"),
        ],
        ["a"],
        False,
        "LoRA inserts small trainable low-rank matrices alongside frozen pretrained weights, cutting "
        "trainable parameters (and memory/compute) drastically versus updating every weight, while "
        "often getting close to full fine-tuning quality for many tasks.",
    ),
    (
        "harnesses",
        1550,
        "In the context of coding/agent evals, what is a 'harness'?",
        [
            ("a", "The surrounding scaffolding that gives a model tools, an environment, and a way to submit an answer for grading"),
            ("b", "A synonym for the model's training dataset"),
            ("c", "A hardware device for running GPUs safely"),
            ("d", "The model's system prompt and nothing else"),
        ],
        ["a"],
        False,
        "A harness is the infrastructure around the model under test: tool APIs, sandboxed execution, "
        "how many turns it gets, and how its final output is scored -- the same model can score very "
        "differently under different harnesses, which is why harness design is itself a research area.",
    ),
    (
        "ai_tuning_eval",
        1650,
        "Why is 'benchmark contamination' a concern when evaluating LLMs?",
        [
            ("a", "If benchmark questions leaked into training data, the model may appear to 'reason' when it actually memorized the answer"),
            ("b", "It refers to GPUs overheating during evaluation runs"),
            ("c", "It only affects image classification models"),
            ("d", "It means the benchmark's test set is too small to matter"),
        ],
        ["a"],
        False,
        "If a benchmark's exact questions (or close paraphrases) end up in a model's pretraining or "
        "fine-tuning data, a high score reflects memorization rather than the general capability the "
        "benchmark was meant to measure -- undermining the whole comparison.",
    ),
    (
        "distributed_systems",
        1750,
        "What's the core idea behind vector clocks in distributed systems?",
        [
            ("a", "Tracking per-node event counters so causal ordering between events on different nodes can be detected without a shared clock"),
            ("b", "Synchronizing wall-clock time exactly across all nodes"),
            ("c", "A visual dashboard for monitoring cluster health"),
            ("d", "A way to compress timestamps for storage"),
        ],
        ["a"],
        False,
        "Since nodes can't perfectly agree on wall-clock time, a vector clock (one counter per node) "
        "lets you determine whether event A causally happened-before event B, or whether they're "
        "concurrent -- without relying on synchronized clocks.",
    ),
    (
        "big_data",
        1850,
        "Why do big-data query engines (e.g. Spark, Presto/Trino) favor columnar storage formats like "
        "Parquet for analytical workloads?",
        [
            ("a", "A query touching a few columns out of many can skip reading the rest, and same-typed values compress better together"),
            ("b", "Columnar formats are required for any data larger than 1GB"),
            ("c", "Row-based formats cannot be compressed at all"),
            ("d", "Columnar storage removes the need for a query planner"),
        ],
        ["a"],
        False,
        "Analytical queries typically aggregate a handful of columns across huge row counts -- columnar "
        "layout lets the engine read only those columns (huge I/O savings) and compress each column's "
        "homogeneous values far better than row-major storage.",
    ),
    (
        "ai_agents",
        1950,
        "What does 'reflection' or 'self-critique' refer to in agent architectures?",
        [
            ("a", "Having the model review/critique its own intermediate output and revise before finalizing"),
            ("b", "Mirroring the user's tone back to them"),
            ("c", "Logging every API call the agent makes"),
            ("d", "Training two separate models to disagree with each other"),
        ],
        ["a"],
        False,
        "Reflection loops feed a model's own draft output back to it (or a critic prompt) to catch "
        "errors before committing to a final answer -- often improving quality at the cost of extra "
        "latency/tokens, a real tradeoff in agent harness design.",
    ),
    (
        "concurrency",
        2100,
        "What distinguishes a deadlock from a livelock?",
        [
            ("a", "In a deadlock nothing progresses at all; in a livelock, processes keep changing state but never make real progress"),
            ("b", "A deadlock only happens with more than 2 threads; a livelock only with exactly 2"),
            ("c", "They are the same phenomenon under different names"),
            ("d", "A livelock always resolves itself within one second"),
        ],
        ["a"],
        False,
        "In a deadlock, threads are blocked waiting on each other forever, fully stalled. In a livelock, "
        "threads keep actively responding to each other (e.g. both repeatedly yielding to avoid a "
        "collision) without any of them completing their work -- 'busy but stuck.'",
    ),
]
