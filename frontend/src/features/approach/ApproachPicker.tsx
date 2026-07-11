import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { ApproachMode } from './types'

interface ApproachPickerProps {
  onStart: (mode: ApproachMode) => void
}

const MODES: { mode: ApproachMode; title: string; description: string }[] = [
  {
    mode: 'quickfire',
    title: 'Quick Fire',
    description: '5 questions, all graded together at the end.',
  },
  {
    mode: 'infinite',
    title: 'Infinite',
    description: 'Keep going as long as you want. Each answer is graded immediately -- no Elo effect.',
  },
]

export function ApproachPicker({ onStart }: ApproachPickerProps) {
  const [mode, setMode] = useState<ApproachMode>('quickfire')

  return (
    <div className="relative flex h-screen flex-col items-center justify-center gap-8 px-6">
      <Link to="/" className="absolute left-6 top-6 text-sm text-neutral-500 hover:text-neutral-300">
        ← Home
      </Link>
      <Link to="/approach/info" className="absolute right-6 top-6 text-sm text-neutral-500 hover:text-neutral-300">
        How scoring works →
      </Link>
      <h1 className="text-3xl font-bold">Quick-Fire Approach</h1>
      <p className="max-w-md text-center text-sm text-neutral-400">
        Read each prompt and type your approach in plain English &mdash; no code, just the strategy
        you'd use. Press Enter to move on. Claude grades your answers.
      </p>

      <div className="grid w-full max-w-lg grid-cols-2 gap-4">
        {MODES.map((m) => (
          <button
            key={m.mode}
            onClick={() => setMode(m.mode)}
            className={`rounded-xl border p-5 text-left transition ${
              mode === m.mode
                ? 'border-violet-500 bg-neutral-900'
                : 'border-neutral-800 bg-neutral-950 hover:border-neutral-700'
            }`}
          >
            <h3 className="font-semibold">{m.title}</h3>
            <p className="mt-1 text-sm text-neutral-400">{m.description}</p>
          </button>
        ))}
      </div>

      <button
        onClick={() => onStart(mode)}
        className="rounded-md bg-violet-600 px-10 py-3 text-lg font-semibold transition hover:bg-violet-500"
      >
        Start
      </button>
    </div>
  )
}
