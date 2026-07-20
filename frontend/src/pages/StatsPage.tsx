import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest } from '../api/client'
import type { Category } from '../api/types'

interface EloHistoryPoint {
  category: Category
  rating_before: number
  rating_after: number
  delta: number
  source_type: string
  created_at: string
}

// Validated (node scripts/validate_palette.js) categorical slots 1-5 from the
// dataviz skill's reference palette, dark-mode column, against our #0a0a0a
// surface: PASS on lightness/chroma/contrast.
const CATEGORY_COLOR: Record<Category, string> = {
  typing: '#3987e5',
  python_trivia: '#199e70',
  approach: '#c98500',
  systems_trivia: '#9085e9',
  complexity: '#e66767',
}

const CATEGORY_LABEL: Record<Category, string> = {
  typing: 'Type Maxxing',
  python_trivia: 'Python Knowledge',
  approach: 'Quick-Fire Approach',
  systems_trivia: 'System Design Knowledge',
  complexity: 'Complexity Analysis',
}

const CATEGORIES: Category[] = ['typing', 'python_trivia', 'approach', 'systems_trivia', 'complexity']

const WIDTH = 760
const HEIGHT = 340
const MARGIN = { top: 20, right: 110, bottom: 30, left: 44 }

export function StatsPage() {
  const [history, setHistory] = useState<EloHistoryPoint[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showTable, setShowTable] = useState(false)
  const [hoverIndex, setHoverIndex] = useState<number | null>(null)

  useEffect(() => {
    apiRequest<{ history: EloHistoryPoint[] }>('/stats/elo-history')
      .then((res) => setHistory(res.history))
      .catch(() => setError('Could not load stats.'))
  }, [])

  const byCategory = useMemo(() => {
    // Derived from CATEGORIES (rather than a hand-listed literal) so adding a
    // category can't silently drop its points from this grouping again.
    const grouped = CATEGORIES.reduce<Record<Category, EloHistoryPoint[]>>((acc, c) => {
      acc[c] = []
      return acc
    }, {} as Record<Category, EloHistoryPoint[]>)
    for (const point of history ?? []) {
      grouped[point.category]?.push(point)
    }
    return grouped
  }, [history])

  const maxLength = Math.max(1, ...CATEGORIES.map((c) => byCategory[c].length))

  const allRatings = CATEGORIES.flatMap((c) => byCategory[c].map((p) => p.rating_after))
  const yMin = allRatings.length ? Math.max(0, Math.min(...allRatings) - 50) : 0
  const yMax = allRatings.length ? Math.min(3000, Math.max(...allRatings) + 50) : 1000

  const plotWidth = WIDTH - MARGIN.left - MARGIN.right
  const plotHeight = HEIGHT - MARGIN.top - MARGIN.bottom

  const xForIndex = (i: number) => MARGIN.left + (maxLength <= 1 ? 0 : (i / (maxLength - 1)) * plotWidth)
  const yForRating = (r: number) => MARGIN.top + plotHeight - ((r - yMin) / (yMax - yMin || 1)) * plotHeight

  const hasAnyData = allRatings.length > 0

  if (error) {
    return <div className="flex h-screen items-center justify-center text-red-400">{error}</div>
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <Link to="/" className="text-sm text-neutral-500 hover:text-neutral-300">
            ← Home
          </Link>
          <h1 className="mt-2 text-2xl font-bold">Progression</h1>
        </div>
        <button
          onClick={() => setShowTable((v) => !v)}
          className="rounded-md border border-neutral-800 px-3 py-1.5 text-sm text-neutral-400 hover:bg-neutral-900"
        >
          {showTable ? 'Chart view' : 'Table view'}
        </button>
      </header>

      {history === null ? (
        <p className="text-neutral-500">Loading...</p>
      ) : !hasAnyData ? (
        <p className="text-neutral-500">
          No sessions yet. Play a round in any mode and your Elo history will show up here.
        </p>
      ) : showTable ? (
        <TableView history={history} />
      ) : (
        <div>
          <div className="mb-4 flex flex-wrap gap-4">
            {CATEGORIES.map((c) => (
              <div key={c} className="flex items-center gap-2 text-sm text-neutral-400">
                <span className="h-0.5 w-4 rounded-full" style={{ backgroundColor: CATEGORY_COLOR[c] }} />
                {CATEGORY_LABEL[c]}
              </div>
            ))}
          </div>

          <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            className="w-full select-none"
            onMouseMove={(e) => {
              const rect = e.currentTarget.getBoundingClientRect()
              const relX = ((e.clientX - rect.left) / rect.width) * WIDTH
              const idx = Math.round(((relX - MARGIN.left) / (plotWidth || 1)) * (maxLength - 1))
              setHoverIndex(Math.max(0, Math.min(maxLength - 1, idx)))
            }}
            onMouseLeave={() => setHoverIndex(null)}
          >
            {/* gridlines */}
            {[0, 0.25, 0.5, 0.75, 1].map((t) => {
              const y = MARGIN.top + t * plotHeight
              const rating = Math.round(yMax - t * (yMax - yMin))
              return (
                <g key={t}>
                  <line x1={MARGIN.left} x2={WIDTH - MARGIN.right} y1={y} y2={y} stroke="#2c2c2a" strokeWidth={1} />
                  <text x={MARGIN.left - 8} y={y + 4} textAnchor="end" fontSize={11} fill="#898781">
                    {rating}
                  </text>
                </g>
              )
            })}

            {/* crosshair */}
            {hoverIndex !== null && (
              <line
                x1={xForIndex(hoverIndex)}
                x2={xForIndex(hoverIndex)}
                y1={MARGIN.top}
                y2={MARGIN.top + plotHeight}
                stroke="#52514e"
                strokeWidth={1}
              />
            )}

            {CATEGORIES.map((c) => {
              const points = byCategory[c]
              if (points.length === 0) return null
              const path = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xForIndex(i)} ${yForRating(p.rating_after)}`).join(' ')
              const last = points[points.length - 1]

              return (
                <g key={c}>
                  <path d={path} fill="none" stroke={CATEGORY_COLOR[c]} strokeWidth={2} strokeLinecap="round" />
                  {points.map((p, i) => (
                    <circle key={i} cx={xForIndex(i)} cy={yForRating(p.rating_after)} r={3} fill={CATEGORY_COLOR[c]} />
                  ))}
                  <text
                    x={xForIndex(points.length - 1) + 8}
                    y={yForRating(last.rating_after) + 4}
                    fontSize={12}
                    fontWeight={600}
                    fill={CATEGORY_COLOR[c]}
                  >
                    {last.rating_after}
                  </text>
                </g>
              )
            })}
          </svg>

          {hoverIndex !== null && (
            <div className="mt-2 rounded-md border border-neutral-800 bg-neutral-900 p-3 text-sm">
              <p className="mb-1 text-neutral-500">Session #{hoverIndex + 1}</p>
              <div className="flex flex-wrap gap-4">
                {CATEGORIES.map((c) => {
                  const points = byCategory[c]
                  if (points.length === 0) return null
                  const point = points[Math.min(hoverIndex, points.length - 1)]
                  return (
                    <div key={c} className="flex items-center gap-2">
                      <span className="h-0.5 w-3 rounded-full" style={{ backgroundColor: CATEGORY_COLOR[c] }} />
                      <span className="font-semibold tabular-nums">{point.rating_after}</span>
                      <span className="text-neutral-500">{CATEGORY_LABEL[c]}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function TableView({ history }: { history: EloHistoryPoint[] }) {
  const rows = [...history].reverse()
  return (
    <div className="overflow-x-auto rounded-md border border-neutral-800">
      <table className="w-full text-left text-sm">
        <thead className="bg-neutral-900 text-neutral-400">
          <tr>
            <th className="px-3 py-2">Date</th>
            <th className="px-3 py-2">Category</th>
            <th className="px-3 py-2">Rating</th>
            <th className="px-3 py-2">Delta</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-neutral-800">
              <td className="px-3 py-2 text-neutral-400">{new Date(row.created_at).toLocaleString()}</td>
              <td className="px-3 py-2">{CATEGORY_LABEL[row.category]}</td>
              <td className="px-3 py-2 tabular-nums">{row.rating_after}</td>
              <td className={`px-3 py-2 tabular-nums ${row.delta > 0 ? 'text-emerald-400' : row.delta < 0 ? 'text-red-400' : 'text-neutral-500'}`}>
                {row.delta > 0 ? `+${row.delta}` : row.delta}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
