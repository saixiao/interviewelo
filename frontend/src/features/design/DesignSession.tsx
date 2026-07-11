import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BigTimer } from '../../components/BigTimer'
import { useCountdown } from '../../hooks/useCountdown'
import { useEscapeKey } from '../../hooks/useEscapeKey'
import { designApi } from './api'
import { DesignRubricLegend } from './RubricScale'
import type { DesignFinishResponse, DesignPromptInfo, TranscriptEntry } from './types'

export const DESIGN_SESSION_STORAGE_KEY = 'interviewelo_design_session_id'

const MAX_FOLLOW_UPS = 5

interface DesignSessionProps {
  durationS: number
  onFinish: (result: DesignFinishResponse) => void
}

interface BootState {
  sessionId: string
  prompt: DesignPromptInfo
  durationS: number
  remainingS: number
  transcript: TranscriptEntry[]
  followUpsUsed: number
}

/** Bootstraps the session: resumes an in-progress one after a refresh (the
 * transcript is persisted turn by turn server-side) or creates a new one. */
export function DesignSession({ durationS, onFinish }: DesignSessionProps) {
  const [boot, setBoot] = useState<BootState | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function bootstrap() {
      const storedId = sessionStorage.getItem(DESIGN_SESSION_STORAGE_KEY)
      if (storedId) {
        try {
          const state = await designApi.getSession(storedId)
          if (state.status === 'in_progress' && state.remaining_s > 5) {
            if (!cancelled) {
              setBoot({
                sessionId: state.session_id,
                prompt: state.prompt,
                durationS: state.duration_s,
                remainingS: state.remaining_s,
                transcript: state.transcript,
                followUpsUsed: state.follow_ups_used,
              })
            }
            return
          }
        } catch {
          // stale or foreign id -- fall through and start fresh
        }
        // Only the effect instance that isn't cancelled (StrictMode's second,
        // "real" invocation) should touch storage -- otherwise the cancelled
        // instance can win a race and clobber it with a stale/orphaned id.
        if (!cancelled) sessionStorage.removeItem(DESIGN_SESSION_STORAGE_KEY)
      }

      try {
        const created = await designApi.createSession(durationS)
        if (cancelled) return
        sessionStorage.setItem(DESIGN_SESSION_STORAGE_KEY, created.session_id)
        setBoot({
          sessionId: created.session_id,
          prompt: created.prompt,
          durationS: created.duration_s,
          remainingS: created.duration_s,
          transcript: [],
          followUpsUsed: 0,
        })
      } catch {
        if (!cancelled) setError('Could not start a session. Is the backend running?')
      }
    }

    bootstrap()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (error) {
    return <div className="flex h-screen items-center justify-center px-6 text-center text-red-400">{error}</div>
  }
  if (!boot) {
    return <div className="flex h-screen items-center justify-center text-neutral-500">Loading...</div>
  }
  return <ActiveDesignSession {...boot} onFinish={onFinish} />
}

