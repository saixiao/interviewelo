/** Renders `target` as spans colored by comparison against `typed` so far:
 * correct, incorrect, the current cursor position, and untyped/pending text.
 * Characters typed past the end of `target` render appended in red. */
export function DiffText({ target, typed }: { target: string; typed: string }) {
  const length = Math.max(target.length, typed.length)
  const chars = []

  for (let i = 0; i < length; i++) {
    const targetChar = target[i]
    const typedChar = typed[i]
    const isCursor = i === typed.length

    let className = 'text-neutral-600' // pending, not yet typed
    let char = targetChar

    if (targetChar === undefined) {
      // typed past the end of the target
      className = 'text-red-400 underline decoration-red-400'
      char = typedChar
    } else if (typedChar !== undefined) {
      className = typedChar === targetChar ? 'text-neutral-100' : 'text-red-400 bg-red-950'
    }

    chars.push(
      <span key={i} className={`${className} ${isCursor ? 'bg-violet-500/30' : ''}`}>
        {char}
      </span>,
    )
  }

  return <div className="whitespace-pre font-mono text-xl leading-relaxed">{chars}</div>
}
