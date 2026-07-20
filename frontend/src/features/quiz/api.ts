import { apiRequest } from '../../api/client'
import type { QuizAttemptRequest, QuizAttemptResponse, QuizCategory, QuizQueueResponse, RevealResponse } from './types'

export const quizApi = {
  queue: (category: QuizCategory, durationS: number) =>
    apiRequest<QuizQueueResponse>(`/quiz/${category}/queue?duration_s=${durationS}`),
  submitAttempt: (category: QuizCategory, body: QuizAttemptRequest) =>
    apiRequest<QuizAttemptResponse>(`/quiz/${category}/attempts`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  // Single-question, non-persisting reveal -- used by every quiz category's
  // immediate-feedback flow. Never touches the session's official answer
  // list (still assembled client-side and submitted once at the end).
  reveal: (questionId: string, selectedKeys: string[]) =>
    apiRequest<RevealResponse>(`/quiz/questions/${questionId}/reveal`, {
      method: 'POST',
      body: JSON.stringify({ selected_keys: selectedKeys }),
    }),
}
