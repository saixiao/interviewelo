import type { AccessTokenResponse, MeResponse } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export function getAccessToken() {
  return accessToken
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}, allowRefresh = true): Promise<T> {
  return request<T>(path, options, allowRefresh)
}

async function request<T>(path: string, options: RequestInit = {}, allowRefresh = true): Promise<T> {
  const headers = new Headers(options.headers)
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (res.status === 401 && allowRefresh && path !== '/auth/refresh') {
    if (await tryRefresh()) {
      return request<T>(path, options, false)
    }
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail ?? `Request failed with status ${res.status}`)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

async function tryRefresh(): Promise<boolean> {
  try {
    const data = await request<AccessTokenResponse>('/auth/refresh', { method: 'POST' }, false)
    setAccessToken(data.access_token)
    return true
  } catch {
    setAccessToken(null)
    return false
  }
}

export const api = {
  signup: (email: string, password: string, displayName: string) =>
    request<AccessTokenResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name: displayName }),
    }),
  login: (email: string, password: string) =>
    request<AccessTokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<void>('/auth/logout', { method: 'POST' }, false),
  refresh: () => tryRefresh(),
  me: () => request<MeResponse>('/me'),
  updateMe: (displayName: string) =>
    request<MeResponse>('/me', { method: 'PATCH', body: JSON.stringify({ display_name: displayName }) }),
}
