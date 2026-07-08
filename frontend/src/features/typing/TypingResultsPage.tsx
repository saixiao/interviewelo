import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { ResultsReveal } from '../../components/ResultsReveal'
import type { TypingAttemptResponse } from './types'

export function TypingResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = (location.state as { result?: TypingAttemptResponse } | null)?.result

  if (!result) {
    return <Navigate to="/typing" replace />
  }

  const primary =
    result.mode === 'classic'
      ? { label: 'Net WPM', value: Math.round(result.net_wpm ?? 0).toString() }
      : { label: 'Lines Correct', value: `${result.lines_correct}/${result.lines_total}` }

  const stats =
    result.mode === 'classic'
      ? [
          { label: 'Raw WPM', value: Math.round(result.raw_wpm ?? 0).toString() },
          { label: 'Accuracy', value: `${Math.round((result.accuracy ?? 0) * 100)}%` },
        ]
      : [{ label: 'Score', value: `${Math.round(result.score * 100)}%` }]

  return (
    <ResultsReveal
      primary={primary}
      stats={stats}
      elo={{
        delta: result.delta,
        ratingAfter: result.rating_after,
        tierBefore: result.tier_before,
        tierAfter: result.tier_after,
      }}
      onPlayAgain={() => navigate('/typing')}
      onHome={() => navigate('/')}
    />
  )
}
