export type QuizCategory = 'python_trivia' | 'systems_trivia' | 'complexity'

export interface QuizChoice {
  key: string
  label: string
}

export interface QueueQuestion {
  id: string
  category: QuizCategory
  topic: string | null
  difficulty: number
  prompt_md: string
  code_snippet: string | null
  language: string | null
  choices: QuizChoice[]
  multi_select: boolean
  dimension: 'time' | 'space' | null
  group_id: string | null
}

export interface QuizQueueResponse {
  category: QuizCategory
  duration_s: number
  questions: QueueQuestion[]
}

export interface AnswerSubmission {
  question_id: string
  selected_keys: string[]
}

export interface QuizAttemptRequest {
  duration_s: number
  elapsed_s: number
  answers: AnswerSubmission[]
}

export interface AnswerResult {
  question_id: string
  correct: boolean
  correct_keys: string[]
  explanation_md: string
  selected_keys: string[]
}

export interface QuizAttemptResponse {
  category: QuizCategory
  overall_score: number
  results: AnswerResult[]
  rating_before: number
  rating_after: number
  delta: number
  tier_before: string
  tier_after: string
}
