# InterviewElo — Implementation Plan

## Context

The user wants to gamify their own coding-interview prep, in the spirit of Human Benchmark: short, snappy, game-like practice sessions with a big satisfying score reveal at the end. The repo is currently empty aside from a one-line README, so this is a from-scratch build. The work is broken into **independently-shippable phases** implemented one at a time, rather than one big build.

Three practice modes, each producing a score that feeds one unified Elo rating (0–3000) across ten named tiers (Noob → Intern → Entry Level → Mid Level → Senior → Staff → Sr. Staff → Principal → Fellow → AGI), so the user can track day-over-day progression toward being interview-ready.

An LC-style coding round with sandboxed Python execution was considered (see git history for the scrapped Phase 2 plan) and explicitly dropped from scope — the app covers typing, the quick-fire approach round, and system design only.

Confirmed tech decisions:
- **Frontend**: React SPA (Vite + TypeScript), deployed to Vercel.
- **Backend**: Python/FastAPI, hosting the API plus Claude-based LLM grading for the approach and design rounds.
- **Auth**: full multi-user auth from day one (real signup/login, not a single-user shim).
- **LLM judging**: Anthropic API (Claude), used to grade the free-text "approach" round and the system-design round.
- **Deployment**: cloud-hosted — Vercel doesn't suit a long-lived FastAPI process or multi-second LLM calls, so the backend needs a dedicated host (Fly.io recommended, Render/Railway as alternatives) plus managed Postgres (Neon recommended).

## Architecture Overview

```
interviewelo/
├── frontend/          # Vite + React + TypeScript SPA (Vercel)
│   └── src/
│       ├── api/       # typed fetch client, auth token handling
│       ├── features/  # typing/, approach/, design/, dashboard/, auth/
│       └── components/# shared UI: SessionShell, BigTimer, ResultsReveal, EloBadge
├── backend/           # FastAPI (Fly.io/Render)
│   └── app/
│       ├── main.py, config.py, db.py, models.py
│       ├── auth/      # signup/login, JWT, password hashing
│       ├── elo/       # tiers, expected-score math, apply_session_result()
│       ├── typing/    # snippets + attempts
│       ├── approach/  # quick-fire sessions + Claude grading
│       ├── design/    # design sessions + Claude grading/follow-ups
│       └── llm/       # single Anthropic client wrapper + graders
└── alembic/, docker-compose.yml (local Postgres for dev)
```

**Cross-cutting decisions**
- **Auth**: email + password (bcrypt via `passlib`), short-lived JWT access token + httpOnly refresh cookie. Every table keys on `user_id`.
- **DB**: Postgres + SQLAlchemy 2.0 + Alembic migrations. JSONB for flexible payloads (keystroke logs, LLM grade breakdowns) so early schema churn stays cheap.
- **LLM judging**: Anthropic Python SDK, `messages.parse()` with Pydantic output models so grades come back as validated JSON; `cache_control` on the static rubric system prompt since grading calls reuse the same rubric text repeatedly.
- **Scores are normalized to S ∈ [0, 1] per session** in every mode, then fed through one shared Elo function — keeps the Elo engine mode-agnostic and lets each phase ship independently.

## Elo System (built as a shell in Phase 0, wired into each mode as it ships)

### Tiers — 300-point bands across 0–3000

| Tier | Range | Tier | Range |
|---|---|---|---|
| Noob | 0–299 | Staff | 1500–1799 |
| Intern | 300–599 | Sr. Staff | 1800–2099 |
| Entry Level | 600–899 | Principal | 2100–2399 |
| Mid Level | 900–1199 | Fellow | 2400–2699 |
| Senior | 1200–1499 | AGI | 2700–3000 |

New users start at **500 (Intern)** in each category.

### Rating update — PvE Elo against content difficulty

Each session produces a normalized score **S ∈ [0, 1]** and the content it was attempted on has a **difficulty rating D** (each approach/design prompt is authored with a difficulty rating; typing packs get D from length/symbol density). Standard expected-outcome math:

```
E = 1 / (1 + 10^((D − R) / 400))     # expected score at current rating R
ΔR = K × (S − E)                      # K = 40 for first 10 sessions (placement), then 24
R' = clamp(R + ΔR, 0, 3000)
```

Acing easy content once you're already Senior gains almost nothing; scoring well on hard content while Entry Level gains a lot; bombing content below your level costs you. Daily practice converges rather than inflates.

