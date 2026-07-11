import { useEffect, useState } from 'react'

/** Counts elapsed milliseconds upward from zero, ticking every 100ms. Never auto-stops. */
export function useStopwatch(): number {
  const [elapsedMs, setElapsedMs] = useState(0)

  useEffect(() => {
    const startedAt = Date.now()
    const interval = setInterval(() => {
      setElapsedMs(Date.now() - startedAt)
    }, 100)
    return () => clearInterval(interval)
  }, [])

  return elapsedMs
}
