export type TypingMode = 'classic' | 'reaction'
/** 0 is the "infinite" sentinel: no fixed duration, the session ends when the user stops it. */
export type TypingDuration = 60 | 300 | 0

export interface QueueItem {
  snippet_id: string
  line_index: number | null
  content: string
}

export interface TypingQueueResponse {
  mode: TypingMode
  items: QueueItem[]
}

export interface ClassicSubmissionItem {
  snippet_id: string
  typed: string
}

export interface ReactionSubmissionItem {
  snippet_id: string
  line_index: number
  typed: string
}

export interface TypingAttemptRequest {
  mode: TypingMode
  duration_s: TypingDuration
  elapsed_s: number
  classic_items?: ClassicSubmissionItem[]
  reaction_items?: ReactionSubmissionItem[]
}

export interface TypingAttemptResponse {
  mode: TypingMode
  score: number
  rating_before: number
  rating_after: number
  delta: number
  tier_before: string
  tier_after: string
  raw_wpm: number | null
  net_wpm: number | null
  accuracy: number | null
  lines_correct: number | null
  lines_total: number | null
}