function ActiveDesignSession({
  sessionId,
  prompt,
  durationS,
  remainingS,
  transcript: initialTranscript,
  followUpsUsed: initialFollowUps,
  onFinish,
}: BootState & { onFinish: (result: DesignFinishResponse) => void }) {
  const navigate = useNavigate()
  const [transcript, setTranscript] = useState<TranscriptEntry[]>(initialTranscript)
  const [draft, setDraft] = useState('')
  const [followUpsUsed, setFollowUpsUsed] = useState(initialFollowUps)
  const [sending, setSending] = useState(false)
  const [followUpPending, setFollowUpPending] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const finishedRef = useRef(false)
  // Once any follow-up has happened (or been requested manually), the
  // halfway-mark auto-trigger stays off for the rest of the session.
  const autoFollowUpDoneRef = useRef(initialFollowUps > 0)
  const draftRef = useRef('')
  draftRef.current = draft
  const followUpsUsedRef = useRef(initialFollowUps)
  followUpsUsedRef.current = followUpsUsed
  const transcriptEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript])

  /** Persists whatever is in the textarea as a user turn. Returns the flushed
   * text (or null if there was nothing to flush). Throws on network failure. */
  const flushDraft = useCallback(async (): Promise<string | null> => {
    const text = draftRef.current.trim()
    if (!text) return null
    const res = await designApi.postMessage(sessionId, text)
    setTranscript(res.transcript)
    setDraft('')
    draftRef.current = ''
    return text
  }, [sessionId])

  const finish = useCallback(async () => {
    if (finishedRef.current) return
    finishedRef.current = true
    setFinishing(true)
    setActionError(null)
    try {
      await flushDraft()
    } catch {
      // grade what made it to the server rather than blocking the debrief
    }
    try {
      const result = await designApi.finishSession(sessionId)
      sessionStorage.removeItem(DESIGN_SESSION_STORAGE_KEY)
      onFinish(result)
    } catch {
      finishedRef.current = false
      setFinishing(false)
      setActionError('Could not grade your session. Please try again.')
    }
  }, [flushDraft, onFinish, sessionId])

  const requestFollowUp = useCallback(async () => {
    if (followUpPending || finishedRef.current || followUpsUsedRef.current >= MAX_FOLLOW_UPS) return
    autoFollowUpDoneRef.current = true
    setFollowUpPending(true)
    setActionError(null)
    try {
      // Flush the draft first so the interviewer sees the latest thinking.
      await flushDraft()
      const res = await designApi.requestFollowUp(sessionId)
      setTranscript((prev) => [...prev, res.entry])
      setFollowUpsUsed(res.follow_ups_used)
    } catch {
      setActionError('Could not get a follow-up question. Please try again.')
    } finally {
      setFollowUpPending(false)
    }
  }, [flushDraft, followUpPending, sessionId])

  const remainingMs = useCountdown(remainingS, finish)

  // Auto-trigger the first follow-up once the session passes its halfway
  // point, if the user hasn't requested one themselves.
  useEffect(() => {
    if (autoFollowUpDoneRef.current || finishedRef.current || followUpPending) return
    if (remainingMs <= (durationS * 1000) / 2 && followUpsUsed === 0) {
      requestFollowUp()
    }
  }, [remainingMs, durationS, followUpsUsed, followUpPending, requestFollowUp])

  useEscapeKey(
    useCallback(() => {
      if (finishedRef.current) return
      if (window.confirm('Abandon this session? It will not be graded.')) {
        finishedRef.current = true
        sessionStorage.removeItem(DESIGN_SESSION_STORAGE_KEY)
        navigate('/design')
      }
    }, [navigate]),
  )

  async function sendMessage() {
    if (sending || finishedRef.current || !draft.trim()) return
    setSending(true)
    setActionError(null)
    try {
      await flushDraft()
    } catch {
      setActionError('Could not save that message. Please try again.')
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (finishing) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 text-neutral-500">
        <p>Grading your design...</p>
        <div className="flex items-center gap-2 text-neutral-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-violet-500" />
          <span className="text-sm">Claude is reviewing the full transcript against the rubric</span>
        </div>
      </div>
    )
  }

  const followUpsLeft = MAX_FOLLOW_UPS - followUpsUsed

  return (
    <div className="flex h-screen flex-col gap-4 px-6 py-4">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between">
        <p className="w-40 text-xs text-neutral-600">Esc to abandon</p>
        <BigTimer remainingMs={remainingMs} />
        <p className="w-40 text-right text-xs text-neutral-500">
          {followUpsLeft} follow-up{followUpsLeft === 1 ? '' : 's'} left
        </p>
      </div>

      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-6 overflow-hidden">
        {/* Prompt panel: visible for the whole session */}
        <aside className="flex w-full max-w-sm flex-col gap-4 overflow-y-auto rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
          <div>
            <p className="text-xs uppercase tracking-wide text-neutral-500">Design prompt</p>
            <h2 className="mt-1 text-lg font-semibold">{prompt.title}</h2>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-neutral-300">{prompt.prompt_md}</p>
          <DesignRubricLegend />
        </aside>

        {/* Transcript + input */}
        <section className="flex min-w-0 flex-1 flex-col gap-3">
          <div className="flex-1 space-y-3 overflow-y-auto rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
            {transcript.length === 0 && (
              <p className="text-sm text-neutral-600">
                Start writing your design below. Clarify requirements, sketch the high-level
                components, then go deep where it matters. Save sections as you go &mdash; nothing
                is lost on refresh.
              </p>
            )}
            {transcript.map((entry, i) => (
              <TranscriptBubble key={`${entry.ts}-${i}`} entry={entry} />
            ))}
            {followUpPending && (
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <span className="h-2 w-2 animate-pulse rounded-full bg-violet-500" />
                Interviewer is thinking of a question...
              </div>
            )}
            <div ref={transcriptEndRef} />
          </div>

          {actionError && <p className="text-sm text-red-400">{actionError}</p>}

          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
            spellCheck={true}
            placeholder="Write the next part of your design (or answer the interviewer)..."
            rows={5}
            className="w-full resize-none rounded-md border border-neutral-800 bg-neutral-950 px-4 py-3 text-base outline-none focus:border-violet-500"
          />

          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-neutral-600">Ctrl+Enter to save a section</p>
            <div className="flex gap-3">
              <button
                onClick={requestFollowUp}
                disabled={followUpPending || followUpsUsed >= MAX_FOLLOW_UPS}
                className="rounded-md border border-neutral-700 px-4 py-2 text-sm font-medium text-neutral-300 transition enabled:hover:bg-neutral-900 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Get follow-up
              </button>
              <button
                onClick={sendMessage}
                disabled={sending || !draft.trim()}
                className="rounded-md bg-neutral-800 px-4 py-2 text-sm font-medium text-neutral-200 transition enabled:hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Save section
              </button>
              <button
                onClick={finish}
                className="rounded-md bg-violet-600 px-5 py-2 text-sm font-semibold transition hover:bg-violet-500"
              >
                Finish &amp; grade
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

function TranscriptBubble({ entry }: { entry: TranscriptEntry }) {
  if (entry.role === 'interviewer') {
    return (
      <div className="rounded-xl border border-violet-800/60 bg-violet-950/30 px-4 py-3">
        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-violet-400">Interviewer</p>
        <p className="whitespace-pre-wrap text-sm text-neutral-200">{entry.text}</p>
      </div>
    )
  }
  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-3">
      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-neutral-500">You</p>
      <p className="whitespace-pre-wrap text-sm text-neutral-200">{entry.text}</p>
    </div>
  )
}
