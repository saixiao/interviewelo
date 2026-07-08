import { useNavigate, useSearchParams } from 'react-router-dom'
import { ClassicSession } from './ClassicSession'
import { ReactionSession } from './ReactionSession'
import { useAuth } from '../../auth/AuthContext'
import type { TypingAttemptResponse, TypingDuration, TypingMode } from './types'

function parseMode(value: string | null): TypingMode {
  return value === 'reaction' ? 'reaction' : 'classic'
}

// Exported for unit tests only.
// oxlint-disable-next-line react/only-export-components
export function parseDuration(value: string | null): TypingDuration {
  if (value === null) return 60
  const n = Number(value)
  if (n === 300) return 300
  if (n === 0) return 0
  return 60
}

export function TypingPlayPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()

  const mode = parseMode(searchParams.get('mode'))
  const duration = parseDuration(searchParams.get('duration'))
  const fingerGuide = searchParams.get('fingerGuide') === '1'

  function onFinish(result: TypingAttemptResponse) {
    // The server-side rating changed; refresh the shared auth state so the
    // header badge and home tiles reflect it as soon as the user navigates.
    refreshUser().catch(() => {})
    navigate('/typing/results', { state: { result } })
  }

  return mode === 'classic' ? (
    <ClassicSession duration={duration} onFinish={onFinish} showFingerGuide={fingerGuide} />
  ) : (
    <ReactionSession duration={duration} onFinish={onFinish} showFingerGuide={fingerGuide} />
  )
}
