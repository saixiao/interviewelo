import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { DesignSession } from './DesignSession'
import type { DesignFinishResponse } from './types'

function parseDuration(value: string | null): number {
  const n = Number(value)
  return n === 1200 || n === 1800 || n === 2400 ? n : 1800
}

export function DesignPlayPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const durationS = parseDuration(searchParams.get('duration'))

  function onFinish(result: DesignFinishResponse) {
    refreshUser().catch(() => {})
    navigate('/design/results', { state: { result } })
  }

  return <DesignSession durationS={durationS} onFinish={onFinish} />
}
