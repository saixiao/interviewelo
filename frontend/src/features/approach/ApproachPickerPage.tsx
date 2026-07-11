import { useNavigate } from 'react-router-dom'
import { ApproachPicker } from './ApproachPicker'

export function ApproachPickerPage() {
  const navigate = useNavigate()

  return <ApproachPicker onStart={(mode) => navigate(`/approach/play?mode=${mode}`)} />
}
