import { Route, Routes } from 'react-router-dom'
import { LoginPage } from './auth/LoginPage'
import { SignupPage } from './auth/SignupPage'
import { RequireAuth } from './auth/RequireAuth'
import { HomePage } from './pages/HomePage'
import { StatsPage } from './pages/StatsPage'
import { TypingPickerPage } from './features/typing/TypingPickerPage'
import { TypingPlayPage } from './features/typing/TypingPlayPage'
import { TypingResultsPage } from './features/typing/TypingResultsPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <HomePage />
          </RequireAuth>
        }
      />
      <Route
        path="/stats"
        element={
          <RequireAuth>
            <StatsPage />
          </RequireAuth>
        }
      />
      <Route
        path="/typing"
        element={
          <RequireAuth>
            <TypingPickerPage />
          </RequireAuth>
        }
      />
      <Route
        path="/typing/play"
        element={
          <RequireAuth>
            <TypingPlayPage />
          </RequireAuth>
        }
      />
      <Route
        path="/typing/results"
        element={
          <RequireAuth>
            <TypingResultsPage />
          </RequireAuth>
        }
      />
    </Routes>
  )
}

export default App
