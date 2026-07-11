interface Stat {
  label: string
  value: string
}

interface EloSummary {
  delta: number
  ratingAfter: number
  tierBefore: string
  tierAfter: string
}

interface ResultsRevealProps {
  primary: Stat
  stats: Stat[]
  elo: EloSummary
  onPlayAgain: () => void
  onHome: () => void
}

const PARTICLE_COLORS = ['#a78bfa', '#34d399', '#fbbf24', '#60a5fa']
const PARTICLE_COUNT = 14

function TierUpBurst() {
  const particles = Array.from({ length: PARTICLE_COUNT }, (_, i) => {
    const angle = (i / PARTICLE_COUNT) * Math.PI * 2
    const distance = 60 + (i % 3) * 20
    return {
      tx: `${Math.cos(angle) * distance}px`,
      ty: `${Math.sin(angle) * distance}px`,
      color: PARTICLE_COLORS[i % PARTICLE_COLORS.length],
      delay: `${(i % 5) * 0.03}s`,
    }
  })

  return (
    <div className="pointer-events-none absolute inset-0 overflow-visible">
      {particles.map((p, i) => (
        <span
          key={i}
          className="tier-up-particle"
          style={{
            backgroundColor: p.color,
            animationDelay: p.delay,
            // @ts-expect-error -- custom properties consumed by the tier-up-particle keyframes
            '--tx': p.tx,
            '--ty': p.ty,
          }}
        />
      ))}
    </div>
  )
}

export function ResultsReveal({ primary, stats, elo, onPlayAgain, onHome }: ResultsRevealProps) {
  const tieredUp = elo.tierBefore !== elo.tierAfter
  const deltaLabel = elo.delta > 0 ? `+${elo.delta}` : `${elo.delta}`
  const deltaColor = elo.delta > 0 ? 'text-emerald-400' : elo.delta < 0 ? 'text-red-400' : 'text-neutral-400'

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-8 px-6 text-center">
      <div>
        <p className="text-sm uppercase tracking-wide text-neutral-500">{primary.label}</p>
        <p className="text-7xl font-bold tabular-nums">{primary.value}</p>
      </div>

      <div className="flex gap-8">
        {stats.map((stat) => (
          <div key={stat.label}>
            <p className="text-xs uppercase tracking-wide text-neutral-500">{stat.label}</p>
            <p className="text-2xl font-semibold tabular-nums">{stat.value}</p>
          </div>
        ))}
      </div>

      <div
        className={`relative flex items-center gap-3 rounded-full border px-5 py-2 ${
          tieredUp ? 'tier-up-pop border-violet-500 bg-violet-950/40' : 'border-neutral-800 bg-neutral-900'
        }`}
      >
        {tieredUp && <TierUpBurst />}
        <span className="text-sm text-neutral-400">{elo.tierAfter}</span>
        <span className="text-lg font-semibold tabular-nums">{elo.ratingAfter}</span>
        <span className={`text-sm font-medium tabular-nums ${deltaColor}`}>{deltaLabel}</span>
        {tieredUp && <span className="text-sm font-medium text-violet-400">Tier up!</span>}
      </div>

      <div className="flex gap-3">
        <button
          onClick={onPlayAgain}
          className="rounded-md bg-violet-600 px-6 py-2 font-medium transition hover:bg-violet-500"
        >
          Go again
        </button>
        <button
          onClick={onHome}
          className="rounded-md border border-neutral-800 px-6 py-2 font-medium text-neutral-300 transition hover:bg-neutral-900"
        >
          Home
        </button>
      </div>
    </div>
  )
}
