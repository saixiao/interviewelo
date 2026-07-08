import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, setAccessToken } from '../api/client'
import type { MeResponse } from '../api/types'

interface AuthContextValue {
  user: MeResponse | null
  loading: boolean
  signup: (email: string, password: string, displayName: string) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    setUser(await api.me())
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      const restored = await api.refresh()
      if (restored) {
        try {
          const me = await api.me()
          if (!cancelled) setUser(me)
        } catch {
          if (!cancelled) setUser(null)
        }
      }
      if (!cancelled) setLoading(false)
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const signup = useCallback(async (email: string, password: string, displayName: string) => {
    const tokens = await api.signup(email, password, displayName)
    setAccessToken(tokens.access_token)
    await refreshUser()
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api.login(email, password)
    setAccessToken(tokens.access_token)
    await refreshUser()
  }, [refreshUser])

  const logout = useCallback(async () => {
    await api.logout()
    setAccessToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
