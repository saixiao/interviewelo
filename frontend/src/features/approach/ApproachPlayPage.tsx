import { useNavigate, useSearchParams } from 'react-router-dom'
import { ApproachQuickFireSession } from './ApproachQuickFireSession'
import { ApproachInfiniteSession } from './ApproachInfiniteSession'
import { useAuth } from '../../auth/AuthContext'
import type { ApproachAttemptResponse, ApproachMode } from './types'

function parseMode(value: string | null): ApproachMode {
  return value === 'infinite' ? 'infinite' : 'quickfire'
}

export function ApproachPlayPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const mode = parseMode(searchParams.get('mode'))

  function onFinish(result: ApproachAttemptResponse) {
    refreshUser().catch(() => {})
    navigate('/approach/results', { state: { result } })
  }

  return mode === 'infinite' ? <ApproachInfiniteSession /> : <ApproachQuickFireSession onFinish={onFinish} />
}
