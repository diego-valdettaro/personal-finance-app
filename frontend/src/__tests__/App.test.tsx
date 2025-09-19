import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../App'

// Mock the query client
vi.mock('../lib/query-client', () => ({
  queryClient: {
    getQueryData: vi.fn(),
    setQueryData: vi.fn(),
  }
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Finance App')).toBeInTheDocument()
  })
})
