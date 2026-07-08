import { useCallback, useEffect, useRef, useState } from 'react'
import { typingApi } from './api'
import { useCountdown } from './useCountdown'
import { useStopwatch } from './useStopwatch'
import { useKeystrokeFeedback } from './useKeystrokeFeedback'
import { playDing } from './sound'
import type { QueueItem, ReactionSubmissionItem, TypingAttemptResponse, TypingDuration } from './types'
import { BigTimer } from '../../components/BigTimer'
import { FingerGuideKeyboard } from '../../components/FingerGuideKeyboard'

interface ReactionSessionProps {
  duration: TypingDuration
  onFinish: (result: TypingAttemptResponse) => void
  showFingerGuide?: boolean
}

export function ReactionSession({ duration, onFinish, showFingerGuide }: ReactionSessionProps) {
  const isInfinite = duration === 0
  const [queue, setQueue] = useState<QueueItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [typed, setTyped] = useState('')
  const submissionsRef = useRef<ReactionSubmissionItem[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const finishedRef = useRef(false)
  const { ref: shakeRef, triggerError, triggerCorrect } = useKeystrokeFeedback<HTMLDivElement>()

  useEffect(() => {
    typingApi
      .queue('reaction')
      .then((res) => setQueue(res.items))
      .catch(() => setError('Could not load lines. Is the backend running?'))
  }, [])

  const finish = useCallback(
    (elapsedS: number) => {
      if (finishedRef.current || !queue) return
      finishedRef.current = true

      typingApi
        .submitAttempt({
          mode: 'reaction',
          duration_s: duration,
          elapsed_s: elapsedS,
          reaction_items: submissionsRef.current,
        })
        .then(onFinish)
        .catch(() => setError('Could not submit your attempt.'))
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [queue, duration],
  )

  const remainingMs = useCountdown(duration, () => finish(duration), !isInfinite)
  const elapsedMs = useStopwatch()

  useEffect(() => {
    inputRef.current?.focus()
  }, [index])

  if (error) {
    return <div className="flex h-screen items-center justify-center text-red-400">{error}</div>
  }

  if (!queue) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">Loading...</div>
  }

  const current = queue[index % queue.length]

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      // Exact match here is just for the immediate ding/flash cue -- the server's
      // fuzzier AST-based match is what actually decides scoring.
      if (typed === current.content) {
        triggerCorrect()
        playDing()
      }

      submissionsRef.current.push({
        snippet_id: current.snippet_id,
        line_index: current.line_index ?? 0,
        typed,
      })
      setIndex((i) => i + 1)
      setTyped('')
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value

    if (value.length > typed.length) {
      const newCharIndex = value.length - 1
      if (value[newCharIndex] !== current.content[newCharIndex]) {
        triggerError()
      }
    }

    setTyped(value)
  }

  return (
    <div ref={shakeRef} className="flex h-screen flex-col items-center justify-center gap-10 px-6">
      <BigTimer remainingMs={isInfinite ? elapsedMs : remainingMs} lowWarning={!isInfinite} />

      <div className="w-full max-w-3xl text-center">
        <p className="whitespace-pre font-mono text-2xl text-neutral-100">{current.content}</p>
      </div>

      <input
        ref={inputRef}
        value={typed}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        autoFocus
        spellCheck={false}
        placeholder="Retype the line, then press Enter"
        className="w-full max-w-xl rounded-md border border-neutral-800 bg-neutral-950 px-4 py-3 text-center font-mono text-lg outline-none focus:border-violet-500"
      />

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
