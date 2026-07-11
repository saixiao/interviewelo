export type ApproachMode = 'quickfire' | 'infinite'

export interface QueuePrompt {
  prompt_id: string
  title: string
  prompt_md: string
}

export interface ApproachQueueResponse {
  items: QueuePrompt[]
}

export interface AnswerSubmission {
  prompt_id: string
  answer_text: string
}

export interface ApproachAttemptRequest {
  elapsed_s: number
  items: AnswerSubmission[]
  is_infinite?: boolean
}

export interface AnswerGradeResult {
  prompt_id: string
  title: string
  prompt_md: string
  answer_text: string
  approach_correctness: number
  complexity_awareness: number
  edge_case_awareness: number
  communication: number
  feedback: string
}

export interface ApproachAttemptResponse {
  score: number
  session_summary: string
  results: AnswerGradeResult[]
  rating_before: number
  rating_after: number
  delta: number
  tier_before: string
  tier_after: string
}

export interface RubricDimension {
  key: string
  label: string
  description: string
}

export interface InfiniteAttemptRequest {
  prompt_id: string
  answer_text: string
  elapsed_s: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  prompt_id: string
  answer_text: string
  feedback: string
  messages: ChatMessage[]
}

export interface ChatResponse {
  reply: string
}

/** One answered question in an infinite-mode session, including its follow-up chat. */
export interface InfiniteTurn {
  prompt: QueuePrompt
  answerText: string
  grade: AnswerGradeResult
  chat: ChatMessage[]
}
