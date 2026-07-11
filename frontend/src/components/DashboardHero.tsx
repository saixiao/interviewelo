import type { StatsSummaryResponse } from '../api/types'

const MODE_LABELS: Record<string, string> = {
  typing: 'a typing sprint',
  approach: 'a quick-fire round',
  design: 'a design session',
  python_trivia: 'a Python quiz',
  systems_trivia: 'a systems quiz',
  complexity: 'a complexity round',
}

export function DashboardHero({ summary }: { summary: StatsSummaryResponse }) {
  const { overall_rating, overall_tier, tier_floor, tier_next_floor, streak_days, categories } = summary

  const progress =
    tier_next_floor === null
      ? 100
      : Math.max(0, Math.min(100, ((overall_rating - tier_floor) / (tier_next_floor - tier_floor)) * 100))

  const playedToday = categories.filter((c) => c.sessions_today > 0)
  const remainingToday = categories.filter((c) => c.sessions_today === 0)

  return (
    <div className="mb-8 rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="text-sm uppercase tracking-wide text-neutral-500">{overall_tier}</p>
          <p className="text-6xl font-bold tabular-nums">{overall_rating}</p>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-neutral-800 bg-neutral-950 px-4 py-1.5 text-sm">
          <span>🔥</span>
          <span className="font-semibold tabular-nums">{streak_days}</span>
          <span className="text-neutral-400">day streak</span>
        </div>
      </div>

      <div className="mt-4">
        <div className="h-2 overflow-hidden rounded-full bg-neutral-800">
          <div
            className="h-full rounded-full bg-violet-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-1.5 text-xs text-neutral-500">
          {tier_next_floor === null
            ? 'Top tier reached'
            : `${tier_next_floor - overall_rating} points to the next tier`}
        </p>
      </div>

      <div className="mt-5 border-t border-neutral-800 pt-4 text-sm">
        {remainingToday.length === 0 ? (
          <p className="text-emerald-400">All of today's practice is done. Nice work.</p>
        ) : (
          <p className="text-neutral-400">
            Today:{' '}
            {remainingToday.map((c, i) => (
              <span key={c.category}>
                {i > 0 && ', '}
                {MODE_LABELS[c.category] ?? c.category}
              </span>
            ))}
            {playedToday.length > 0 && <span className="text-neutral-600"> (already did {playedToday.length} today)</span>}
          </p>
        )}
      </div>
    </div>
  )
}
