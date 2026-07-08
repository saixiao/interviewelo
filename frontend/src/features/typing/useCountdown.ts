import { useEffect, useRef, useState } from 'react'

/** Counts down from `durationS` seconds, calling `onExpire` once when it hits zero.
 * Pass `enabled=false` to skip starting the interval entirely (e.g. when a session
 * has no fixed duration) rather than feeding it a fake long duration. */
export function useCountdown(durationS: number, onExpire: () => void, enabled: boolean = true) {
  const [remainingMs, setRemainingMs] = useState(durationS * 1000)
  const expiredRef = useRef(false)
  const onExpireRef = useRef(onExpire)
  onExpireRef.current = onExpire

  useEffect(() => {
    if (!enabled) return
    const startedAt = Date.now()
    const totalMs = durationS * 1000
    const interval = setInterval(() => {
      const left = Math.max(0, totalMs - (Date.now() - startedAt))
      setRemainingMs(left)
      if (left === 0 && !expiredRef.current) {
        expiredRef.current = true
        clearInterval(interval)
        onExpireRef.current()
      }
    }, 100)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [durationS, enabled])

  return remainingMs
}
