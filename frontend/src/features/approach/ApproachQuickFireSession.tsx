import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { approachApi } from './api'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { useStopwatch } from '../../hooks/useStopwatch'
import type { AnswerSubmission, ApproachAttemptResponse, QueuePrompt } from './types'
import { BigTimer } from '../../components/BigTimer'
import { RubricLegend } from './RubricScale'

interface ApproachQuickFireSessionProps {
  onFinish: (result: ApproachAttemptResponse) => void
}

export function ApproachQuickFireSession({ onFinish }: ApproachQuickFireSessionProps) {
  const navigate = useNavigate()
  const [queue, setQueue] = useState<QueuePrompt[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const finishedRef = useRef(false)
  const elapsedMs = useStopwatch()

  useEscapeKey(
    useCallback(() => {
      if (finishedRef.current) return
      if (window.confirm('Abandon this session? Your answers will be lost.')) {
        finishedRef.current = true
        navigate('/approach')
      }
    }, [navigate]),
  )

  useEffect(() => {
    approachApi
      .queue()
      .then((res) => setQueue(res.items))
      .catch(() => setError('Could not load prompts. Is the backend running?'))
  }, [])

  useEffect(() => {
    textareaRef.current?.focus()
  }, [index])

  const submit = useCallback(
    (finalAnswers: Record<string, string>) => {
      if (finishedRef.current || !queue) return
      finishedRef.current = true
      setSubmitting(true)

      const items: AnswerSubmission[] = queue.map((q) => ({
        prompt_id: q.prompt_id,
        answer_text: finalAnswers[q.prompt_id] ?? '',
      }))

      approachApi
        .submitAttempt({ elapsed_s: Math.max(1, Math.round(elapsedMs / 1000)), items })
        .then(onFinish)
        .catch(() => {
          finishedRef.current = false
          setSubmitting(false)
          setError('Could not grade your session. Please try again.')
        })
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [queue, elapsedMs],
  )

  if (error) {
    return <div className="flex h-screen items-center justify-center px-6 text-center text-red-400">{error}</div>
  }

  if (!queue) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">Loading...</div>
  }

  if (submitting) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 text-neutral-500">
        <p>Grading your approach...</p>
        <div className="flex items-center gap-2 text-neutral-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-violet-500" />
          <span className="text-sm">Claude is thinking through all 5 answers together</span>
        </div>
      </div>
    )
  }

  const current = queue[index]
  const isLast = index === queue.length - 1

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      advance()
    }
  }

  function advance() {
    if (isLast) {
      submit(answers)
    } else {
      setIndex((i) => i + 1)
    }
  }

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-8 px-6">
      <BigTimer remainingMs={elapsedMs} lowWarning={false} />

      <p className="text-sm uppercase tracking-wide text-neutral-500">
        Question {index + 1} of {queue.length}
      </p>

      <div className="w-full max-w-2xl">
        <h2 className="mb-1 text-lg font-semibold">{current.title}</h2>
        <p className="mb-6 text-neutral-300">{current.prompt_md}</p>

        <textarea
          ref={textareaRef}
          value={answers[current.prompt_id] ?? ''}
          onChange={(e) => setAnswers((prev) => ({ ...prev, [current.prompt_id]: e.target.value }))}
          onKeyDown={handleKeyDown}
          autoFocus
          spellCheck={true}
          placeholder="Describe your approach in plain English -- no code needed."
          rows={6}
          className="w-full resize-none rounded-md border border-neutral-800 bg-neutral-950 px-4 py-3 text-base outline-none focus:border-violet-500"
        />
        <p className="mt-2 text-xs text-neutral-600">
          Enter to continue &middot; Shift+Enter for a new line &middot; Esc to abandon
        </p>
      </div>

      <RubricLegend />

      <button
        onClick={advance}
        className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500"
      >
        {isLast ? 'Submit' : 'Next'}
      </button>
    </div>
  )
}
