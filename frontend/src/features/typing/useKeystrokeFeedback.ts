import { useCallback, useRef } from 'react'

function replay(el: HTMLElement, className: string) {
  el.classList.remove(className)
  void el.offsetWidth // force reflow so the animation restarts even if it's still playing
  el.classList.add(className)
}

/** Ref to attach to the element that should react to keystrokes, plus triggers
 * for the error (shake) and correct-line (green flash) feedback animations.
 * Both replay via a forced reflow so rapid repeats each get their own animation
 * instead of only the first. */
export function useKeystrokeFeedback<T extends HTMLElement>() {
  const ref = useRef<T>(null)

  const triggerError = useCallback(() => {
    if (ref.current) replay(ref.current, 'shake-on-error')
  }, [])

  const triggerCorrect = useCallback(() => {
    if (ref.current) replay(ref.current, 'flash-correct')
  }, [])

  return { ref, triggerError, triggerCorrect }
}
