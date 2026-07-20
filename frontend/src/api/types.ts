export type Category = 'typing' | 'approach' | 'python_trivia' | 'systems_trivia' | 'complexity'

export interface CategoryRating {
  category: Category
  rating: number
  tier: string
  sessions_count: number
}

export interface MeResponse {
  id: string
  email: string
  display_name: string
  overall_rating: number
  overall_tier: string
  categories: CategoryRating[]
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
}

export interface CategorySummary {
  category: Category
  rating: number
  tier: string
  sessions_count: number
  best_rating: number
  sessions_today: number
}

export interface StatsSummaryResponse {
  overall_rating: number
  overall_tier: string
  tier_floor: number
  tier_next_floor: number | null
  streak_days: number
  categories: CategorySummary[]
}
