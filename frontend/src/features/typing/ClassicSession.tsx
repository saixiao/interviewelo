import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { typingApi } from './api'
import { DiffText } from './DiffText'
import { useCountdown } from '../../hooks/useCountdown'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { useStopwatch } from '../../hooks/useStopwatch'
import { useKeystrokeFeedback } from './useKeystrokeFeedback'
import { playDing } from './sound'
import type { ClassicSubmissionItem, QueueItem, TypingAttemptResponse, TypingDuration } from './types'
import { BigTimer } from '../../components/BigTimer'
import { FingerGuideKeyboard } from '../../components/FingerGuideKeyboard'

interface ClassicSessionProps {
  duration: TypingDuration
  onFinish: (result: TypingAttemptResponse) => void
  showFingerGuide?: boolean
}

export function ClassicSession({ duration, onFinish, showFingerGuide }: ClassicSessionProps) {
  const isInfinite = duration === 0
  const navigate = useNavigate()
  const [queue, setQueue] = useState<QueueItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [typed, setTyped] = useState('')
  const submissionsRef = useRef<ClassicSubmissionItem[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const pendingCursorRef = useRef<number | null>(null)
  const finishedRef = useRef(false)
  const { ref: shakeRef, triggerError, triggerCorrect } = useKeystrokeFeedback<HTMLDivElement>()

  useEscapeKey(() => {
    if (window.confirm('Abandon this session? Your progress will be lost.')) navigate('/')
  })

  useEffect(() => {
    typingApi
      .queue('classic')
      .then((res) => setQueue(res.items))
      .catch(() => setError('Could not load snippets. Is the backend running?'))
  }, [])

  const finish = useCallback(
    (elapsedS: number) => {
      if (finishedRef.current || !queue) return
      finishedRef.current = true

      const submissions = [...submissionsRef.current]
      if (typed.length > 0) {
        submissions.push({ snippet_id: queue[index % queue.length].snippet_id, typed })
      }

      typingApi
        .submitAttempt({
          mode: 'classic',
          duration_s: duration,
          elapsed_s: elapsedS,
          classic_items: submissions,
        })
        .then(onFinish)
        .catch(() => setError('Could not submit your attempt.'))
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [queue, index, typed, duration],
  )

  const remainingMs = useCountdown(duration, () => finish(duration), !isInfinite)
  const elapsedMs = useStopwatch()

  useLayoutEffect(() => {
    if (pendingCursorRef.current !== null && textareaRef.current) {
      textareaRef.current.selectionStart = textareaRef.current.selectionEnd = pendingCursorRef.current
      pendingCursorRef.current = null
    }
  }, [typed])

  useEffect(() => {
    textareaRef.current?.focus()
  }, [index])

  if (error) {
    return <div className="flex h-screen items-center justify-center text-red-400">{error}</div>
  }

  if (!queue) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">Loading...</div>
  }

  const current = queue[index % queue.length]

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const value = e.target.value

    if (value.length > typed.length) {
      const newCharIndex = value.length - 1
      if (value[newCharIndex] !== current.content[newCharIndex]) {
        triggerError()
      }
    }

    setTyped(value)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter') {
      // Every snippet is a single line -- Enter is what submits it, never an
      // auto-advance at content length, so overtyping/undertyping is always
      // visible via the diff before the user commits.
      e.preventDefault()

      if (typed === current.content) {
        triggerCorrect()
        playDing()
      }

      submissionsRef.current.push({ snippet_id: current.snippet_id, typed })
      setIndex((i) => i + 1)
      setTyped('')
      return
    }

    if (e.key === 'Tab') {
      e.preventDefault()
      const el = e.currentTarget
      const start = el.selectionStart
      const end = el.selectionEnd
      const next = typed.slice(0, start) + '    ' + typed.slice(end)
      pendingCursorRef.current = start + 4
      setTyped(next)
    }
  }

  return (
    <div
      ref={shakeRef}
      className="flex h-screen flex-col items-center justify-center gap-10 px-6 cursor-text"
      onClick={() => textareaRef.current?.focus()}
    >
      <BigTimer remainingMs={isInfinite ? elapsedMs : remainingMs} lowWarning={!isInfinite} />

      <div className="relative w-full max-w-3xl">
        <DiffText target={current.content} typed={typed} />
        <textarea
          ref={textareaRef}
          value={typed}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          autoFocus
          spellCheck={false}
          className="absolute inset-0 h-full w-full resize-none opacity-0 outline-none"
        />
      </div>

      {showFingerGuide && <FingerGuideKeyboard expectedChar={current.content[typed.length]} />}

      {isInfinite && (
        <button
          onClick={() => finish(Math.max(1, Math.round(elapsedMs / 1000)))}
          className="rounded-md bg-neutral-800 px-6 py-2 text-sm font-medium text-neutral-300 transition hover:bg-neutral-700"
        >
          Finish session
        </button>
      )}
    </div>
  )
}
