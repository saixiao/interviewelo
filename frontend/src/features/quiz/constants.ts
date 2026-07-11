import type { QuizCategory } from './types'

export const QUIZ_CATEGORIES: QuizCategory[] = ['python_trivia', 'systems_trivia', 'complexity']

export const QUIZ_CATEGORY_META: Record<QuizCategory, { title: string; description: string }> = {
  python_trivia: {
    title: 'Python Knowledge',
    description: 'Quick-fire multiple choice on Python language features.',
  },
  systems_trivia: {
    title: 'System Design Knowledge',
    description: 'Quick-fire trivia on systems, infra, and AI engineering.',
  },
  complexity: {
    title: 'Complexity Analysis',
    description: 'Read the code, pick its time and space complexity.',
  },
}
