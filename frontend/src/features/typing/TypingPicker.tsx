import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { TypingDuration, TypingMode } from './types'

interface TypingPickerProps {
  onStart: (mode: TypingMode, duration: TypingDuration, fingerGuide: boolean) => void
}

const MODES: { mode: TypingMode; title: string; description: string }[] = [
  {
    mode: 'classic',
    title: 'Classic',
    description: 'Type the full snippet exactly, character for character.',
  },
  {
    mode: 'reaction',
    title: 'Reaction',
    description: 'One line at a time. Get the logic right, not every character.',
  },
]

const DURATIONS: { value: TypingDuration; label: string }[] = [
  { value: 60, label: '1 min' },
  { value: 300, label: '5 min' },
  { value: 0, label: '∞ Infinite' },
]

export function TypingPicker({ onStart }: TypingPickerProps) {
  const [mode, setMode] = useState<TypingMode>('classic')
  const [duration, setDuration] = useState<TypingDuration>(60)
  const [fingerGuide, setFingerGuide] = useState(false)

  return (
    <div className="relative flex h-screen flex-col items-center justify-center gap-8 px-6">
      <Link
        to="/"
        className="absolute left-6 top-6 text-sm text-neutral-500 hover:text-neutral-300"
      >
        ← Home
      </Link>
      <h1 className="text-3xl font-bold">Type Maxxing</h1>

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

      <label className="flex cursor-pointer items-center gap-2 text-sm text-neutral-400">
        <input
          type="checkbox"
          checked={fingerGuide}
          onChange={(e) => setFingerGuide(e.target.checked)}
          className="h-4 w-4 accent-violet-500"
        />
        Show finger guide
      </label>

      <button
        onClick={() => onStart(mode, duration, fingerGuide)}
        className="rounded-md bg-violet-600 px-10 py-3 text-lg font-semibold transition hover:bg-violet-500"
      >
        Start
      </button>
    </div>
  )
}