**Per-mode S:**
- **Typing**: `net_wpm = wpm × accuracy²`; S = piecewise-linear map (0 at ≤20 net WPM → 1.0 at ≥90 net WPM).
- **Approach round**: Claude grades each answer 0–100 on a 4-part rubric; S = session average / 100.
- **System design**: Claude grades the full transcript 0–100 on the prompt's rubric; S = score / 100.

**Overall Elo** = mean of the three category ratings (an unplayed category counts at the 500 floor, so the overall number is meaningful from day one and playing all three modes is incentivized). Every update writes an `elo_history` row for charting.

## Core Data Model

```
users            (id, email, password_hash, display_name, created_at)
user_ratings     (user_id, category ∈ {typing,approach,design}, rating, sessions_count)
elo_history      (id, user_id, category, rating_before, rating_after, delta,
                  source_type, source_id, created_at)

typing_snippets  (id, language, difficulty, content, char_count, symbol_density)
typing_attempts  (id, user_id, duration_s ∈ {60,300}, wpm, raw_wpm, accuracy,
                  keystroke_log JSONB, score, elo_delta, created_at)

approach_prompts (id, difficulty, prompt_md, grading_notes_md)
approach_sessions(id, user_id, started_at, duration_s, overall_score, grade_summary JSONB, elo_delta)
approach_answers (id, session_id, prompt_id, answer_text, grade JSONB, created_at)

design_prompts   (id, difficulty, prompt_md, rubric_md)
design_sessions  (id, user_id, prompt_id, transcript JSONB[{role,text,ts}],
                  grade JSONB, overall_score, elo_delta, status, created_at)
```

## Phase 0 — Scaffolding, Auth, Elo Shell

Two deployable apps, real accounts, a tested Elo engine — no game modes yet.

- Repo layout as above; `docker-compose.yml` for local Postgres; Alembic wired up.
- Backend: FastAPI app factory, CORS for the Vercel origin, `/health`; `POST /auth/signup`, `POST /auth/login`, `POST /auth/refresh`, `GET /me` (ratings + tier per category + overall).
- Elo module (`backend/app/elo/engine.py`): pure functions — `tier_for(rating)`, `expected_score(R, D)`, `apply_session_result(user, category, S, D)` updating `user_ratings` + appending `elo_history` in one transaction. Unit-test this thoroughly now; every later phase just calls it.
- Frontend: Vite + React Router + Tailwind; auth pages; app shell with three mode tiles (Human-Benchmark-style grid, greyed out until their phase ships); Elo badge in the header.
- Deploy both ends now so every later phase is a deploy, not a migration.

## Phase 1 — Typing Racer (first playable feature)

Self-contained: no LLM — validates session flow, scoring, Elo, and the results-reveal UX end to end.

