import { Link } from 'react-router-dom'
import { useRubric } from './RubricScale'

export function ApproachInfoPage() {
  const dims = useRubric()

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <Link to="/approach" className="text-sm text-neutral-500 hover:text-neutral-300">
        ← Back
      </Link>

      <h1 className="mt-4 text-2xl font-bold">How scoring works</h1>
      <p className="mt-2 text-sm text-neutral-400">
        Claude grades every answer on four independent 0-100 dimensions, judged against ground-truth
        approach notes written for that specific question -- not against Claude's own guess at a
        solution. Your score for a question is the average of these four numbers.
      </p>

      <div className="mt-8 flex flex-col gap-4">
        {dims.map((d) => (
          <div key={d.key} className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
            <h3 className="font-semibold">{d.label}</h3>
            <p className="mt-1 text-sm text-neutral-400">{d.description}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-lg border border-neutral-800 bg-neutral-900 p-4 text-sm text-neutral-400">
        <p className="font-semibold text-neutral-200">Quick Fire vs Infinite</p>
        <p className="mt-1">
          Quick Fire grades all 5 answers together at the end and updates your Elo rating. Infinite
          mode grades one answer at a time as you go, streams Claude's reasoning live while it grades,
          lets you go back and review or chat about any earlier question, and never touches your
          rating -- it's unbounded practice.
        </p>
      </div>
    </div>
  )
}
