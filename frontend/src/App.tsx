import { Route, Routes } from 'react-router-dom'
import { LoginPage } from './auth/LoginPage'
import { SignupPage } from './auth/SignupPage'
import { RequireAuth } from './auth/RequireAuth'
import { HomePage } from './pages/HomePage'
import { StatsPage } from './pages/StatsPage'
import { SettingsPage } from './pages/SettingsPage'
import { TypingPickerPage } from './features/typing/TypingPickerPage'
import { TypingPlayPage } from './features/typing/TypingPlayPage'
import { TypingResultsPage } from './features/typing/TypingResultsPage'
import { ApproachPickerPage } from './features/approach/ApproachPickerPage'
import { ApproachPlayPage } from './features/approach/ApproachPlayPage'
import { ApproachResultsPage } from './features/approach/ApproachResultsPage'
import { ApproachInfoPage } from './features/approach/ApproachInfoPage'
import { DesignPickerPage } from './features/design/DesignPickerPage'
import { DesignPlayPage } from './features/design/DesignPlayPage'
import { DesignResultsPage } from './features/design/DesignResultsPage'

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
        path="/settings"
        element={
          <RequireAuth>
            <SettingsPage />
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
      <Route
        path="/approach"
        element={
          <RequireAuth>
            <ApproachPickerPage />
          </RequireAuth>
        }
      />
      <Route
        path="/approach/play"
        element={
          <RequireAuth>
            <ApproachPlayPage />
          </RequireAuth>
        }
      />
      <Route
        path="/approach/results"
        element={
          <RequireAuth>
            <ApproachResultsPage />
          </RequireAuth>
        }
      />
      <Route
        path="/approach/info"
        element={
          <RequireAuth>
            <ApproachInfoPage />
          </RequireAuth>
        }
      />
      <Route
        path="/design"
        element={
          <RequireAuth>
            <DesignPickerPage />
          </RequireAuth>
        }
      />
      <Route
        path="/design/play"
        element={
          <RequireAuth>
            <DesignPlayPage />
          </RequireAuth>
        }
      />
      <Route
        path="/design/results"
        element={
          <RequireAuth>
            <DesignResultsPage />
          </RequireAuth>
        }
      />
    </Routes>
  )
}

export default App
