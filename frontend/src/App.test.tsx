import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from './App'
import * as AuthContext from './contexts/AuthContext'

// Mock the AuthContext
const mockAuthContext = {
  user: { id: '1', username: 'testuser', email: 'test@example.com' },
  login: vi.fn(),
  logout: vi.fn(),
  loading: false
}

describe('App', () => {
  it('renders welcome message', () => {
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue(mockAuthContext)
    
    render(<App />)
    expect(screen.getByText('Welcome to AI Trip Planner')).toBeInTheDocument()
  })

  it('renders project description', () => {
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue(mockAuthContext)
    
    render(<App />)
    expect(screen.getByText(/Plan your perfect trip with AI-powered recommendations/)).toBeInTheDocument()
  })

  it('renders trip input form', () => {
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue(mockAuthContext)
    
    render(<App />)
    expect(screen.getByText('Plan Your Perfect Trip')).toBeInTheDocument()
  })
})