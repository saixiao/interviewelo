import { apiRequest } from '../../api/client'
import type { QuizAttemptRequest, QuizAttemptResponse, QuizCategory, QuizQueueResponse } from './types'

export const quizApi = {
  queue: (category: QuizCategory, durationS: number) =>
    apiRequest<QuizQueueResponse>(`/quiz/${category}/queue?duration_s=${durationS}`),
  submitAttempt: (category: QuizCategory, body: QuizAttemptRequest) =>
    apiRequest<QuizAttemptResponse>(`/quiz/${category}/attempts`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}
