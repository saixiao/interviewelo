import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { approachApi, streamInfiniteGrade } from './api'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { RubricLegend } from './RubricScale'
import type { ChatMessage, InfiniteTurn, QueuePrompt } from './types'

type LivePhase = 'loading' | 'answering' | 'grading'

export function ApproachInfiniteSession() {
  const navigate = useNavigate()
  const [turns, setTurns] = useState<InfiniteTurn[]>([])
  // cursor === turns.length means "on the live card" (answering or grading
  // the next question); cursor < turns.length means viewing a past turn.
  const [cursor, setCursor] = useState(0)
  const [livePhase, setLivePhase] = useState<LivePhase>('loading')
  const [currentPrompt, setCurrentPrompt] = useState<QueuePrompt | null>(null)
  const [answerText, setAnswerText] = useState('')
  const [thinkingText, setThinkingText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [justGradedIndex, setJustGradedIndex] = useState<number | null>(null)

  const turnsRef = useRef<InfiniteTurn[]>([])
  const questionStartRef = useRef(Date.now())
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const finish = useCallback(() => {
    if (turnsRef.current.length === 0) {
      navigate('/approach')
    } else {
      navigate('/approach/results', { state: { infiniteResults: turnsRef.current.map((t) => t.grade) } })
    }
  }, [navigate])

  useEscapeKey(finish)

  const loadNextPrompt = useCallback(() => {
    setLivePhase('loading')
    setError(null)
    setThinkingText('')
    setAnswerText('')
    setCursor(turnsRef.current.length)
    approachApi
      .queue(1)
      .then((res) => {
        setCurrentPrompt(res.items[0] ?? null)
        questionStartRef.current = Date.now()
        setLivePhase('answering')
      })
      .catch(() => setError('Could not load the next prompt. Is the backend running?'))
  }, [])

  useEffect(() => {
    loadNextPrompt()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (cursor === turns.length && livePhase === 'answering') textareaRef.current?.focus()
  }, [cursor, turns.length, livePhase])

  function submitAnswer() {
    if (!currentPrompt) return
    setLivePhase('grading')
    setThinkingText('')
    const elapsedS = Math.max(1, Math.round((Date.now() - questionStartRef.current) / 1000))
    const prompt = currentPrompt

    streamInfiniteGrade(
      { prompt_id: prompt.prompt_id, answer_text: answerText, elapsed_s: elapsedS },
      {
        onThinking: (text) => setThinkingText((prev) => prev + text),
        onDone: (grade) => {
          setTurns((prev) => {
            const next = [...prev, { prompt, answerText, grade, chat: [] }]
            turnsRef.current = next
            setJustGradedIndex(next.length - 1)
            setCursor(next.length - 1)
            return next
          })
        },
        onError: (message) => {
          setError(message)
          setLivePhase('answering')
        },
      },
    ).catch(() => {
      setError('Could not grade that answer. Please try again.')
      setLivePhase('answering')
    })
  }

  function handleAnswerKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submitAnswer()
    }
  }

  function updateTurnChat(index: number, chat: ChatMessage[]) {
    setTurns((prev) => {
      const next = prev.map((t, i) => (i === index ? { ...t, chat } : t))
      turnsRef.current = next
      return next
    })
  }

  function goBack() {
    if (cursor > 0) setCursor(cursor - 1)
  }

  function goForward() {
    if (cursor + 1 < turns.length) {
      setCursor(cursor + 1)
    } else {
      loadNextPrompt()
    }
  }

  if (error && livePhase !== 'grading') {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="text-red-400">{error}</p>
        <button
          onClick={() => (currentPrompt ? setLivePhase('answering') : loadNextPrompt())}
          className="rounded-md border border-neutral-800 px-6 py-2 text-neutral-300 transition hover:bg-neutral-900"
        >
          Try again
        </button>
      </div>
    )
  }

  const canGoBack = cursor > 0

  // Viewing a completed turn (reveal + chat), whether just-graded or historical.
  if (cursor < turns.length) {
    const turn = turns[cursor]
    return (
      <TurnView
        turn={turn}
        index={cursor}
        total={turns.length}
        justGraded={justGradedIndex === cursor}
        canGoBack={canGoBack}
        onBack={goBack}
        onForward={goForward}
        onChatChange={(chat) => updateTurnChat(cursor, chat)}
      />
    )
  }

  if (livePhase === 'loading') {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 text-neutral-500">
        <p>Loading...</p>
        {canGoBack && <BackButton onClick={goBack} />}
      </div>
    )
  }

  if (livePhase === 'grading') {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 px-6">
        <p className="text-sm uppercase tracking-wide text-neutral-500">Grading your answer...</p>
        <div className="flex items-center gap-2 text-neutral-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-violet-500" />
          <span className="text-sm">Claude is thinking</span>
        </div>
        <div className="max-h-64 w-full max-w-xl overflow-y-auto rounded-md border border-neutral-800 bg-neutral-950 p-4">
          <p className="whitespace-pre-wrap text-sm text-neutral-500">
            {thinkingText || 'Reasoning about the approach and the rubric...'}
          </p>
        </div>
      </div>
    )
  }

  if (!currentPrompt) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">No prompts available.</div>
  }

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-6 px-6">
      <div className="flex w-full max-w-2xl items-center justify-between">
        {canGoBack ? <BackButton onClick={goBack} /> : <span />}
        <p className="text-sm uppercase tracking-wide text-neutral-500">
          Question {turns.length + 1} &middot; Infinite mode
        </p>
        <span />
      </div>

      <div className="w-full max-w-2xl">
        <h2 className="mb-1 text-lg font-semibold">{currentPrompt.title}</h2>
        <p className="mb-6 text-neutral-300">{currentPrompt.prompt_md}</p>

        <textarea
          ref={textareaRef}
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          onKeyDown={handleAnswerKeyDown}
          autoFocus
          spellCheck={true}
          placeholder="Describe your approach in plain English -- no code needed."
          rows={6}
          className="w-full resize-none rounded-md border border-neutral-800 bg-neutral-950 px-4 py-3 text-base outline-none focus:border-violet-500"
        />
        <p className="mt-2 text-xs text-neutral-600">
          Enter to grade this answer &middot; Shift+Enter for a new line &middot; Esc to finish
        </p>
      </div>

      <RubricLegend />

      <button
        onClick={submitAnswer}
        className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500"
      >
        Grade answer
      </button>
    </div>
  )
}

