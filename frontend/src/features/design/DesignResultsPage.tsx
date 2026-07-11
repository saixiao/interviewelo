import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { DesignRubricLegend } from './RubricScale'
import type { DesignFinishResponse, TranscriptEntry } from './types'

interface LocationState {
  result?: DesignFinishResponse
}

export function DesignResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  if (!state?.result) {
    return <Navigate to="/design" replace />
  }
  const result = state.result

  const tieredUp = result.tier_before !== result.tier_after
  const deltaLabel = result.delta > 0 ? `+${result.delta}` : `${result.delta}`
  const deltaColor = result.delta > 0 ? 'text-emerald-400' : result.delta < 0 ? 'text-red-400' : 'text-neutral-400'

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <div className="flex flex-col items-center gap-6 text-center">
        <p className="text-sm uppercase tracking-wide text-neutral-500">{result.prompt_title}</p>
        <p className="text-7xl font-bold tabular-nums">{result.grade.overall}</p>
        <p className="text-sm text-neutral-500">overall / 100</p>

        <div className="flex items-center gap-3 rounded-full border border-neutral-800 bg-neutral-900 px-5 py-2">
          <span className="text-sm text-neutral-400">{result.tier_after}</span>
          <span className="text-lg font-semibold tabular-nums">{result.rating_after}</span>
          <span className={`text-sm font-medium tabular-nums ${deltaColor}`}>{deltaLabel}</span>
          {tieredUp && <span className="text-sm font-medium text-violet-400">Tier up!</span>}
        </div>

        <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4">
          <DimensionScore label="Requirements" value={result.grade.requirements} />
          <DimensionScore label="High-level" value={result.grade.high_level_design} />
          <DimensionScore label="Deep dives" value={result.grade.deep_dives} />
          <DimensionScore label="Tradeoffs" value={result.grade.tradeoffs_and_scaling} />
        </div>

        <DesignRubricLegend />
      </div>

      {/* The debrief payload: what you missed comes first, and loudest. */}
      <section className="mt-12 rounded-2xl border border-amber-800/50 bg-amber-950/20 p-5">
        <h2 className="mb-3 text-lg font-semibold text-amber-300">What you missed</h2>
        {result.grade.improvements.length === 0 ? (
          <p className="text-sm text-neutral-400">Nothing major -- a very complete design.</p>
        ) : (
          <ul className="space-y-2">
            {result.grade.improvements.map((item, i) => (
              <li key={i} className="flex gap-3 text-sm leading-relaxed text-neutral-200">
                <span className="mt-0.5 shrink-0 font-semibold tabular-nums text-amber-400">{i + 1}.</span>
                {item}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-4 rounded-2xl border border-emerald-900/50 bg-emerald-950/20 p-5">
        <h2 className="mb-3 text-lg font-semibold text-emerald-300">What you did well</h2>
        {result.grade.strengths.length === 0 ? (
          <p className="text-sm text-neutral-400">The grader didn't find much to praise this time.</p>
        ) : (
          <ul className="space-y-2">
            {result.grade.strengths.map((item, i) => (
              <li key={i} className="flex gap-3 text-sm leading-relaxed text-neutral-200">
                <span className="mt-0.5 shrink-0 text-emerald-400">✓</span>
                {item}
              </li>
            ))}
          </ul>
        )}
      </section>

      <TranscriptReview transcript={result.transcript} />

      <div className="mt-10 flex justify-center gap-3">
        <button
          onClick={() => navigate('/design')}
          className="rounded-md bg-violet-600 px-6 py-2 font-medium transition hover:bg-violet-500"
        >
          Go again
        </button>
        <button
          onClick={() => navigate('/')}
          className="rounded-md border border-neutral-800 px-6 py-2 font-medium text-neutral-300 transition hover:bg-neutral-900"
        >
          Home
        </button>
      </div>
    </div>
  )
}

function DimensionScore({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-neutral-950 px-3 py-2 text-center">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  )
}

function TranscriptReview({ transcript }: { transcript: TranscriptEntry[] }) {
  const [expanded, setExpanded] = useState(false)

  if (transcript.length === 0) return null

  return (
    <div className="mt-4 rounded-2xl border border-neutral-800 bg-neutral-900">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <p className="font-medium">
          Session transcript{' '}
          <span className="text-sm font-normal text-neutral-500">({transcript.length} turns)</span>
        </p>
        <span className="text-neutral-500">{expanded ? '−' : '+'}</span>
      </button>
      {expanded && (
        <div className="space-y-4 border-t border-neutral-800 px-5 py-4">
          {transcript.map((entry, i) => (
            <div key={`${entry.ts}-${i}`}>
              <p
                className={`mb-1 text-xs font-medium uppercase tracking-wide ${
                  entry.role === 'interviewer' ? 'text-violet-400' : 'text-neutral-500'
                }`}
              >
                {entry.role === 'interviewer' ? 'Interviewer' : 'You'}
              </p>
              <p className="whitespace-pre-wrap text-sm text-neutral-300">{entry.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
