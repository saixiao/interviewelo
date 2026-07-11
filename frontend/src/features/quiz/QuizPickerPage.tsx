import { useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { QUIZ_CATEGORIES, QUIZ_CATEGORY_META } from './constants'
import type { QuizCategory } from './types'

const DURATIONS = [
  { value: 180, label: '3 min' },
  { value: 300, label: '5 min' },
  { value: 600, label: '10 min' },
]

export function QuizPickerPage() {
  const { category } = useParams<{ category: string }>()
  const navigate = useNavigate()
  const [duration, setDuration] = useState(300)

  if (!category || !QUIZ_CATEGORIES.includes(category as QuizCategory)) {
    return <Navigate to="/" replace />
  }
  const meta = QUIZ_CATEGORY_META[category as QuizCategory]

  return (
    <div className="relative flex h-screen flex-col items-center justify-center gap-8 px-6">
      <Link to="/" className="absolute left-6 top-6 text-sm text-neutral-500 hover:text-neutral-300">
        ← Home
      </Link>
      <h1 className="text-3xl font-bold">{meta.title}</h1>
      <p className="max-w-md text-center text-sm text-neutral-400">{meta.description}</p>

      <div className="flex gap-3">
        {DURATIONS.map((d) => (
          <button
            key={d.value}
            onClick={() => setDuration(d.value)}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${
              duration === d.value
                ? 'bg-violet-600 text-white'
                : 'bg-neutral-900 text-neutral-400 hover:bg-neutral-800'
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>

      <button
        onClick={() => navigate(`/quiz/${category}/play?duration=${duration}`)}
        className="rounded-md bg-violet-600 px-10 py-3 text-lg font-semibold transition hover:bg-violet-500"
      >
        Start
      </button>
    </div>
  )
}