function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="rounded-md border border-neutral-800 px-3 py-1.5 text-sm text-neutral-400 transition hover:bg-neutral-900"
    >
      ← Back
    </button>
  )
}

interface TurnViewProps {
  turn: InfiniteTurn
  index: number
  total: number
  justGraded: boolean
  canGoBack: boolean
  onBack: () => void
  onForward: () => void
  onChatChange: (chat: ChatMessage[]) => void
}

function TurnView({ turn, index, total, justGraded, canGoBack, onBack, onForward, onChatChange }: TurnViewProps) {
  const { grade } = turn
  const average = Math.round(
    (grade.approach_correctness + grade.complexity_awareness + grade.edge_case_awareness + grade.communication) / 4,
  )

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-8 px-6 py-12">
      <div className="flex items-center justify-between">
        {canGoBack ? <BackButton onClick={onBack} /> : <span />}
        <p className="text-sm uppercase tracking-wide text-neutral-500">
          Question {index + 1} of {total}
        </p>
        <span className="text-xs text-neutral-600">Esc to finish</span>
      </div>

      <div className={`flex flex-col items-center gap-6 text-center ${justGraded ? 'flash-correct' : ''}`}>
        <p className="text-sm uppercase tracking-wide text-neutral-500">{grade.title}</p>
        <p className="text-7xl font-bold tabular-nums">{average}</p>

        <div className="grid w-full max-w-lg grid-cols-2 gap-3 sm:grid-cols-4">
          <DimensionScore label="Correctness" value={grade.approach_correctness} />
          <DimensionScore label="Complexity" value={grade.complexity_awareness} />
          <DimensionScore label="Edge cases" value={grade.edge_case_awareness} />
          <DimensionScore label="Communication" value={grade.communication} />
        </div>

        <RubricLegend />

        <p className="max-w-lg text-center text-sm text-neutral-400">{grade.feedback}</p>
      </div>

      <details className="rounded-lg border border-neutral-800 bg-neutral-950 p-4 text-sm text-neutral-400" open={false}>
        <summary className="cursor-pointer font-medium text-neutral-300">Your answer</summary>
        <p className="mt-2 whitespace-pre-wrap">{turn.answerText || '(no answer submitted)'}</p>
      </details>

      <ChatPanel turn={turn} onChatChange={onChatChange} />

      <div className="flex justify-center gap-3 pb-8">
        <button
          onClick={onForward}
          className="rounded-md bg-violet-600 px-8 py-2.5 font-medium transition hover:bg-violet-500"
        >
          {index + 1 < total ? 'Next →' : 'Next question'}
        </button>
      </div>
    </div>
  )
}

function DimensionScore({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-neutral-900 px-3 py-2 text-center">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  )
}

function ChatPanel({ turn, onChatChange }: { turn: InfiniteTurn; onChatChange: (chat: ChatMessage[]) => void }) {
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [chatError, setChatError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turn.chat.length])

  function send() {
    const text = draft.trim()
    if (!text || sending) return
    setChatError(null)
    const nextChat: ChatMessage[] = [...turn.chat, { role: 'user', content: text }]
    onChatChange(nextChat)
    setDraft('')
    setSending(true)

    approachApi
      .chat({
        prompt_id: turn.prompt.prompt_id,
        answer_text: turn.answerText,
        feedback: turn.grade.feedback,
        messages: nextChat,
      })
      .then((res) => {
        onChatChange([...nextChat, { role: 'assistant', content: res.reply }])
      })
      .catch(() => setChatError('Could not send that message. Please try again.'))
      .finally(() => setSending(false))
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-950">
      <p className="border-b border-neutral-800 px-4 py-2 text-xs uppercase tracking-wide text-neutral-500">
        Discuss this question with Claude
      </p>

      {turn.chat.length > 0 && (
        <div className="flex max-h-72 flex-col gap-3 overflow-y-auto px-4 py-3">
          {turn.chat.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'self-end text-right' : 'self-start'}>
              <p
                className={`inline-block max-w-md whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                  m.role === 'user' ? 'bg-violet-600 text-white' : 'bg-neutral-900 text-neutral-300'
                }`}
              >
                {m.content}
              </p>
            </div>
          ))}
          {sending && <p className="text-xs text-neutral-600">Claude is replying...</p>}
          <div ref={bottomRef} />
        </div>
      )}

      <div className="flex gap-2 p-3">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask a follow-up question, or explore an alternative approach..."
          className="flex-1 resize-none rounded-md border border-neutral-800 bg-neutral-900 px-3 py-2 text-sm outline-none focus:border-violet-500"
        />
        <button
          onClick={send}
          disabled={sending || !draft.trim()}
          className="rounded-md bg-violet-600 px-4 py-2 text-sm font-medium transition hover:bg-violet-500 disabled:opacity-40"
        >
          Send
        </button>
      </div>
      {chatError && <p className="px-3 pb-3 text-xs text-red-400">{chatError}</p>}
    </div>
  )
}
