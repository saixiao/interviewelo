import { FINGER_COLORS, FINGER_LABELS, KEYBOARD_ROWS, getKeyInfo, type Finger } from '../features/typing/fingerMap'

interface FingerGuideKeyboardProps {
  /** The next character the user is expected to type, or undefined between snippets. */
  expectedChar: string | undefined
}

const LEGEND_FINGERS: Finger[] = ['LP', 'LR', 'LM', 'LI', 'LT']

export function FingerGuideKeyboard({ expectedChar }: FingerGuideKeyboardProps) {
  const info = getKeyInfo(expectedChar)

  return (
    <div className="flex flex-col items-center gap-5 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-5">
      <div className="flex flex-col gap-1.5">
        {KEYBOARD_ROWS.map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-1.5" style={{ marginLeft: rowIndex * 16 }}>
            {rowIndex === 3 && (
              <KeyCap
                label="Shift"
                wide
                active={info?.needsShift === true && info.shiftFinger === 'LP'}
                colorHex={FINGER_COLORS.LP}
              />
            )}
            {row.map(({ char, finger }) => (
              <KeyCap key={char} label={char} active={info?.keyLabel === char} colorHex={FINGER_COLORS[finger]} />
            ))}
            {rowIndex === 2 && (
              <KeyCap label="Enter" wide active={info?.keyLabel === 'Enter'} colorHex={FINGER_COLORS.RP} />
            )}
            {rowIndex === 3 && (
              <KeyCap
                label="Shift"
                wide
                active={info?.needsShift === true && info.shiftFinger === 'RP'}
                colorHex={FINGER_COLORS.RP}
              />
            )}
          </div>
        ))}
        <div className="mt-0.5 flex justify-center" style={{ marginLeft: 16 }}>
          <KeyCap label="␣" wide active={info?.keyLabel === ' '} colorHex={FINGER_COLORS.RT} />
        </div>
      </div>

      <HandIllustration activeFinger={info?.finger} shiftFinger={info?.needsShift ? info.shiftFinger : undefined} />

      <p className="h-5 text-sm text-neutral-300">
        {info ? (
          <>
            Use <FingerName finger={info.finger} />
            {info.needsShift && info.shiftFinger ? (
              <>
                {' '}
                + <FingerName finger={info.shiftFinger} /> (Shift)
              </>
            ) : null}
          </>
        ) : (
          <span className="text-neutral-600">Ready when you are</span>
        )}
      </p>

      <div className="flex flex-wrap justify-center gap-3 text-[11px] text-neutral-500">
        {LEGEND_FINGERS.map((finger) => (
          <span key={finger} className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: FINGER_COLORS[finger] }} />
            {FINGER_LABELS[finger].replace('Left ', '')}
          </span>
        ))}
      </div>
    </div>
  )
}

function FingerName({ finger }: { finger: Finger }) {
  return (
    <span className="font-semibold" style={{ color: FINGER_COLORS[finger] }}>
      {FINGER_LABELS[finger]}
    </span>
  )
}

function KeyCap({ label, active, colorHex, wide }: { label: string; active: boolean; colorHex: string; wide?: boolean }) {
  return (
    <div
      className={`flex h-9 items-center justify-center rounded-md border font-mono text-xs uppercase transition-all duration-150 ${
        wide ? 'px-4' : 'w-9'
      } ${active ? 'scale-110 border-white text-neutral-950 shadow-lg' : 'border-neutral-800 text-neutral-400'}`}
      style={{ backgroundColor: active ? colorHex : `${colorHex}22` }}
    >
      {label}
    </div>
  )
}

interface HandFingerSpec {
  finger: Finger
  offset: number
  rotate: number
}

const LEFT_HAND: HandFingerSpec[] = [
  { finger: 'LP', offset: 10, rotate: -18 },
  { finger: 'LR', offset: 2, rotate: -9 },
  { finger: 'LM', offset: -4, rotate: 0 },
  { finger: 'LI', offset: 4, rotate: 10 },
  { finger: 'LT', offset: 26, rotate: 34 },
]

const RIGHT_HAND: HandFingerSpec[] = [
  { finger: 'RT', offset: 26, rotate: -34 },
  { finger: 'RI', offset: 4, rotate: -10 },
  { finger: 'RM', offset: -4, rotate: 0 },
  { finger: 'RR', offset: 2, rotate: 9 },
  { finger: 'RP', offset: 10, rotate: 18 },
]

function HandIllustration({ activeFinger, shiftFinger }: { activeFinger?: Finger; shiftFinger?: Finger }) {
  return (
    <div className="flex items-end gap-10">
      <div className="flex items-end gap-1.5">
        {LEFT_HAND.map((spec) => (
          <FingerPill key={spec.finger} {...spec} isActive={spec.finger === activeFinger || spec.finger === shiftFinger} />
        ))}
      </div>
      <div className="flex items-end gap-1.5">
        {RIGHT_HAND.map((spec) => (
          <FingerPill key={spec.finger} {...spec} isActive={spec.finger === activeFinger || spec.finger === shiftFinger} />
        ))}
      </div>
    </div>
  )
}

function FingerPill({ finger, offset, rotate, isActive }: HandFingerSpec & { isActive: boolean }) {
  return (
    <div className="transition-transform duration-150" style={{ transform: `translateY(${offset}px) rotate(${rotate}deg)` }}>
      {/* Fixed box size so the active/inactive swap only transforms (scale) and repaints
          (opacity, glow) — never changes layout size, which would reflow this row on
          every keystroke and jitter the whole vertically-centered screen. */}
      <div
        className={`h-12 w-5 rounded-full transition-all duration-150 ${
          isActive ? 'scale-110 opacity-100 shadow-[0_0_14px_rgba(255,255,255,0.6)]' : 'opacity-40'
        }`}
        style={{ backgroundColor: FINGER_COLORS[finger] }}
      />
    </div>
  )
}
