// Synthesized in-browser via Web Audio so there's no audio asset to ship or license.
let audioContext: AudioContext | null = null

function getAudioContext(): AudioContext {
  if (!audioContext) audioContext = new AudioContext()
  return audioContext
}

/** A short, bright two-note "ding" for a correctly completed line. */
export function playDing() {
  const ctx = getAudioContext()
  if (ctx.state === 'suspended') ctx.resume()

  const now = ctx.currentTime
  const osc = ctx.createOscillator()
  const gain = ctx.createGain()

  osc.type = 'sine'
  osc.frequency.setValueAtTime(880, now) // A5
  osc.frequency.exponentialRampToValueAtTime(1318.5, now + 0.09) // E6

  gain.gain.setValueAtTime(0, now)
  gain.gain.linearRampToValueAtTime(0.2, now + 0.01)
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28)

  osc.connect(gain)
  gain.connect(ctx.destination)
  osc.start(now)
  osc.stop(now + 0.3)
}
