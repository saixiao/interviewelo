export function BigTimer({ remainingMs, lowWarning = true }: { remainingMs: number; lowWarning?: boolean }) {
  const totalSeconds = Math.ceil(remainingMs / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  const low = lowWarning && totalSeconds <= 10

  return (
    <div
      className={`text-center text-5xl font-bold tabular-nums transition-colors ${
        low ? 'text-red-400' : 'text-neutral-100'
      }`}
    >
      {minutes}:{seconds.toString().padStart(2, '0')}
    </div>
  )
}
