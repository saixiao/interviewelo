import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../api/client'

export function SettingsPage() {
  const { user, updateDisplayName, logout } = useAuth()
  const [displayName, setDisplayName] = useState(user?.display_name ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  if (!user) return null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setSaving(true)
    try {
      await updateDisplayName(displayName)
      setSaved(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl px-6 py-10">
      <Link to="/" className="text-sm text-neutral-500 hover:text-neutral-300">
        ← Home
      </Link>
      <h1 className="mt-2 mb-8 text-2xl font-bold">Settings</h1>

      <div className="space-y-6 rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
        <div>
          <p className="text-sm text-neutral-500">Email</p>
          <p className="mt-1">{user.email}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1">
            <label className="text-sm text-neutral-500">Display name</label>
            <input
              type="text"
              required
              minLength={1}
              maxLength={100}
              value={displayName}
              onChange={(e) => {
                setDisplayName(e.target.value)
                setSaved(false)
              }}
              className="w-full rounded-md border border-neutral-700 bg-neutral-950 px-3 py-2 outline-none focus:border-violet-500"
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={saving || displayName === user.display_name}
              className="rounded-md bg-violet-600 px-4 py-2 text-sm font-medium transition hover:bg-violet-500 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            {saved && <span className="text-sm text-emerald-400">Saved</span>}
          </div>
        </form>
      </div>

      <button
        onClick={() => logout()}
        className="mt-6 rounded-md border border-neutral-800 px-4 py-2 text-sm text-neutral-400 hover:bg-neutral-900"
      >
        Log out
      </button>
    </div>
  )
}
