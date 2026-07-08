import type { MeResponse } from '../api/types'

export function EloBadge({ user }: { user: MeResponse }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-neutral-800 bg-neutral-900 px-4 py-1.5">
      <span className="text-sm font-medium text-neutral-400">{user.overall_tier}</span>
      <span className="text-sm font-semibold tabular-nums text-violet-400">{user.overall_rating}</span>
    </div>
  )
}
