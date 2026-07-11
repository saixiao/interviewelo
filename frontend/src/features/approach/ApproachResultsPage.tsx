import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { RubricLegend } from './RubricScale'
import type { AnswerGradeResult, ApproachAttemptResponse } from './types'

interface LocationState {
  result?: ApproachAttemptResponse
  infiniteResults?: AnswerGradeResult[]
}

export function ApproachResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  const onPlayAgain = () => navigate('/approach')
  const onHome = () => navigate('/')

  if (state?.result) {
    return <QuickFireResults result={state.result} onPlayAgain={onPlayAgain} onHome={onHome} />
  }

  if (state?.infiniteResults && state.infiniteResults.length > 0) {
    return <InfiniteResults results={state.infiniteResults} onPlayAgain={onPlayAgain} onHome={onHome} />
  }

  return <Navigate to="/approach" replace />
}

interface ResultsActionsProps {
  onPlayAgain: () => void
  onHome: () => void
}

function QuickFireResults({ result, onPlayAgain, onHome }: { result: ApproachAttemptResponse } & ResultsActionsProps) {
  const tieredUp = result.tier_before !== result.tier_after
  const deltaLabel = result.delta > 0 ? `+${result.delta}` : `${result.delta}`
  const deltaColor = result.delta > 0 ? 'text-emerald-400' : result.delta < 0 ? 'text-red-400' : 'text-neutral-400'

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <div className="flex flex-col items-center gap-6 text-center">
        <p className="text-sm uppercase tracking-wide text-neutral-500">Overall Score</p>
        <p className="text-7xl font-bold tabular-nums">{Math.round(result.score * 100)}%</p>

        <div className="flex items-center gap-3 rounded-full border border-neutral-800 bg-neutral-900 px-5 py-2">
          <span className="text-sm text-neutral-400">{result.tier_after}</span>
          <span className="text-lg font-semibold tabular-nums">{result.rating_after}</span>
          <span className={`text-sm font-medium tabular-nums ${deltaColor}`}>{deltaLabel}</span>
          {tieredUp && <span className="text-sm font-medium text-violet-400">Tier up!</span>}
        </div>

        <p className="max-w-lg text-sm text-neutral-400">{result.session_summary}</p>

        <RubricLegend />
      </div>

      <QuestionList results={result.results} />
      <ResultsActionButtons onPlayAgain={onPlayAgain} onHome={onHome} />
    </div>
  )
}

function InfiniteResults({
  results,
  onPlayAgain,
  onHome,
}: { results: AnswerGradeResult[] } & ResultsActionsProps) {
  const average = Math.round(results.reduce((sum, r) => sum + questionAverage(r), 0) / results.length)

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <div className="flex flex-col items-center gap-6 text-center">
        <p className="text-sm uppercase tracking-wide text-neutral-500">Session Complete</p>
        <p className="text-7xl font-bold tabular-nums">{average}</p>
        <p className="text-sm text-neutral-400">
          {results.length} question{results.length === 1 ? '' : 's'} &middot; average score across all dimensions
        </p>
        <p className="text-xs text-neutral-600">Infinite mode practice sessions don't affect your Elo rating.</p>

        <RubricLegend />
      </div>

      <QuestionList results={results} />
      <ResultsActionButtons onPlayAgain={onPlayAgain} onHome={onHome} />
    </div>
  )
}

function ResultsActionButtons({ onPlayAgain, onHome }: ResultsActionsProps) {
  return (
    <div className="mt-10 flex justify-center gap-3">
      <button
        onClick={onPlayAgain}
        className="rounded-md bg-violet-600 px-6 py-2 font-medium transition hover:bg-violet-500"
      >
        Go again
      </button>
      <button
        onClick={onHome}
        className="rounded-md border border-neutral-800 px-6 py-2 font-medium text-neutral-300 transition hover:bg-neutral-900"
      >
        Home
      </button>
    </div>
  )
}

function QuestionList({ results }: { results: AnswerGradeResult[] }) {
  return (
    <div className="mt-12 flex flex-col gap-3">
      {results.map((r, i) => (
        <QuestionCard key={`${r.prompt_id}-${i}`} index={i + 1} result={r} />
      ))}
    </div>
  )
}

function questionAverage(r: AnswerGradeResult): number {
  return Math.round(
    (r.approach_correctness + r.complexity_awareness + r.edge_case_awareness + r.communication) / 4,
  )
}

function QuestionCard({ index, result }: { index: number; result: AnswerGradeResult }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <div>
          <p className="text-xs uppercase tracking-wide text-neutral-500">Question {index}</p>
          <p className="font-medium">{result.title}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-lg font-semibold tabular-nums">{questionAverage(result)}</span>
          <span className="text-neutral-500">{expanded ? '−' : '+'}</span>
        </div>
      </button>

      {expanded && (
        <div className="space-y-4 border-t border-neutral-800 px-5 py-4">
          <div>
            <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Prompt</p>
            <p className="text-sm text-neutral-300">{result.prompt_md}</p>
          </div>

          <div>
            <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Your answer</p>
            <p className="whitespace-pre-wrap text-sm text-neutral-300">
              {result.answer_text || <span className="text-neutral-600">(no answer submitted)</span>}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <DimensionScore label="Correctness" value={result.approach_correctness} />
            <DimensionScore label="Complexity" value={result.complexity_awareness} />
            <DimensionScore label="Edge cases" value={result.edge_case_awareness} />
            <DimensionScore label="Communication" value={result.communication} />
          </div>

          <div>
            <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Feedback</p>
            <p className="text-sm text-neutral-300">{result.feedback}</p>
          </div>
        </div>
      )}
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
