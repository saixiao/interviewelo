import { describe, expect, it } from 'vitest'
import { parseDuration } from './TypingPlayPage'

describe('parseDuration', () => {
  it('defaults to 60 when the duration param is missing (null)', () => {
    // Regression: Number(null) === 0, which previously made a missing param
    // fall into the infinite-mode (0) sentinel instead of the 60s default.
    expect(parseDuration(null)).toBe(60)
  })

  it('parses "300" as 300', () => {
    expect(parseDuration('300')).toBe(300)
  })

  it('parses "0" as the infinite-mode sentinel 0', () => {
    expect(parseDuration('0')).toBe(0)
  })

  it('falls back to 60 for garbage input', () => {
    expect(parseDuration('banana')).toBe(60)
  })
})
