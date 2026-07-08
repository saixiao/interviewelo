import { describe, expect, it } from 'vitest'
import { getKeyInfo } from './fingerMap'

describe('getKeyInfo', () => {
  it('maps a newline to the Enter key with the right pinky', () => {
    // FingerGuideKeyboard renders an Enter KeyCap keyed off this contract.
    const info = getKeyInfo('\n')
    expect(info).not.toBeNull()
    expect(info?.keyLabel).toBe('Enter')
    expect(info?.finger).toBe('RP')
  })
})
