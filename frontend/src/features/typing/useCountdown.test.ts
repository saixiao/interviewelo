import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useCountdown } from './useCountdown'

describe('useCountdown', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('counts down to zero and calls onExpire once when enabled (default)', () => {
    const onExpire = vi.fn()
    const { result } = renderHook(() => useCountdown(1, onExpire))

    expect(result.current).toBe(1000)

    act(() => {
      vi.advanceTimersByTime(500)
    })
    expect(result.current).toBeLessThan(1000)
    expect(onExpire).not.toHaveBeenCalled()

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(result.current).toBe(0)
    expect(onExpire).toHaveBeenCalledTimes(1)

    // Well past expiry it must not fire again.
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(onExpire).toHaveBeenCalledTimes(1)
  })

  it('never starts the interval or calls onExpire when enabled=false', () => {
    const onExpire = vi.fn()
    const { result } = renderHook(() => useCountdown(1, onExpire, false))

    expect(result.current).toBe(1000)

    // Advance far beyond durationS -- nothing should tick.
    act(() => {
      vi.advanceTimersByTime(60_000)
    })
    expect(result.current).toBe(1000)
    expect(onExpire).not.toHaveBeenCalled()
  })
})
