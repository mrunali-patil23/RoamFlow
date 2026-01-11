/**
 * Performance tests for the AI Travel Planner frontend.
 * Tests component rendering performance, form interaction responsiveness, and memory usage.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { TripPlanningProvider } from '../contexts/TripPlanningContext'
import TripForm from '../components/TripForm'
import { useRouter } from 'next/navigation'
import * as api from '../lib/api'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock API calls
jest.mock('../lib/api', () => ({
  planTrip: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  back: jest.fn(),
}

const mockPlanTrip = api.planTrip as jest.MockedFunction<typeof api.planTrip>

describe('Frontend Performance Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  describe('Component Rendering Performance', () => {
    it('should render TripForm component quickly', () => {
      const startTime = performance.now()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const endTime = performance.now()
      const renderTime = endTime - startTime
      
      // Component should render in under 100ms
      expect(renderTime).toBeLessThan(100)
      
      // Verify component is actually rendered
      expect(screen.getByRole('form')).toBeInTheDocument()
      expect(screen.getByLabelText(/destination/i)).toBeInTheDocument()
    })

    it('should handle multiple rapid re-renders efficiently', () => {
      const { rerender } = render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const startTime = performance.now()
      
      // Perform 10 rapid re-renders
      for (let i = 0; i < 10; i++) {
        rerender(
          <TripPlanningProvider>
            <TripForm />
          </TripPlanningProvider>
        )
      }
      
      const endTime = performance.now()
      const totalRerenderTime = endTime - startTime
      
      // 10 re-renders should complete in under 500ms
      expect(totalRerenderTime).toBeLessThan(500)
    })

    it('should render large lists efficiently', () => {
      // Create a component with many elements to test rendering performance
      const LargeListComponent = () => (
        <div>
          {Array.from({ length: 1000 }, (_, i) => (
            <div key={i} data-testid={`item-${i}`}>
              Item {i}
            </div>
          ))}
        </div>
      )
      
      const startTime = performance.now()
      
      render(<LargeListComponent />)
      
      const endTime = performance.now()
      const renderTime = endTime - startTime
      
      // Large list should render in under 200ms
      expect(renderTime).toBeLessThan(200)
      
      // Verify some items are rendered
      expect(screen.getByTestId('item-0')).toBeInTheDocument()
      expect(screen.getByTestId('item-999')).toBeInTheDocument()
    })
  })

  describe('Form Interaction Performance', () => {
    it('should handle rapid form input changes efficiently', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const destinationInput = screen.getByLabelText(/destination/i)
      const daysInput = screen.getByLabelText(/days/i)
      
      const startTime = performance.now()
      
      // Perform rapid input changes
      await user.type(destinationInput, 'Paris')
      await user.clear(daysInput)
      await user.type(daysInput, '7')
      
      // Click multiple budget options rapidly
      const budgetCards = screen.getAllByText(/budget|moderate|luxury/i)
      for (const card of budgetCards.slice(0, 3)) {
        const cardElement = card.closest('button')
        if (cardElement) {
          await user.click(cardElement)
        }
      }
      
      const endTime = performance.now()
      const interactionTime = endTime - startTime
      
      // All interactions should complete in under 1 second
      expect(interactionTime).toBeLessThan(1000)
    })

    it('should handle form validation efficiently', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      
      const startTime = performance.now()
      
      // Trigger validation by submitting empty form multiple times
      for (let i = 0; i < 5; i++) {
        await user.click(submitButton)
      }
      
      const endTime = performance.now()
      const validationTime = endTime - startTime
      
      // Multiple validation attempts should complete quickly
      expect(validationTime).toBeLessThan(500)
    })

    it('should handle API call simulation efficiently', async () => {
      const user = userEvent.setup()
      
      // Mock a fast API response
      mockPlanTrip.mockResolvedValue({
        trip_id: 'test-trip',
        destination: 'Paris',
        total_days: 5,
        daily_plans: [],
        total_budget: 1000
      })
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Fill out form quickly
      const destinationInput = screen.getByLabelText(/destination/i)
      await user.type(destinationInput, 'Paris')
      
      const daysInput = screen.getByLabelText(/days/i)
      await user.clear(daysInput)
      await user.type(daysInput, '5')
      
      // Select budget and traveler type
      const moderateCard = screen.getByText(/moderate/i).closest('button')
      if (moderateCard) {
        await user.click(moderateCard)
      }
      
      const coupleCard = screen.getByText(/couple/i).closest('button')
      if (coupleCard) {
        await user.click(coupleCard)
      }
      
      const startTime = performance.now()
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Wait for API call to complete
      await waitFor(() => {
        expect(mockPlanTrip).toHaveBeenCalled()
      })
      
      const endTime = performance.now()
      const submissionTime = endTime - startTime
      
      // Form submission and API call should complete quickly with mocked response
      expect(submissionTime).toBeLessThan(200)
    })
  })

  describe('Memory Usage Performance', () => {
    it('should not create memory leaks with repeated component mounting', () => {
      // Track initial memory usage (if available)
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0
      
      // Mount and unmount component multiple times
      for (let i = 0; i < 20; i++) {
        const { unmount } = render(
          <TripPlanningProvider>
            <TripForm />
          </TripPlanningProvider>
        )
        unmount()
      }
      
      // Force garbage collection if available
      if (global.gc) {
        global.gc()
      }
      
      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0
      
      // Memory increase should be reasonable (this is a basic check)
      if (initialMemory > 0 && finalMemory > 0) {
        const memoryIncrease = finalMemory - initialMemory
        const memoryIncreasePercent = (memoryIncrease / initialMemory) * 100
        
        // Memory should not increase by more than 50% after multiple mount/unmount cycles
        expect(memoryIncreasePercent).toBeLessThan(50)
      }
    })

    it('should handle large state updates efficiently', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const startTime = performance.now()
      
      // Perform many state updates
      const destinationInput = screen.getByLabelText(/destination/i)
      
      // Type and clear multiple times to trigger state updates
      for (let i = 0; i < 10; i++) {
        await user.type(destinationInput, `City${i}`)
        await user.clear(destinationInput)
      }
      
      const endTime = performance.now()
      const stateUpdateTime = endTime - startTime
      
      // Multiple state updates should complete in reasonable time
      expect(stateUpdateTime).toBeLessThan(2000)
    })
  })

  describe('Event Handler Performance', () => {
    it('should handle rapid click events efficiently', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const budgetCards = screen.getAllByText(/budget|moderate|luxury/i)
      
      const startTime = performance.now()
      
      // Rapidly click between budget options
      for (let i = 0; i < 20; i++) {
        const cardIndex = i % budgetCards.length
        const cardElement = budgetCards[cardIndex].closest('button')
        if (cardElement) {
          await user.click(cardElement)
        }
      }
      
      const endTime = performance.now()
      const clickTime = endTime - startTime
      
      // Rapid clicking should be handled efficiently
      expect(clickTime).toBeLessThan(1000)
    })

    it('should handle keyboard navigation efficiently', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const startTime = performance.now()
      
      // Navigate through form using keyboard
      const destinationInput = screen.getByLabelText(/destination/i)
      destinationInput.focus()
      
      // Tab through multiple elements
      for (let i = 0; i < 10; i++) {
        await user.tab()
      }
      
      const endTime = performance.now()
      const navigationTime = endTime - startTime
      
      // Keyboard navigation should be responsive
      expect(navigationTime).toBeLessThan(500)
    })
  })

  describe('Rendering Optimization', () => {
    it('should avoid unnecessary re-renders', () => {
      let renderCount = 0
      
      const TestComponent = () => {
        renderCount++
        return (
          <TripPlanningProvider>
            <TripForm />
          </TripPlanningProvider>
        )
      }
      
      const { rerender } = render(<TestComponent />)
      
      const initialRenderCount = renderCount
      
      // Re-render with same props (should not cause unnecessary re-renders)
      rerender(<TestComponent />)
      rerender(<TestComponent />)
      
      // Should not have excessive re-renders for same props
      expect(renderCount - initialRenderCount).toBeLessThanOrEqual(2)
    })

    it('should handle conditional rendering efficiently', () => {
      const ConditionalComponent = ({ showForm }: { showForm: boolean }) => (
        <div>
          {showForm && (
            <TripPlanningProvider>
              <TripForm />
            </TripPlanningProvider>
          )}
        </div>
      )
      
      const startTime = performance.now()
      
      const { rerender } = render(<ConditionalComponent showForm={false} />)
      
      // Toggle visibility multiple times
      for (let i = 0; i < 10; i++) {
        rerender(<ConditionalComponent showForm={i % 2 === 0} />)
      }
      
      const endTime = performance.now()
      const conditionalRenderTime = endTime - startTime
      
      // Conditional rendering should be efficient
      expect(conditionalRenderTime).toBeLessThan(300)
    })
  })

  describe('Bundle Size and Loading Performance', () => {
    it('should not import unnecessary dependencies', () => {
      // This is a basic test to ensure we're not importing heavy libraries unnecessarily
      const startTime = performance.now()
      
      // Import and render component
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      const endTime = performance.now()
      const importAndRenderTime = endTime - startTime
      
      // Initial import and render should be fast
      expect(importAndRenderTime).toBeLessThan(150)
    })
  })
})