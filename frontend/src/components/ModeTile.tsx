import { Link } from 'react-router-dom'
import type { CategoryRating } from '../api/types'

interface ModeTileProps {
  title: string
  description: string
  rating?: CategoryRating
  locked?: boolean
  to?: string
}

export function ModeTile({ title, description, rating, locked = true, to }: ModeTileProps) {
  const content = (
    <>
      <div>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="mt-1 text-sm text-neutral-400">{description}</p>
      </div>
      <div className="mt-6 flex items-center justify-between">
        {rating ? (
          <span className="text-sm text-neutral-400">
            {rating.tier} · <span className="tabular-nums text-neutral-200">{rating.rating}</span>
          </span>
        ) : (
          <span className="text-sm text-neutral-600">Not played yet</span>
        )}
        {locked && (
          <span className="rounded-full bg-neutral-800 px-2.5 py-0.5 text-xs font-medium text-neutral-400">
            Coming soon
          </span>
        )}
      </div>
    </>
  )

  const className = `flex flex-col justify-between rounded-2xl border p-6 transition ${
    locked
      ? 'border-neutral-900 bg-neutral-950 opacity-50'
      : 'border-neutral-800 bg-neutral-900 hover:border-violet-500 cursor-pointer'
  }`

  if (!locked && to) {
    return (
      <Link to={to} className={className}>
        {content}
      </Link>
    )
  }

  return <div className={className}>{content}</div>
}
