"""Seed content for the System Design round. `difficulty` is an Elo-scale
content-difficulty rating (same scale as user ratings), roughly anchored to
easy=800, medium=1400, hard=2000 per CLAUDE.md. `rubric_md` is the ground-truth
grading rubric describing what a strong answer covers -- never sent to the
client. Each `prompt_md` bakes in a couple of concrete numeric constraints so
the design has something real to be measured against.
"""

PROMPTS: list[tuple[str, int, str, str]] = [
    (
        "URL Shortener",
        900,
        "Design a URL shortener (like bit.ly).\n\n"
        "**Constraints:** 100M new shortens/day; read-heavy at ~10:1 redirects to shortens; "
        "redirect latency < 50ms p99; links never expire; optional custom aliases.",
        "**Requirements a strong answer pins down:** ~1,200 writes/s and ~12k reads/s average "
        "(several x at peak); storage math (100M/day * ~500 bytes ≈ 18 TB/yr -- fits a sharded "
        "KV/relational store comfortably); redirects must be fast and highly available; eventual "
        "consistency is fine for analytics but a new link must resolve immediately.\n\n"
        "**High-level design:** API (`POST /shorten`, `GET /{code}` returning 301/302 -- bonus for "
        "discussing 301 vs 302 and its caching/analytics tradeoff); a key-generation service; a "
        "store mapping code -> long URL; a cache (Redis/CDN) in front of the store for hot links "
        "-- without a cache the 50ms p99 target is at risk.\n\n"
        "**Deep dives that matter:** (1) Short-code generation: base62 over an auto-increment ID or "
        "distributed ID (Snowflake) vs hashing with collision retry vs a pre-generated key pool; "
        "7 base62 chars ≈ 3.5T codes is enough. Custom aliases need a uniqueness check "
        "(unique constraint / conditional put). (2) Read path: cache-aside with high hit rate, "
        "handling cache misses and hot keys; 404 handling for unknown codes (negative caching, "
        "bloom filter as a bonus).\n\n"
        "**Tradeoffs & scaling:** DB sharding by code (hash-based) and why that keeps redirects "
        "single-shard; counter-based ID generation being a single point of contention and how to "
        "fix it (ranges per node); rate limiting shorten abuse. Analytics (click counts) should be "
        "async (queue/stream), never on the redirect path.",
    ),
    (
        "API Rate Limiter",
        1000,
        "Design a rate limiter for a public API platform.\n\n"
        "**Constraints:** 100k requests/s across the fleet; per-user limits (e.g. 100 req/min) plus "
        "per-endpoint limits; decision latency budget < 5ms; limits must hold approximately across "
        "multiple API-gateway nodes; return HTTP 429 with a Retry-After header.",
        "**Requirements a strong answer pins down:** accuracy vs latency tradeoff (a strictly exact "
        "global counter is too slow; slight over-admission is acceptable); where it sits "
        "(middleware in the gateway); what a rule looks like (key = user/API-key + endpoint, "
        "window, limit); fail-open vs fail-closed when the limiter's store is down.\n\n"
        "**High-level design:** gateway middleware consulting a shared counter store (Redis) keyed "
        "by client+rule; rules config service; 429 + Retry-After + rate-limit headers on rejection.\n\n"
        "**Deep dives that matter:** (1) Algorithm choice with actual mechanics: token bucket / "
        "leaky bucket / fixed window (and its boundary-burst flaw) / sliding window log (memory "
        "cost) / sliding window counter as the practical compromise. Expect at least token bucket "
        "or sliding-window counter explained concretely, including atomicity (Redis Lua/INCR+EXPIRE "
        "to avoid read-modify-write races). (2) Distributed enforcement: centralized Redis (adds "
        "~1-2ms, needs clustering by key) vs local counters with async sync (fast but approximate); "
        "the 5ms budget essentially forces one of these and the choice should be justified.\n\n"
        "**Tradeoffs & scaling:** hot-key handling for a single abusive user; Redis failure "
        "behavior (fail-open for availability is the usual call -- should be an explicit decision); "
        "memory footprint per active client; how rule changes propagate.",
    ),
    (
        "Parking Garage System",
        700,
        "Design the software for a multi-level parking garage (object-oriented design, not a "
        "distributed system).\n\n"
        "**Constraints:** 4 levels, ~200 spots each; three spot sizes (motorcycle, compact, large); "
        "entry kiosks issue tickets, exit kiosks take payment; pricing by vehicle size and duration; "
        "display of free spots per level must update within ~1 second.",
        "**Requirements a strong answer pins down:** this is an OOD problem -- the grader wants "
        "clean classes and responsibilities, not microservices. Core flows: vehicle arrives -> "
        "assign appropriate spot -> issue ticket; vehicle exits -> compute fee -> free spot; "
        "spot-availability display. Rules: a motorcycle fits any spot, a compact fits "
        "compact/large, a large fits only large (or a stated variant).\n\n"
        "**High-level design (classes):** `ParkingGarage` -> `Level` -> `Spot(size, occupied)`; "
        "`Vehicle` hierarchy (Motorcycle/Car/Truck) or a size enum; `Ticket(id, entry_time, "
        "vehicle, spot)`; `EntryKiosk`/`ExitKiosk`; a `PricingStrategy` interface so pricing rules "
        "can change without touching kiosk logic; an `AvailabilityBoard` observing spot changes.\n\n"
        "**Deep dives that matter:** (1) Spot assignment: per-level free lists (or min-heaps) keyed "
        "by spot size for O(1)/O(log n) allocation, and the fallback order when the preferred size "
        "is full. (2) Concurrency at the boundaries: two entry kiosks must not assign the same spot "
        "-- lock or atomic reservation on the free list.\n\n"
        "**Tradeoffs & scaling:** strategy pattern for pricing (hourly vs daily cap vs lost "
        "ticket); observer pattern (or simple event) for the display board; persistence of tickets "
        "so a crash doesn't strand cars; extensibility to EV-charging or reserved spots.",
    ),
    (
        "Notification System",
        1300,
        "Design a notification system that sends push, email, and SMS for a large consumer app.\n\n"
        "**Constraints:** 150M notifications/day across all channels, with marketing campaign "
        "bursts of 1M+ in minutes; at-least-once delivery with no duplicates visible to users where "
        "possible; per-user channel preferences and quiet hours must be respected; OTP/security "
        "messages must go out in < 1 minute even during campaign bursts.",
        "**Requirements a strong answer pins down:** ~1,700/s average but very bursty -- the design "
        "must be queue-backed, not synchronous; priority classes (transactional/OTP vs marketing) "
        "with the stated <1min SLA for OTP; preference/opt-out checking is a hard requirement "
        "(legal), not a nice-to-have; third-party providers (APNs, FCM, SES, Twilio) are rate-"
        "limited and flaky.\n\n"
        "**High-level design:** producer API for internal services -> validation + preference/"
        "quiet-hours filter -> priority queues (separate queues per priority and/or channel, so a "
        "marketing flood can't starve OTP) -> per-channel worker pools calling providers -> status/"
        "receipt tracking store. A template service and a user-contact/device-token store.\n\n"
        "**Deep dives that matter:** (1) Delivery semantics: retries with exponential backoff, "
        "idempotency keys / dedup store so retries don't double-send, DLQ for poison messages, "
        "provider failover. (2) Burst handling: queue buffering, worker autoscaling, rate limiting "
        "toward providers, and why priority isolation (separate queues, reserved workers) protects "
        "the OTP SLA.\n\n"
        "**Tradeoffs & scaling:** at-least-once + dedup vs exactly-once claims (should be "
        "skeptical of exactly-once); fan-out for campaign sends (materialize 1M messages via "
        "batch/stream job); observability -- per-channel delivery rates, provider health; storing "
        "notification status for in-app display.",
    ),
    (
        "News Feed",
        1500,
        "Design the home feed for a social network (like Twitter/X or Instagram).\n\n"
        "**Constraints:** 300M DAU; average user follows 400 accounts; feed load p99 < 200ms; a new "
        "post should appear in followers' feeds within ~10 seconds; celebrity accounts have up to "
        "100M followers; feed is ranked, not strictly chronological.",
        "**Requirements a strong answer pins down:** read-to-write ratio is extreme (feed loads "
        "dominate posts); the celebrity number is in the prompt specifically to force the fan-out "
        "discussion; 200ms p99 means feeds must be precomputed or cached, not assembled from 400 "
        "queries at request time.\n\n"
        "**High-level design:** post service + post store; follow graph service; fan-out service "
        "consuming new posts; per-user feed cache (Redis lists/sorted sets of post IDs); feed API "
        "that reads the feed cache, hydrates posts, and applies ranking; media via blob store + "
        "CDN.\n\n"
        "**Deep dives that matter:** (1) Fan-out on write (push post ID to each follower's feed "
        "cache -- fast reads, but a 100M-follower post is 100M writes) vs fan-out on read (pull at "
        "request time -- no write amplification but slow reads), and the standard hybrid: push for "
        "normal users, pull-and-merge for celebrity follows at read time. This tradeoff is the "
        "heart of the question and must be explicit. (2) Feed storage & ranking: store recent post "
        "IDs per user (bounded, e.g. last 500), hydrate + rank at read; where ranking scores come "
        "from; pagination via cursors.\n\n"
        "**Tradeoffs & scaling:** eventual consistency of the 10s freshness target vs read "
        "latency; cache memory math (300M users x ~500 IDs is large but feasible; inactive-user "
        "eviction); dedup/idempotency in fan-out workers; thundering herd on hot posts.",
    ),
    (
        "Chat Application",
        1500,
        "Design a 1:1 and small-group chat service (like WhatsApp).\n\n"
        "**Constraints:** 500M DAU with ~1B messages/day; message delivery latency < 500ms when "
        "both users are online; messages must never be lost once the server acks; support offline "
        "users (deliver on reconnect), delivery/read receipts, and group chats up to 512 members; "
        "messages stored server-side with per-conversation ordering.",
        "**Requirements a strong answer pins down:** persistent connections (WebSocket) rather "
        "than polling; durability rule -- persist before ack, then deliver; per-conversation "
        "ordering (global ordering is unnecessary); ~12k messages/s average, several x peak.\n\n"
        "**High-level design:** chat/gateway servers holding WebSocket connections; a session/"
        "presence registry mapping user -> gateway node (so a message to user B can be routed to "
        "the node holding B's socket); message store (wide-column store like Cassandra, partitioned "
        "by conversation ID, clustered by message ID/time); queue or pub/sub between gateways; "
        "push-notification hook for offline recipients.\n\n"
        "**Deep dives that matter:** (1) Message flow & reliability: sender -> gateway -> persist "
        "-> ack sender -> route to recipient's gateway -> deliver -> delivery receipt; client "
        "retries with idempotent message IDs; offline case writes to the store (per-user inbox or "
        "conversation cursor) and delivers on reconnect. (2) Message IDs & ordering: per-"
        "conversation monotonic IDs (or hybrid logical clocks); why device clocks can't be "
        "trusted; group chat as fan-out to member inboxes vs a shared conversation partition read "
        "by all members -- with the 512-member bound making server-side fan-out tractable.\n\n"
        "**Tradeoffs & scaling:** connection state makes gateways stateful -- reconnect/failover "
        "handling; presence heartbeats at 500M DAU are their own load problem; storage retention; "
        "end-to-end encryption mention is a bonus (changes what the server can store).",
    ),
    (
        "Distributed Cache",
        1400,
        "Design a distributed in-memory cache service (like Memcached/Redis cluster) used by other "
        "teams' services.\n\n"
        "**Constraints:** 1M ops/s aggregate at ~10:1 get:set; p99 read latency < 1ms in-"
        "datacenter; total capacity 1 TB across the fleet; adding/removing a node must not blow "
        "away the whole cache; per-key TTLs and LRU eviction under memory pressure.",
        "**Requirements a strong answer pins down:** it's a cache, not a database -- data loss on "
        "node failure is acceptable (misses fall through to the source of truth), which drives "
        "most tradeoffs; the 1ms p99 rules out disk and cross-region hops; client library vs "
        "proxy access model.\n\n"
        "**High-level design:** N cache nodes each owning a share of the keyspace; a routing "
        "layer (smart client or lightweight proxy) that hashes key -> node; cluster membership/"
        "config service so clients learn topology changes.\n\n"
        "**Deep dives that matter:** (1) Consistent hashing with virtual nodes -- why naive "
        "`hash(key) % N` remaps almost everything when N changes, how vnodes smooth load, and "
        "what happens on node add/remove (only ~1/N of keys move). This is the signature deep "
        "dive and should be concrete. (2) Eviction & expiry mechanics: LRU via doubly-linked list "
        "+ hash map (O(1)); lazy TTL expiry on read plus periodic sweep; memory accounting.\n\n"
        "**Tradeoffs & scaling:** hot keys (one celebrity key can saturate a node -- client-side "
        "caching, key replication, or request coalescing); thundering herd on expiry (stale-while-"
        "revalidate, request coalescing, jittered TTLs); optional replication for read scaling vs "
        "the consistency cost; cache stampede protection for downstream DBs.",
    ),
    (
        "Web Crawler",
        1400,
        "Design a web crawler that keeps a search index fresh.\n\n"
        "**Constraints:** crawl 1B pages/month (~400 pages/s sustained); strictly respect "
        "robots.txt and a per-domain politeness limit of 1 request/s; avoid re-crawling duplicate "
        "content; prioritize important/frequently-changing pages; the fetched corpus (~2 KB "
        "average per stored page ≈ 2 TB/month) feeds a downstream indexer.",
        "**Requirements a strong answer pins down:** the politeness constraint is the crux -- "
        "throughput must come from parallelism across millions of domains while each domain stays "
        "at <= 1 req/s; crawler traps (infinite calendars, session-ID URLs) and duplicate content "
        "are the other core problems; freshness implies re-crawl scheduling, not one pass.\n\n"
        "**High-level design:** URL frontier (the heart: priority queues + per-domain queues "
        "enforcing politeness, e.g. Mercator-style front/back queues); DNS resolver with caching; "
        "fetcher fleet; parser/extractor; dedup (URL-seen store + content fingerprints); link "
        "extractor feeding back into the frontier; storage for page content; robots.txt cache per "
        "domain.\n\n"
        "**Deep dives that matter:** (1) Frontier design: how per-domain back-queues + a heap of "
        "next-allowed-fetch times enforce 1 req/s per domain while thousands of fetchers stay "
        "busy; priority scoring (PageRank-ish importance, change frequency) deciding what enters "
        "front queues. (2) Dedup at scale: URL-seen test with a Bloom filter (memory math: 10B "
        "URLs x few bits) backed by a persistent store; near-duplicate content via SimHash/"
        "shingling rather than exact hashes only.\n\n"
        "**Tradeoffs & scaling:** partitioning the frontier by domain hash across crawler nodes "
        "(keeps politeness state local); trap avoidance (URL normalization, depth limits, per-"
        "domain page budgets); re-crawl scheduling by observed change rate; being a good citizen "
        "(identify via user-agent, exponential backoff on 5xx/429).",
    ),
    (
        "Ticket Booking System",
        1600,
        "Design a ticket-selling system for concerts and sports events (like Ticketmaster).\n\n"
        "**Constraints:** a hot on-sale can bring 500k concurrent users competing for 50k seats in "
        "the first minutes; a seat must never be sold twice; users get 5 minutes to complete "
        "payment after selecting seats; browsing the seat map should feel live; normal load is "
        "tiny by comparison -- the design is all about the spike.",
        "**Requirements a strong answer pins down:** correctness (no double-sell) is non-"
        "negotiable and requires strong consistency on the seat-state transition, even while "
        "browsing can be eventually consistent; the 500k-vs-50k mismatch means most users must be "
        "absorbed *before* the transactional core (queue/waiting room); the 5-minute hold "
        "introduces a reservation state machine: available -> held(expires) -> sold.\n\n"
        "**High-level design:** virtual waiting room / queue that admits users into the purchase "
        "flow at a controlled rate; seat-map service (cached, versioned, WebSocket or polling "
        "updates); reservation service owning seat state in an ACID store; payment integration; "
        "expiry mechanism releasing lapsed holds.\n\n"
        "**Deep dives that matter:** (1) The hold: conditional update ensuring atomicity "
        "(`UPDATE seats SET status='held', hold_expires=... WHERE seat_id=? AND status='available'` "
        "or equivalent conditional put / distributed lock with TTL and fencing), and hold expiry "
        "via TTL + background sweep -- including the race between payment completion and expiry. "
        "(2) The waiting room: token-issued admission at a rate the core can handle, fairness "
        "(randomized or FIFO), and bot mitigation.\n\n"
        "**Tradeoffs & scaling:** why optimistic/conditional writes beat long-held pessimistic "
        "locks at this contention level; keeping the seat map read path cache-served and slightly "
        "stale by design while purchase truth lives in the ACID store; idempotent payment "
        "callbacks; per-event sharding since events are independent.",
    ),
    (
        "Video Streaming Platform",
        1800,
        "Design a video-on-demand streaming platform (like YouTube/Netflix).\n\n"
        "**Constraints:** 100M DAU watching ~1B hours/month; creators upload 500 hours of video "
        "per minute; time-to-first-frame < 1s on a good connection; playback must adapt to "
        "bandwidth from 240p to 4K; a newly uploaded video should be watchable worldwide within "
        "~10 minutes; storage and egress cost matter.",
        "**Requirements a strong answer pins down:** two nearly separate systems -- the upload/"
        "processing pipeline (write path, throughput-bound) and the delivery path (read, latency-"
        "bound); raw video is huge so transcoding into multiple bitrates is mandatory; egress at "
        "this scale means CDN is the delivery backbone, with origin storage behind it.\n\n"
        "**High-level design:** upload service (resumable, chunked, to blob storage); async "
        "transcoding pipeline (split video into segments, transcode each segment in parallel "
        "across workers into a bitrate ladder, package as HLS/DASH manifests + segments); metadata "
        "DB; CDN with origin-pull (plus pre-warm/push for predicted-hot titles); playback API "
        "handing clients a manifest URL.\n\n"
        "**Deep dives that matter:** (1) Adaptive bitrate streaming: segment-based (2-6s) HLS/"
        "DASH, the client measuring throughput and switching rungs per segment -- this is how both "
        "the <1s start (start low, ramp up) and bandwidth adaptation are met. (2) The transcoding "
        "pipeline as a DAG: chunk-level parallelism to make a 2-hour upload ready in ~minutes, "
        "priority lanes, retries on failed chunks, and the ~10-minute availability target driving "
        "the fan-out.\n\n"
        "**Tradeoffs & scaling:** storage tiering & per-title encoding (hot titles get full "
        "ladders, long-tail gets fewer rungs) for cost; CDN cache hit rate as the key economic "
        "metric; view-count and watch-history writes as high-volume async streams; copyright/"
        "content scanning as a pipeline stage (bonus).",
    ),
    (
        "Ride-Sharing Dispatch",
        1900,
        "Design the matching/dispatch core of a ride-sharing service (like Uber).\n\n"
        "**Constraints:** 2M concurrent drivers sending location updates every 4 seconds "
        "(~500k writes/s); rider requests a ride and should be matched to a nearby driver in "
        "< 3 seconds p95; a driver must never be dispatched to two riders at once; surge areas "
        "see 10x request density; location history is kept for 30 days for support/analytics.",
        "**Requirements a strong answer pins down:** the location-update firehose (500k writes/s) "
        "must land in memory, not a relational DB; matching needs an efficient geospatial nearest-"
        "neighbor query, so lat/lon must be indexed by cell (geohash/S2/H3) rather than scanned; "
        "driver state (available/offered/on-trip) is a small strongly-consistent state machine "
        "sitting next to a huge eventually-consistent location layer.\n\n"
        "**High-level design:** driver gateway ingesting location pings -> in-memory geospatial "
        "index sharded by geographic cell (e.g. sorted sets / cell buckets keyed by geohash "
        "prefix); trip/matching service that queries nearby cells, ranks candidates (distance/ETA), "
        "and runs the offer state machine; driver-state store with atomic transitions; async "
        "pipeline (Kafka) archiving pings to cold storage for the 30-day history; notification "
        "path to driver apps.\n\n"
        "**Deep dives that matter:** (1) Geospatial index: geohash/H3 cell mapping, querying the "
        "rider's cell + neighbors (handling cell-boundary cases), cell size tradeoff (too big = "
        "scan too many drivers, too small = many neighbor queries), sharding by region and the "
        "hot-shard problem downtown. (2) Dispatch correctness: offer -> accept flow as atomic "
        "compare-and-swap on driver state with a short TTL offer lock, timeout -> next candidate, "
        "and idempotency so retries can't double-book; sequential offer vs broadcast tradeoff.\n\n"
        "**Tradeoffs & scaling:** in-memory index durability (rebuild from fresh pings in seconds "
        "-- data is self-healing, so replication can be light); surge handled by splitting hot "
        "cells / adding matcher partitions; ETA-based ranking vs straight-line distance; "
        "backpressure -- shedding ping frequency adaptively when overloaded.",
    ),
    (
        "Distributed Key-Value Store",
        2000,
        "Design a distributed key-value store (like DynamoDB/Cassandra) offered as infrastructure "
        "to other teams.\n\n"
        "**Constraints:** 1M ops/s mixed reads/writes; values up to 1 MB; 99.99% availability "
        "including during node failures and rolling deploys; tunable consistency per request "
        "(strong reads must be available as an option); single-key p99 < 10ms; petabyte-scale "
        "total data; no single point of failure.",
        "**Requirements a strong answer pins down:** this is a from-scratch storage-system "
        "question -- the grader expects partitioning, replication, consistency, and failure "
        "handling to each get real treatment; 99.99% availability + no SPOF forces leaderless or "
        "multi-leader thinking (or per-partition leaders with fast failover); 'tunable "
        "consistency' points directly at quorum mechanics.\n\n"
        "**High-level design:** consistent-hash ring (vnodes) partitioning the keyspace; each "
        "partition replicated to N nodes (N=3); coordinator (any node or smart client) routing "
        "requests to replicas; gossip for membership/failure detection; per-node storage engine "
        "(LSM tree: memtable + WAL + SSTables + compaction) for write-heavy performance.\n\n"
        "**Deep dives that matter:** (1) Quorum consistency: N/R/W, R+W>N giving strong reads "
        "(e.g. W=2,R=2,N=3), per-request tunability, and what breaks under partition (CAP: choose "
        "availability with sloppy quorums + hinted handoff, or reject writes for consistency); "
        "conflict handling for concurrent writes -- last-write-wins timestamps vs vector clocks "
        "and their respective lies/costs; read repair + anti-entropy (Merkle trees). (2) Storage "
        "engine: why LSM over B-tree for this write rate, WAL for durability, compaction "
        "strategies and their read/write/space amplification tradeoffs; bloom filters keeping "
        "point reads under the 10ms p99.\n\n"
        "**Tradeoffs & scaling:** failure handling end-to-end (detection via gossip, hinted "
        "handoff during transient failure, replacement + streaming on permanent loss); rebalancing "
        "when nodes join; hot partitions (key salting, adaptive splitting); large 1MB values vs "
        "the LSM (separate blob log is a bonus answer).",
    ),
    (
        "Collaborative Document Editor",
        2100,
        "Design a real-time collaborative document editor (like Google Docs).\n\n"
        "**Constraints:** up to 100 concurrent editors on a single document; edits from one user "
        "visible to others in < 200ms; all replicas must converge to the same document (no lost "
        "edits, ever); offline editing with merge on reconnect; full version history with restore; "
        "documents up to ~1M characters.",
        "**Requirements a strong answer pins down:** naive last-write-wins on the whole document "
        "is disqualifying -- concurrent edits at overlapping positions require a real convergence "
        "mechanism; character positions shift as others type, so raw index-based ops conflict; "
        "the interesting state is per-document and session-oriented (all editors of one doc should "
        "hit the same server for cheap ordering).\n\n"
        "**High-level design:** clients holding a local replica and sending operations (not "
        "snapshots) over WebSocket; a per-document session server that orders/transforms ops and "
        "broadcasts them; document store persisting an op log + periodic snapshots (snapshot + "
        "tail replay for fast load); presence/cursor channel; version-history built from the op "
        "log.\n\n"
        "**Deep dives that matter:** (1) Convergence: Operational Transformation (server transforms "
        "concurrent ops against each other; needs a central sequencer; the classic Docs approach) "
        "vs CRDTs (ops commute by construction -- e.g. unique IDs per character with fractional/"
        "tree positions; no central transform but metadata overhead) -- a strong answer explains "
        "one mechanism concretely (e.g. how insert-at-position gets transformed against a "
        "concurrent insert, or how CRDT character IDs make order deterministic) and states why "
        "they chose it. (2) Offline & history: op-log versioning with client vectors/revision "
        "numbers, replaying+transforming queued offline ops on reconnect (or CRDT merge), "
        "snapshot+log compaction serving both fast loads and time-travel history.\n\n"
        "**Tradeoffs & scaling:** OT's central-server simplicity vs CRDT's decentralization and "
        "memory overhead (tombstones); sticky routing of a doc's editors to one session server and "
        "failover (rebuild from persisted log); 100-editor broadcast fan-out with batching/"
        "debouncing to hold the 200ms target; permissions and share-links as a lighter section.",
    ),
]
