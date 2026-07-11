import { apiRequest, getAccessToken } from '../../api/client'
import type {
  AnswerGradeResult,
  ApproachAttemptRequest,
  ApproachAttemptResponse,
  ApproachQueueResponse,
  ChatRequest,
  ChatResponse,
  InfiniteAttemptRequest,
  RubricDimension,
} from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const approachApi = {
  queue: (count?: number) =>
    apiRequest<ApproachQueueResponse>(count ? `/approach/queue?count=${count}` : '/approach/queue'),
  submitAttempt: (body: ApproachAttemptRequest) =>
    apiRequest<ApproachAttemptResponse>('/approach/attempts', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  rubric: () => apiRequest<RubricDimension[]>('/approach/rubric'),
  chat: (body: ChatRequest) =>
    apiRequest<ChatResponse>('/approach/chat', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}

interface InfiniteGradeStreamHandlers {
  onThinking: (text: string) => void
  onDone: (result: AnswerGradeResult) => void
  onError: (message: string) => void
}

/**
 * Streams SSE from POST /approach/infinite/attempts. EventSource can't carry
 * a POST body, so this reads the fetch response body by hand and parses
 * `event:` / `data:` frames itself.
 */
export async function streamInfiniteGrade(
  body: InfiniteAttemptRequest,
  handlers: InfiniteGradeStreamHandlers,
): Promise<void> {
  const headers = new Headers({ 'Content-Type': 'application/json' })
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let res: Response
  try {
    res = await fetch(`${API_URL}/approach/infinite/attempts`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(body),
    })
  } catch {
    handlers.onError('Could not reach the backend. Please try again.')
    return
  }

  if (!res.ok || !res.body) {
    handlers.onError('Could not grade that answer. Please try again.')
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let sepIndex: number
    while ((sepIndex = buffer.indexOf('\n\n')) !== -1) {
      const rawEvent = buffer.slice(0, sepIndex)
      buffer = buffer.slice(sepIndex + 2)

      const lines = rawEvent.split('\n')
      const eventLine = lines.find((l) => l.startsWith('event:'))
      const dataLine = lines.find((l) => l.startsWith('data:'))
      if (!eventLine || !dataLine) continue

      const eventName = eventLine.slice('event:'.length).trim()
      let data: Record<string, unknown>
      try {
        data = JSON.parse(dataLine.slice('data:'.length).trim())
      } catch {
        continue
      }

      if (eventName === 'thinking') handlers.onThinking(String(data.text ?? ''))
      else if (eventName === 'done') handlers.onDone(data as unknown as AnswerGradeResult)
      else if (eventName === 'error') handlers.onError(String(data.message ?? 'Something went wrong.'))
    }
  }
}
