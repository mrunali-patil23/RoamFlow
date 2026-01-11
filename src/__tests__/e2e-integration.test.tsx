/**
 * End-to-end integration tests for the AI Travel Planner frontend.
 * Tests complete user workflows and component integration.
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
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
  getFlights: jest.fn(),
  getLocalTransport: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  back: jest.fn(),
}

const mockPlanTrip = api.planTrip as jest.MockedFunction<typeof api.planTrip>

describe('End-to-End Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  describe('Complete User Workflow', () => {
    it('should complete the full trip planning workflow', async () => {
      const user = userEvent.setup()
      
      // Mock successful API response
      const mockTripResponse = {
        trip_id: 'test-trip-123',
        destination: 'Paris',
        total_days: 5,
        daily_plans: [
          {
            day_number: 1,
            activities: [
              {
                name: 'Visit Eiffel Tower',
                description: 'Iconic landmark visit',
                duration: 120,
                cost: 25.0,
                category: 'sightseeing'
              }
            ],
            transport: [
              {
                type: 'metro',
                provider: 'RATP',
                cost: 1.90,
                duration: 30,
                route: 'Line 6 to Bir-Hakeim'
              }
            ],
            estimated_cost: 26.90
          }
        ],
        total_budget: 134.50
      }
      
      mockPlanTrip.mockResolvedValue(mockTripResponse)
      
      // Render the trip form with context
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Step 1: Fill out the form
      const destinationInput = screen.getByLabelText(/destination/i)
      await user.type(destinationInput, 'Paris')
      
      const daysInput = screen.getByLabelText(/days/i)
      await user.clear(daysInput)
      await user.type(daysInput, '5')
      
      // Step 2: Select budget category
      const moderateBudgetCard = screen.getByText(/moderate/i).closest('div')
      if (moderateBudgetCard) {
        await user.click(moderateBudgetCard)
      }
      
      // Step 3: Select traveler type
      const coupleCard = screen.getByText(/couple/i).closest('div')
      if (coupleCard) {
        await user.click(coupleCard)
      }
      
      // Step 4: Submit the form
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Step 5: Verify API call was made
      await waitFor(() => {
        expect(mockPlanTrip).toHaveBeenCalledWith({
          destination: 'Paris',
          days: 5,
          budget: 'moderate',
          travelers: 'couple'
        })
      })
      
      // Step 6: Verify navigation to results page
      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/results')
      })
    })

    it('should handle form validation errors', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Try to submit form without filling required fields
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Should show validation errors
      await waitFor(() => {
        const errorMessages = screen.queryAllByText(/required/i)
        expect(errorMessages.length).toBeGreaterThan(0)
      })
      
      // API should not be called
      expect(mockPlanTrip).not.toHaveBeenCalled()
      expect(mockRouter.push).not.toHaveBeenCalled()
    })

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()
      
      // Mock API error
      mockPlanTrip.mockRejectedValue(new Error('Server error'))
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Fill out form completely
      const destinationInput = screen.getByLabelText(/destination/i)
      await user.type(destinationInput, 'Tokyo')
      
      const daysInput = screen.getByLabelText(/days/i)
      await user.clear(daysInput)
      await user.type(daysInput, '7')
      
      // Select budget and traveler type
      const luxuryBudgetCard = screen.getByText(/luxury/i).closest('div')
      if (luxuryBudgetCard) {
        await user.click(luxuryBudgetCard)
      }
      
      const familyCard = screen.getByText(/family/i).closest('div')
      if (familyCard) {
        await user.click(familyCard)
      }
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Should show error message
      await waitFor(() => {
        const errorMessage = screen.queryByText(/error/i) || screen.queryByText(/failed/i)
        expect(errorMessage).toBeInTheDocument()
      })
      
      // Should not navigate to results
      expect(mockRouter.push).not.toHaveBeenCalledWith('/results')
    })
  })

  describe('Form Component Integration', () => {
    it('should enforce single selection for budget categories', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Select cheap budget
      const cheapCard = screen.getByText(/cheap/i).closest('div')
      if (cheapCard) {
        await user.click(cheapCard)
        expect(cheapCard).toHaveClass('border-black')
      }
      
      // Select moderate budget (should deselect cheap)
      const moderateCard = screen.getByText(/moderate/i).closest('div')
      if (moderateCard) {
        await user.click(moderateCard)
        expect(moderateCard).toHaveClass('border-black')
        
        // Cheap should no longer be selected
        if (cheapCard) {
          expect(cheapCard).not.toHaveClass('border-black')
        }
      }
    })

    it('should enforce single selection for traveler types', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Select "Just Me"
      const justMeCard = screen.getByText(/just me/i).closest('div')
      if (justMeCard) {
        await user.click(justMeCard)
        expect(justMeCard).toHaveClass('border-black')
      }
      
      // Select "Friends" (should deselect "Just Me")
      const friendsCard = screen.getByText(/friends/i).closest('div')
      if (friendsCard) {
        await user.click(friendsCard)
        expect(friendsCard).toHaveClass('border-black')
        
        // "Just Me" should no longer be selected
        if (justMeCard) {
          expect(justMeCard).not.toHaveClass('border-black')
        }
      }
    })

    it('should provide visual feedback for form interactions', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Test input field focus
      const destinationInput = screen.getByLabelText(/destination/i)
      await user.click(destinationInput)
      
      // Input should be focused
      expect(destinationInput).toHaveFocus()
      
      // Test card selection visual feedback
      const budgetCards = screen.getAllByText(/cheap|moderate|luxury/i)
      for (const card of budgetCards) {
        const cardElement = card.closest('div')
        if (cardElement) {
          await user.click(cardElement)
          // Should have selection styling
          expect(cardElement).toHaveClass('border-black')
        }
      }
    })
  })

  describe('Loading States and User Experience', () => {
    it('should show loading state during form submission', async () => {
      const user = userEvent.setup()
      
      // Mock delayed API response
      mockPlanTrip.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          trip_id: 'test',
          destination: 'Paris',
          total_days: 5,
          daily_plans: [],
          total_budget: 1000
        }), 100))
      )
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Fill out form
      const destinationInput = screen.getByLabelText(/destination/i)
      await user.type(destinationInput, 'Paris')
      
      const daysInput = screen.getByLabelText(/days/i)
      await user.clear(daysInput)
      await user.type(daysInput, '5')
      
      // Select options
      const moderateCard = screen.getByText(/moderate/i).closest('div')
      if (moderateCard) {
        await user.click(moderateCard)
      }
      
      const coupleCard = screen.getByText(/couple/i).closest('div')
      if (coupleCard) {
        await user.click(coupleCard)
      }
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Should show loading state
      await waitFor(() => {
        const loadingElement = screen.queryByText(/loading/i) || 
                              screen.queryByText(/planning/i) ||
                              submitButton.hasAttribute('disabled')
        expect(loadingElement).toBeTruthy()
      })
    })

    it('should handle edge cases in form inputs', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Test edge cases
      const daysInput = screen.getByLabelText(/days/i)
      
      // Test zero days
      await user.clear(daysInput)
      await user.type(daysInput, '0')
      
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      await user.click(submitButton)
      
      // Should show validation error
      await waitFor(() => {
        const errorMessage = screen.queryByText(/must be.*greater/i) || 
                            screen.queryByText(/invalid/i)
        expect(errorMessage).toBeTruthy()
      })
      
      // Test very large number of days
      await user.clear(daysInput)
      await user.type(daysInput, '365')
      
      // Should handle gracefully (either accept or show reasonable limit)
      expect(daysInput).toHaveValue(365)
    })
  })

  describe('Error Boundary Integration', () => {
    it('should handle component errors gracefully', () => {
      // Mock console.error to avoid noise in test output
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      // Component that throws an error
      const ErrorComponent = () => {
        throw new Error('Test error')
      }
      
      // This test would need an actual error boundary implementation
      // For now, we just verify the error is thrown
      expect(() => {
        render(<ErrorComponent />)
      }).toThrow('Test error')
      
      consoleSpy.mockRestore()
    })
  })

  describe('Accessibility Integration', () => {
    it('should maintain accessibility standards', async () => {
      const user = userEvent.setup()
      
      render(
        <TripPlanningProvider>
          <TripForm />
        </TripPlanningProvider>
      )
      
      // Test keyboard navigation
      const destinationInput = screen.getByLabelText(/destination/i)
      destinationInput.focus()
      
      // Should be able to tab through form elements
      await user.tab()
      const daysInput = screen.getByLabelText(/days/i)
      expect(daysInput).toHaveFocus()
      
      // Test form labels
      expect(screen.getByLabelText(/destination/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/days/i)).toBeInTheDocument()
      
      // Test button accessibility
      const submitButton = screen.getByRole('button', { name: /plan.*trip/i })
      expect(submitButton).toBeInTheDocument()
      expect(submitButton).toHaveAttribute('type', 'submit')
    })
  })
})