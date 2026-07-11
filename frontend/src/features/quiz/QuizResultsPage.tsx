import { useState } from 'react'
import { Navigate, useLocation, useNavigate, useParams } from 'react-router-dom'
import { QUIZ_CATEGORY_META } from './constants'
import type { AnswerResult, QueueQuestion, QuizAttemptResponse } from './types'

interface LocationState {
  result?: QuizAttemptResponse
  queue?: QueueQuestion[]
}

export function QuizResultsPage() {
  const { category } = useParams<{ category: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null

  if (!category) return <Navigate to="/" replace />
  if (!state?.result) return <Navigate to={`/quiz/${category}`} replace />

  const { result, queue = [] } = state
  const questionsById = new Map(queue.map((q) => [q.id, q]))
  const tieredUp = result.tier_before !== result.tier_after
  const deltaLabel = result.delta > 0 ? `+${result.delta}` : `${result.delta}`
  const deltaColor = result.delta > 0 ? 'text-emerald-400' : result.delta < 0 ? 'text-red-400' : 'text-neutral-400'
  const correctCount = result.results.filter((r) => r.correct).length

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <div className="flex flex-col items-center gap-6 text-center">
        <p className="text-sm uppercase tracking-wide text-neutral-500">
          {QUIZ_CATEGORY_META[result.category]?.title ?? result.category}
        </p>
        <p className="text-7xl font-bold tabular-nums">{Math.round(result.overall_score * 100)}%</p>
        <p className="text-sm text-neutral-400">
          {correctCount} / {result.results.length} correct
        </p>

        <div className="flex items-center gap-3 rounded-full border border-neutral-800 bg-neutral-900 px-5 py-2">
          <span className="text-sm text-neutral-400">{result.tier_after}</span>
          <span className="text-lg font-semibold tabular-nums">{result.rating_after}</span>
          <span className={`text-sm font-medium tabular-nums ${deltaColor}`}>{deltaLabel}</span>
          {tieredUp && <span className="text-sm font-medium text-violet-400">Tier up!</span>}
        </div>
      </div>

      <div className="mt-12 flex flex-col gap-3">
        {result.results.map((r, i) => (
          <ReviewCard key={`${r.question_id}-${i}`} index={i + 1} result={r} question={questionsById.get(r.question_id)} />
        ))}
      </div>

      <div className="mt-10 flex justify-center gap-3">
        <button
          onClick={() => navigate(`/quiz/${category}`)}
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

function ReviewCard({
  index,
  result,
  question,
}: {
  index: number
  result: AnswerResult
  question?: QueueQuestion
}) {
  const [expanded, setExpanded] = useState(false)
  const choiceLabel = (key: string) => question?.choices.find((c) => c.key === key)?.label ?? key

  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <div>
          <p className="text-xs uppercase tracking-wide text-neutral-500">Question {index}</p>
          <p className="whitespace-pre-wrap font-medium">{question?.prompt_md ?? '...'}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-semibold ${result.correct ? 'text-emerald-400' : 'text-red-400'}`}>
            {result.correct ? 'Correct' : 'Incorrect'}
          </span>
          <span className="text-neutral-500">{expanded ? '−' : '+'}</span>
        </div>
      </button>

      {expanded && (
        <div className="space-y-4 border-t border-neutral-800 px-5 py-4">
          {question?.code_snippet && (
            <pre className="overflow-x-auto rounded-md bg-neutral-950 p-4 font-mono text-sm text-neutral-200">
              {question.code_snippet}
            </pre>
          )}

          <div>
            <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Your answer</p>
            <p className="text-sm text-neutral-300">
              {result.selected_keys.map(choiceLabel).join(', ') || '(no answer submitted)'}
            </p>
          </div>

          {!result.correct && (
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Correct answer</p>
              <p className="text-sm text-emerald-400">{result.correct_keys.map(choiceLabel).join(', ')}</p>
            </div>
          )}

          <div>
            <p className="mb-1 text-xs uppercase tracking-wide text-neutral-500">Why</p>
            <p className="text-sm text-neutral-300">{result.explanation_md}</p>
          </div>
        </div>
      )}
    </div>
  )
}
