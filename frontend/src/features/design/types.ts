export type DesignDuration = 1200 | 1800 | 2400

export interface DesignPromptInfo {
  title: string
  prompt_md: string
  difficulty: number
}

export interface DesignSessionCreateResponse {
  session_id: string
  duration_s: number
  prompt: DesignPromptInfo
}

export interface TranscriptEntry {
  role: 'user' | 'interviewer'
  text: string
  ts: string
}

export interface DesignSessionState {
  session_id: string
  status: 'in_progress' | 'graded'
  duration_s: number
  remaining_s: number
  follow_ups_used: number
  transcript: TranscriptEntry[]
  prompt: DesignPromptInfo
}

export interface MessageResponse {
  entry: TranscriptEntry
  transcript: TranscriptEntry[]
}

export interface FollowUpResponse {
  entry: TranscriptEntry
  follow_ups_used: number
  follow_ups_remaining: number
}

export interface DesignGrade {
  requirements: number
  high_level_design: number
  deep_dives: number
  tradeoffs_and_scaling: number
  strengths: string[]
  improvements: string[]
  overall: number
}

export interface DesignFinishResponse {
  grade: DesignGrade
  overall_score: number
  prompt_title: string
  transcript: TranscriptEntry[]
  graded_at: string
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
