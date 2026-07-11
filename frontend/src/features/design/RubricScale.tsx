import { useEffect, useState } from 'react'
import { designApi } from './api'
import type { RubricDimension } from './types'

// Mirrors backend/app/llm/grader.py::DESIGN_RUBRIC_DIMENSIONS -- used only
// until the real fetch resolves, so the legend never flashes empty.
const FALLBACK_DIMENSIONS: RubricDimension[] = [
  {
    key: 'requirements',
    label: 'Requirements',
    description:
      'Did the answer pin down the functional and non-functional requirements -- scale, latency, consistency -- and let them drive the design?',
  },
  {
    key: 'high_level_design',
    label: 'High-level design',
    description: 'Are the core components, request flow, API surface, data model, and storage choices right?',
  },
  {
    key: 'deep_dives',
    label: 'Deep dives',
    description:
      'Did the answer go deep on the 1-2 areas critical for this system, with concrete mechanisms rather than hand-waving?',
  },
  {
    key: 'tradeoffs_and_scaling',
    label: 'Tradeoffs & scaling',
    description:
      'Were choices justified against alternatives, and were bottlenecks, failure modes, and stated constraints addressed?',
  },
]

export function useDesignRubric(): RubricDimension[] {
  const [dims, setDims] = useState<RubricDimension[]>(FALLBACK_DIMENSIONS)
  useEffect(() => {
    designApi
      .rubric()
      .then((d) => d.length > 0 && setDims(d))
      .catch(() => {})
  }, [])
  return dims
}

/** Collapsible strip explaining the four 0-100 grading dimensions. */
export function DesignRubricLegend({ defaultExpanded = false }: { defaultExpanded?: boolean }) {
  const dims = useDesignRubric()
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <div className="w-full rounded-lg border border-neutral-800 bg-neutral-950 px-4 py-2 text-xs text-neutral-500">
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between text-left"
      >
        <span>Graded 0-100 on {dims.length} dimensions</span>
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
