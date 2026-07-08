import { afterEach, describe, expect, it } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { FingerGuideKeyboard } from './FingerGuideKeyboard'

describe('FingerGuideKeyboard', () => {
  // RTL only auto-cleans when test globals are enabled; we run without globals.
  afterEach(cleanup)

  it('renders an active Enter key when the expected character is a newline', () => {
    render(<FingerGuideKeyboard expectedChar={'\n'} />)

    // Regression for the missing Enter KeyCap: the cap must exist...
    const enterCap = screen.getByText('Enter')
    expect(enterCap).toBeInTheDocument()
    // ...and reflect the active state (active caps scale up).
    expect(enterCap.className).toContain('scale-110')

    // The finger hint names the right pinky.
    expect(screen.getByText('Right pinky')).toBeInTheDocument()
  })

  it('renders an inactive Enter key for a non-newline character', () => {
    render(<FingerGuideKeyboard expectedChar="a" />)

    const enterCap = screen.getByText('Enter')
    expect(enterCap).toBeInTheDocument()
    expect(enterCap.className).not.toContain('scale-110')
  })
})
