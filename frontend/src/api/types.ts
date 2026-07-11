export type Category = 'typing' | 'approach' | 'design'

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
