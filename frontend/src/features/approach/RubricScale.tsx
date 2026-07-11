import { useEffect, useState } from 'react'
import { approachApi } from './api'
import type { RubricDimension } from './types'

// Mirrors backend/app/llm/grader.py::RUBRIC_DIMENSIONS -- used only until the
// real fetch resolves, so the legend never flashes empty.
const FALLBACK_DIMENSIONS: RubricDimension[] = [
  {
    key: 'approach_correctness',
    label: 'Approach correctness',
    description: 'Does the approach actually solve the problem correctly and efficiently?',
  },
  {
    key: 'complexity_awareness',
    label: 'Complexity awareness',
    description: 'Does the answer show awareness of the time/space complexity of the approach?',
  },
  {
    key: 'edge_case_awareness',
    label: 'Edge case awareness',
    description: 'Are relevant edge cases mentioned or accounted for?',
  },
  {
    key: 'communication',
    label: 'Communication',
    description: 'Is the explanation clear, well-organized, and understandable?',
  },
]

export function useRubric(): RubricDimension[] {
  const [dims, setDims] = useState<RubricDimension[]>(FALLBACK_DIMENSIONS)
  useEffect(() => {
    approachApi
      .rubric()
      .then((d) => d.length > 0 && setDims(d))
      .catch(() => {})
  }, [])
  return dims
}

/** Collapsible strip explaining the 0-100 scale, meant for session/reveal pages. */
export function RubricLegend({ defaultExpanded = false }: { defaultExpanded?: boolean }) {
  const dims = useRubric()
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <div className="w-full max-w-2xl rounded-lg border border-neutral-800 bg-neutral-950 px-4 py-2 text-xs text-neutral-500">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between text-left"
      >
        <span>Scored 0-100 on {dims.length} dimensions</span>
        <span className="text-neutral-600">{expanded ? 'Hide scale ▲' : 'Show scale ▼'}</span>
      </button>
      {expanded && (
        <dl className="mt-2 grid gap-2 border-t border-neutral-900 pt-2 sm:grid-cols-2">
          {dims.map((d) => (
            <div key={d.key}>
              <dt className="font-medium text-neutral-400">{d.label}</dt>
              <dd>{d.description}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  )
}
