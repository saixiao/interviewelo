import { apiRequest } from '../../api/client'
import type { TypingAttemptRequest, TypingAttemptResponse, TypingMode, TypingQueueResponse } from './types'

export const typingApi = {
  queue: (mode: TypingMode) => apiRequest<TypingQueueResponse>(`/typing/queue?mode=${mode}`),
  submitAttempt: (body: TypingAttemptRequest) =>
    apiRequest<TypingAttemptResponse>('/typing/attempts', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}
