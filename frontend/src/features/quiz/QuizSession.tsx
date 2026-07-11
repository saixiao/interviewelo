import { useCallback, useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { BigTimer } from '../../components/BigTimer'
import { useCountdown } from '../../hooks/useCountdown'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { useStopwatch } from '../../hooks/useStopwatch'
import { quizApi } from './api'
import { QUIZ_CATEGORIES } from './constants'
import type { AnswerSubmission, QueueQuestion, QuizCategory } from './types'

// A "screen" is what's shown to the user at once: one question for the
// trivia categories, or a linked {time, space} pair (same group_id) for
// complexity, so a code snippet is only shown once for both questions.
type Screen = QueueQuestion[]

function chunkIntoScreens(questions: QueueQuestion[]): Screen[] {
  const screens: Screen[] = []
  let i = 0
  while (i < questions.length) {
    const current = questions[i]
    const next = questions[i + 1]
    if (current.group_id && next?.group_id === current.group_id) {
      screens.push([current, next])
      i += 2
    } else {
      screens.push([current])
      i += 1
    }
  }
  return screens
}

export function QuizSession() {
  const { category } = useParams<{ category: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const durationS = Number(searchParams.get('duration') ?? 300)

  const [queue, setQueue] = useState<QueueQuestion[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [screenIndex, setScreenIndex] = useState(0)
  const [selections, setSelections] = useState<Record<string, string[]>>({})
  const answersRef = useRef<AnswerSubmission[]>([])
  const finishedRef = useRef(false)

  useEffect(() => {
    if (!category) return
    quizApi
      .queue(category as QuizCategory, durationS)
      .then((res) => setQueue(res.questions))
      .catch(() => setError('Could not load questions. Is the backend running?'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category])

  const finish = useCallback(
    (elapsedS: number) => {
      if (finishedRef.current || !category) return
      finishedRef.current = true

      quizApi
        .submitAttempt(category as QuizCategory, {
          duration_s: durationS,
          elapsed_s: elapsedS,
          answers: answersRef.current,
        })
        .then((result) => navigate(`/quiz/${category}/results`, { state: { result, queue } }))
        .catch(() => setError('Could not submit your attempt.'))
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [category, durationS, navigate, queue],
  )

  const remainingMs = useCountdown(durationS, () => finish(durationS), true)
  const elapsedMs = useStopwatch()

  useEscapeKey(() => {
    if (window.confirm('Abandon this quiz session? Your progress will be lost.')) navigate('/')
  })

  if (!category || !QUIZ_CATEGORIES.includes(category as QuizCategory)) {
    return <Navigate to="/" replace />
  }

  if (error) {
    return <div className="flex h-screen items-center justify-center text-red-400">{error}</div>
  }

  if (!queue) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">Loading...</div>
  }

  const screens = chunkIntoScreens(queue)

  function toggleKey(question: QueueQuestion, key: string) {
    setSelections((prev) => {
      const current = prev[question.id] ?? []
      if (question.multi_select) {
        const next = current.includes(key) ? current.filter((k) => k !== key) : [...current, key]
        return { ...prev, [question.id]: next }
      }
      return { ...prev, [question.id]: [key] }
    })
  }

  function handleNext() {
    for (const q of screens[screenIndex]) {
      answersRef.current.push({ question_id: q.id, selected_keys: selections[q.id] ?? [] })
    }
    if (screenIndex + 1 >= screens.length) {
      finish(Math.max(1, Math.round(elapsedMs / 1000)))
    } else {
      setScreenIndex((i) => i + 1)
    }
  }

  if (screenIndex >= screens.length) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-6 px-6 text-center">
        <BigTimer remainingMs={remainingMs} lowWarning />
        <p className="text-neutral-400">You've answered every question available right now.</p>
        <button
          onClick={() => finish(Math.max(1, Math.round(elapsedMs / 1000)))}
          className="rounded-md bg-violet-600 px-6 py-2 font-medium transition hover:bg-violet-500"
        >
          Finish session
        </button>
      </div>
    )
  }

  const screen = screens[screenIndex]
  const canAdvance = screen.every((q) => (selections[q.id] ?? []).length > 0)

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-8 overflow-y-auto px-6 py-10">
      <BigTimer remainingMs={remainingMs} lowWarning />

      <div className="w-full max-w-2xl space-y-6">
        {screen.map((q) => (
          <QuestionBlock key={q.id} question={q} selected={selections[q.id] ?? []} onToggle={(key) => toggleKey(q, key)} />
        ))}
      </div>

      <button
        onClick={handleNext}
        disabled={!canAdvance}
        className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500 disabled:opacity-40"
      >
        {screenIndex + 1 >= screens.length ? 'Finish' : 'Next'}
      </button>
    </div>
  )
}

function QuestionBlock({
  question,
  selected,
  onToggle,
}: {
  question: QueueQuestion
  selected: string[]
  onToggle: (key: string) => void
}) {
  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
      <p className="whitespace-pre-wrap text-lg">{question.prompt_md}</p>
      {question.code_snippet && (
        <pre className="mt-3 overflow-x-auto rounded-md bg-neutral-950 p-4 font-mono text-sm text-neutral-200">
          {question.code_snippet}
        </pre>
      )}
      <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {question.choices.map((c) => (
          <button
            key={c.key}
            onClick={() => onToggle(c.key)}
            className={`rounded-md border px-4 py-2.5 text-left text-sm transition ${
              selected.includes(c.key)
                ? 'border-violet-500 bg-violet-950/40 text-white'
                : 'border-neutral-800 bg-neutral-950 text-neutral-300 hover:border-neutral-700'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>
    </div>
  )
}