- Snippet bank: `typing_snippets` seeded from a checked-in `seeds/snippets/` folder of real Python idioms (comprehensions, dunder methods, decorators, slicing) chosen for symbol density (`->`, `[]`, `{}`, `==`, `_`). ~40–60 snippets to start.
- Session mechanics (client-side): pick 1-min or 5-min → backend returns a shuffled snippet queue → full-screen typing surface with live per-character diffing (pending/correct/incorrect/cursor states, TypeRacer-style), preserved indentation, **Tab inserts real indentation**. Keystrokes tracked in a `useTypingSession` reducer; WPM/accuracy computed client-side for live feedback.
- `POST /typing/attempts` submits summary + keystroke log; **server recomputes WPM/accuracy from the log** (don't trust client numbers), computes S, calls the Elo engine, returns `elo_delta`.
- Results reveal: full-screen takeover, huge net-WPM number counts up, accuracy beneath, Elo delta animates in with tier badge. This `ResultsReveal` component is built generically here and reused by every later mode.

## Phase 2 — Quick-Fire Approach Round + Claude Grading

First LLM integration; establishes the `llm/` grading pattern Phase 3 reuses.

- `POST /approach/sessions` starts a 10-minute session; frontend shows one prompt at a time with a plain textarea ("explain your approach out loud"), Next/Skip advances through as many as fit; answers saved incrementally so a refresh loses nothing; timeout triggers grading.
- Grading (`backend/app/llm/grader.py`): one `messages.parse()` call for the whole session with a Pydantic output model: per-answer `{approach_correctness, complexity_awareness, edge_case_awareness, communication: 0..100, feedback}` + session summary. Static rubric gets `cache_control`. S = mean/100 → Elo engine.
- Results: total score reveal, then expandable per-question cards with your answer + Claude's dimension scores and feedback — this is the actual learning payload.
- Seed ~30 `approach_prompts`, each with `grading_notes_md` (the intended optimal approach) so the judge grades against ground truth rather than its own guess.

## Phase 3 — System Design Round + Claude Follow-ups

- Pick/get-random prompt ("Design a URL shortener") → 10-minute session → user writes design in a large textarea → mid-session "Get follow-up" (plus one auto-triggered around 5 min) sends the transcript to Claude for one probing interviewer question; user answers inline. Transcript stored as alternating `{role: user|interviewer}` JSONB entries.
- Grading at timeout: full transcript → `messages.parse()` against the prompt's `rubric_md` → `{requirements, high_level_design, deep_dives, tradeoffs_and_scaling: 0..100, strengths[], improvements[], overall}`. S = overall/100 → Elo.
- Same Anthropic client wrapper as Phase 2, so prompt-engineering iterations live in one place. Seed 10–15 design prompts each with a tailored rubric.
- Frontend reuses SessionShell/BigTimer/ResultsReveal; new pieces are the transcript view and follow-up bubbles.

## Phase 4 — Dashboard, Progression, Polish

- `GET /stats/elo-history?category=&range=` and `GET /stats/summary` (per-category rating/tier/session counts, streak computed from `elo_history` dates, best-session records).
- Dashboard: overall Elo hero number + tier badge + progress bar to next tier; Elo-over-time line chart (Recharts) with category toggle; per-category tiles; streak counter; recent-sessions feed with deltas.
- Polish: tier-up celebration animation, daily-practice prompt on the home screen ("Today: 1 typing sprint, 1 quick-fire, 1 design session"), settings page, mobile-usable typing fallback.
- Backlog (not in scope now): leaderboards, spaced repetition of weak prompts/snippets, Elo decay.

## Human-Benchmark-Style UI Pattern (shared across all modes)

Every mode follows the same three-beat loop, built once as shared components:
1. **Pre-session**: minimal card — mode name, one-line description, duration picker, single giant "Start" button.
2. **In-session**: full-screen takeover, nav hidden, one big centered timer and exactly one interactive surface. Escape = abandon (confirm).
3. **Results reveal**: screen wipes to one enormous animated number (net WPM / grade), sub-stats fade in, then Elo delta slides in with tier badge (tier-up burst when crossed), then "Go again" / "Details" buttons.

## Deployment

- **Frontend**: Vercel (static SPA build; `VITE_API_URL` env).
- **Backend**: Fly.io (recommended) or Render/Railway as simpler alternatives. Dockerfile-based deploy, Alembic migrations on release.
- **Postgres**: Neon (free tier, branching) or the host's managed Postgres.
- **Secrets**: `DATABASE_URL`, `JWT_SECRET`, `ANTHROPIC_API_KEY` (backend only — never the frontend).

## Risks

- **LLM grade inconsistency** → ground-truth `grading_notes_md`/rubrics per prompt, structured outputs; Elo's K-factor smooths residual noise.
- **Elo tuning feel** → all constants (K, difficulty ratings D, WPM curve) centralized in `elo/constants.py`; expect to retune after real use — `elo_history` allows replay/recompute if the formula changes.
- **Typing cheat-ability** → server-side recompute from keystroke logs.

## Critical Files

- `backend/app/elo/engine.py` — tier thresholds, expected-score math, `apply_session_result()`; every mode depends on it.
- `backend/app/llm/grader.py` — Anthropic client wrapper + structured-output graders for approach and design rounds.
- `frontend/src/components/ResultsReveal.tsx` — the shared big-number reveal that defines the game feel across all modes.
- `backend/app/models.py` — SQLAlchemy models for the full schema.

## Verification (per phase)

- Phase 0: `curl` signup/login/me against local FastAPI; run Elo engine unit tests directly.
- Phase 1: run a full 1-min typing session in the browser, confirm WPM/accuracy match a manual count, confirm Elo updates in `/me`.
- Phase 2/3: run a real 10-minute session, confirm Claude's structured grade parses without validation errors and Elo updates sensibly.
- Phase 4: confirm dashboard charts reflect real `elo_history` rows across all three categories.
