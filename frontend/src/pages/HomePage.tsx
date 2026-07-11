import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EloBadge } from '../components/EloBadge'
import { ModeTile } from '../components/ModeTile'
import type { Category } from '../api/types'

const MODES: { category: Category; title: string; description: string; to?: string }[] = [
  {
    category: 'typing',
    title: 'Type Maxxing',
    description: 'Drill precise, fast code syntax under a clock.',
    to: '/typing',
  },
  {
    category: 'approach',
    title: 'Quick-Fire Approach',
    description: 'Rapid-fire problems, plain-English strategy only.',
    to: '/approach',
  },
  {
    category: 'design',
    title: 'System Design',
    description: 'Design a system, get LLM follow-ups and a grade.',
    to: '/design',
  },
]

export function HomePage() {
  const { user, logout } = useAuth()

  if (!user) return null

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">InterviewElo</h1>
          <p className="text-sm text-neutral-500">{user.display_name}</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/stats"
            className="rounded-md border border-neutral-800 px-3 py-1.5 text-sm text-neutral-400 hover:bg-neutral-900"
          >
            Stats
          </Link>
          <EloBadge user={user} />
          <button
            onClick={() => logout()}
            className="rounded-md border border-neutral-800 px-3 py-1.5 text-sm text-neutral-400 hover:bg-neutral-900"
          >
            Log out
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {MODES.map((mode) => (
          <ModeTile
            key={mode.category}
            title={mode.title}
            description={mode.description}
            rating={user.categories.find((c) => c.category === mode.category)}
            locked={!mode.to}
            to={mode.to}
          />
        ))}
      </div>
    </div>
  )
}
