/** Standard US-QWERTY touch-typing finger assignments, used to drive the
 * on-screen finger guide. Purely a client-side lookup — the physical finger
 * a user actually pressed can't be observed, so this only ever states the
 * *recommended* finger for the next expected character. */

export type Finger = 'LP' | 'LR' | 'LM' | 'LI' | 'LT' | 'RT' | 'RI' | 'RM' | 'RR' | 'RP'

interface BaseKey {
  char: string
  finger: Finger
}

const ROW_NUMBERS: BaseKey[] = [
  { char: '`', finger: 'LP' },
  { char: '1', finger: 'LP' },
  { char: '2', finger: 'LR' },
  { char: '3', finger: 'LM' },
  { char: '4', finger: 'LI' },
  { char: '5', finger: 'LI' },
  { char: '6', finger: 'RI' },
  { char: '7', finger: 'RI' },
  { char: '8', finger: 'RM' },
  { char: '9', finger: 'RR' },
  { char: '0', finger: 'RP' },
  { char: '-', finger: 'RP' },
  { char: '=', finger: 'RP' },
]

const ROW_TOP: BaseKey[] = [
  { char: 'q', finger: 'LP' },
  { char: 'w', finger: 'LR' },
  { char: 'e', finger: 'LM' },
  { char: 'r', finger: 'LI' },
  { char: 't', finger: 'LI' },
  { char: 'y', finger: 'RI' },
  { char: 'u', finger: 'RI' },
  { char: 'i', finger: 'RM' },
  { char: 'o', finger: 'RR' },
  { char: 'p', finger: 'RP' },
  { char: '[', finger: 'RP' },
  { char: ']', finger: 'RP' },
  { char: '\\', finger: 'RP' },
]

const ROW_HOME: BaseKey[] = [
  { char: 'a', finger: 'LP' },
  { char: 's', finger: 'LR' },
  { char: 'd', finger: 'LM' },
  { char: 'f', finger: 'LI' },
  { char: 'g', finger: 'LI' },
  { char: 'h', finger: 'RI' },
  { char: 'j', finger: 'RI' },
  { char: 'k', finger: 'RM' },
  { char: 'l', finger: 'RR' },
  { char: ';', finger: 'RP' },
  { char: "'", finger: 'RP' },
]

const ROW_BOTTOM: BaseKey[] = [
  { char: 'z', finger: 'LP' },
  { char: 'x', finger: 'LR' },
  { char: 'c', finger: 'LM' },
  { char: 'v', finger: 'LI' },
  { char: 'b', finger: 'LI' },
  { char: 'n', finger: 'RI' },
  { char: 'm', finger: 'RI' },
  { char: ',', finger: 'RM' },
  { char: '.', finger: 'RR' },
  { char: '/', finger: 'RP' },
]

export const KEYBOARD_ROWS = [ROW_NUMBERS, ROW_TOP, ROW_HOME, ROW_BOTTOM]

// Shifted symbol -> the base (unshifted) key that produces it.
const SHIFT_PAIRS: Record<string, string> = {
  '~': '`', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
  _: '-', '+': '=', '{': '[', '}': ']', '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/',
}

export interface KeyInfo {
  finger: Finger
  needsShift: boolean
  shiftFinger?: Finger
  /** The base/unshifted character — used to find and highlight the physical key. */
  keyLabel: string
}

function oppositePinky(finger: Finger): Finger {
  return finger[0] === 'L' ? 'RP' : 'LP'
}

const CHAR_MAP = new Map<string, KeyInfo>()

for (const row of KEYBOARD_ROWS) {
  for (const { char, finger } of row) {
    CHAR_MAP.set(char, { finger, needsShift: false, keyLabel: char })
    if (/[a-z]/.test(char)) {
      CHAR_MAP.set(char.toUpperCase(), { finger, needsShift: true, shiftFinger: oppositePinky(finger), keyLabel: char })
    }
  }
}

for (const [shifted, base] of Object.entries(SHIFT_PAIRS)) {
  const baseInfo = CHAR_MAP.get(base)
  if (!baseInfo) continue
  CHAR_MAP.set(shifted, { finger: baseInfo.finger, needsShift: true, shiftFinger: oppositePinky(baseInfo.finger), keyLabel: base })
}

CHAR_MAP.set(' ', { finger: 'RT', needsShift: false, keyLabel: ' ' })
CHAR_MAP.set('\n', { finger: 'RP', needsShift: false, keyLabel: 'Enter' })
CHAR_MAP.set('\t', { finger: 'LP', needsShift: false, keyLabel: 'Tab' })

export function getKeyInfo(char: string | undefined): KeyInfo | null {
  if (char === undefined) return null
  return CHAR_MAP.get(char) ?? null
}

export const FINGER_LABELS: Record<Finger, string> = {
  LP: 'Left pinky',
  LR: 'Left ring',
  LM: 'Left middle',
  LI: 'Left index',
  LT: 'Left thumb',
  RT: 'Right thumb',
  RI: 'Right index',
  RM: 'Right middle',
  RR: 'Right ring',
  RP: 'Right pinky',
}

export const FINGER_COLORS: Record<Finger, string> = {
  LP: '#fb7185',
  RP: '#fb7185',
  LR: '#fbbf24',
  RR: '#fbbf24',
  LM: '#34d399',
  RM: '#34d399',
  LI: '#38bdf8',
  RI: '#38bdf8',
  LT: '#c084fc',
  RT: '#c084fc',
}
