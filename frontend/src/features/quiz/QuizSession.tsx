import { useCallback, useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { BigTimer } from '../../components/BigTimer'
import { useCountdown } from '../../hooks/useCountdown'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { useStopwatch } from '../../hooks/useStopwatch'
import { quizApi } from './api'
import { QUIZ_CATEGORIES } from './constants'
import type { AnswerSubmission, QueueQuestion, QuizCategory, RevealResponse } from './types'

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
  // Per-question "show correct answer" reveal, fetched from a lightweight
  // non-persisting endpoint (POST /quiz/questions/:id/reveal) -- keeps the
  // queue itself free of correct_keys/explanation_md and never touches the
  // official answer list in answersRef, which is still assembled
  // client-side and submitted once at the end exactly as before.
  const [revealResults, setRevealResults] = useState<Record<string, RevealResponse>>({})
  const [checking, setChecking] = useState(false)
  const [checkError, setCheckError] = useState<string | null>(null)
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

  useEscapeKey(
    useCallback(() => {
      // Guard against the same race the other three session shells guard
      // against: once finish() has fired (auto-submit at timeout, or the
      // last screen's Finish button), a submitAttempt request is already in
      // flight and will navigate to /results itself when it resolves. If
      // Escape were still live here, confirming "Abandon" would navigate
      // home immediately, only for that stale in-flight `.then` to yank the
      // user back to /results moments later -- so once finished, Escape is
      // a no-op, matching Approach's pattern.
      if (finishedRef.current) return
      if (window.confirm('Abandon this quiz session? Your progress will be lost.')) navigate('/')
    }, [navigate]),
  )

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

  // Fetch the reveal for every not-yet-revealed question on the current
  // screen (a single question for python_trivia, or the linked time+space
  // pair for complexity) and show it before Next is enabled. This never
  // touches answersRef -- the real submission still happens once at the end
  // via handleNext/finish, unchanged.
  function checkAnswer(screenQuestions: QueueQuestion[]) {
    const toCheck = screenQuestions.filter((q) => !revealResults[q.id])
    if (checking || toCheck.length === 0) return
    setChecking(true)
    setCheckError(null)
    Promise.all(
      toCheck.map((q) => quizApi.reveal(q.id, selections[q.id] ?? []).then((res) => [q.id, res] as const)),
    )
      .then((pairs) => {
        setRevealResults((prev) => {
          const next = { ...prev }
          for (const [id, res] of pairs) next[id] = res
          return next
        })
      })
      .catch(() => setCheckError('Could not check that answer. Please try again.'))
      .finally(() => setChecking(false))
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
  const hasSelections = screen.every((q) => (selections[q.id] ?? []).length > 0)
  const allRevealed = screen.every((q) => Boolean(revealResults[q.id]))
  const canAdvance = allRevealed

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-8 overflow-y-auto px-6 py-10">
      <BigTimer remainingMs={remainingMs} lowWarning />

      <div className="w-full max-w-2xl space-y-6">
        {screen.map((q) => (
          <QuestionBlock
            key={q.id}
            question={q}
            selected={selections[q.id] ?? []}
            onToggle={(key) => toggleKey(q, key)}
            reveal={revealResults[q.id]}
          />
        ))}
        {checkError && <p className="text-sm text-red-400">{checkError}</p>}
      </div>

      {!allRevealed ? (
        <button
          onClick={() => checkAnswer(screen)}
          disabled={!hasSelections || checking}
          className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500 disabled:opacity-40"
        >
          {checking ? 'Checking...' : 'Check answer'}
        </button>
      ) : (
        <button
          onClick={handleNext}
          disabled={!canAdvance}
          className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500 disabled:opacity-40"
        >
          {screenIndex + 1 >= screens.length ? 'Finish' : 'Next'}
        </button>
      )}
    </div>
  )
}

function QuestionBlock({
  question,
  selected,
  onToggle,
  reveal,
}: {
  question: QueueQuestion
  selected: string[]
  onToggle: (key: string) => void
  reveal?: RevealResponse
}) {
  const locked = Boolean(reveal)

  function choiceClasses(key: string) {
    if (reveal) {
      const isCorrectKey = reveal.correct_keys.includes(key)
      const isSelected = selected.includes(key)
      if (isCorrectKey) return 'border-green-500 bg-green-950/40 text-white'
      if (isSelected) return 'border-red-500 bg-red-950/40 text-white'
      return 'border-neutral-800 bg-neutral-950 text-neutral-500'
    }
    return selected.includes(key)
      ? 'border-violet-500 bg-violet-950/40 text-white'
      : 'border-neutral-800 bg-neutral-950 text-neutral-300 hover:border-neutral-700'
  }

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
            onClick={() => !locked && onToggle(c.key)}
            disabled={locked}
            className={`rounded-md border px-4 py-2.5 text-left text-sm transition disabled:cursor-default ${choiceClasses(c.key)}`}
          >
            {c.label}
          </button>
        ))}
      </div>
      {reveal && (
        <div
          className={`mt-4 rounded-md border p-3 text-sm ${
            reveal.correct ? 'border-green-800 bg-green-950/30 text-green-200' : 'border-red-800 bg-red-950/30 text-red-200'
          }`}
        >
          <p className="mb-1 font-semibold">{reveal.correct ? 'Correct!' : 'Not quite.'}</p>
          <p className="whitespace-pre-wrap text-neutral-300">{reveal.explanation_md}</p>
        </div>
      )}
    </div>
  )
}
