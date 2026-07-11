import { apiRequest } from '../../api/client'
import type {
  DesignFinishResponse,
  DesignSessionCreateResponse,
  DesignSessionState,
  FollowUpResponse,
  MessageResponse,
  RubricDimension,
} from './types'

export const designApi = {
  createSession: (durationS: number) =>
    apiRequest<DesignSessionCreateResponse>('/design/sessions', {
      method: 'POST',
      body: JSON.stringify({ duration_s: durationS }),
    }),
  getSession: (sessionId: string) => apiRequest<DesignSessionState>(`/design/sessions/${sessionId}`),
  postMessage: (sessionId: string, text: string) =>
    apiRequest<MessageResponse>(`/design/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  requestFollowUp: (sessionId: string) =>
    apiRequest<FollowUpResponse>(`/design/sessions/${sessionId}/follow-up`, { method: 'POST' }),
  finishSession: (sessionId: string) =>
    apiRequest<DesignFinishResponse>(`/design/sessions/${sessionId}/finish`, { method: 'POST' }),
  rubric: () => apiRequest<RubricDimension[]>('/design/rubric'),
}
