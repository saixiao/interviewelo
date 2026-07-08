import { useNavigate } from 'react-router-dom'
import { TypingPicker } from './TypingPicker'

export function TypingPickerPage() {
  const navigate = useNavigate()

  return (
    <TypingPicker
      onStart={(mode, duration, fingerGuide) =>
        navigate(`/typing/play?mode=${mode}&duration=${duration}&fingerGuide=${fingerGuide ? '1' : '0'}`)
      }
    />
  )
}
