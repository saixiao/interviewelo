import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { DESIGN_SESSION_STORAGE_KEY } from './DesignSession'
import type { DesignDuration } from './types'

const DURATIONS: { value: DesignDuration; label: string }[] = [
  { value: 1200, label: '20 min' },
  { value: 1800, label: '30 min' },
  { value: 2400, label: '40 min' },
]

export function DesignPickerPage() {
  const navigate = useNavigate()
  const [duration, setDuration] = useState<DesignDuration>(1800)

  function start() {
    // Starting fresh from the picker always creates a new session -- the
    // stored id only exists so a mid-session refresh can resume.
    sessionStorage.removeItem(DESIGN_SESSION_STORAGE_KEY)
    navigate(`/design/play?duration=${duration}`)
  }

  return (
    <div className="relative flex h-screen flex-col items-center justify-center gap-8 px-6">
      <Link to="/" className="absolute left-6 top-6 text-sm text-neutral-500 hover:text-neutral-300">
        ← Home
      </Link>
      <h1 className="text-3xl font-bold">System Design</h1>
      <p className="max-w-md text-center text-sm text-neutral-400">
        You get a random design prompt with concrete constraints. Write your design, request
        interviewer follow-ups as you go (up to 5), and get a full debrief when time is up &mdash;
        including everything you missed.
      </p>

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
        onClick={start}
        className="rounded-md bg-violet-600 px-10 py-3 text-lg font-semibold transition hover:bg-violet-500"
      >
        Start
      </button>
    </div>
  )
}
