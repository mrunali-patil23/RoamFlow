/**
 * Property-based tests for form selection components
 * Feature: ai-travel-planner
 */

import { render, screen, cleanup } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import fc from 'fast-check'
import BudgetSelector from '@/components/BudgetSelector'
import TravelerTypeSelector from '@/components/TravelerTypeSelector'
import { BudgetCategory, TravelerType } from '@/types'

// Helper function to get budget label from value
const getBudgetLabel = (value: BudgetCategory): string => {
  const labels = { cheap: 'Budget', moderate: 'Moderate', luxury: 'Luxury' }
  return labels[value]
}

// Helper function to get traveler type label from value
const getTravelerTypeLabel = (value: TravelerType): string => {
  const labels = { 'just-me': 'Just Me', couple: 'Couple', family: 'Family', friends: 'Friends' }
  return labels[value]
}

describe('Form Selection Property Tests', () => {
  afterEach(() => {
    cleanup()
  })

  /**
   * Property 2: Single Selection Enforcement
   * Feature: ai-travel-planner, Property 2: Single Selection Enforcement
   * Validates: Requirements 1.4, 1.5, 1.6
   */
  describe('Property 2: Single Selection Enforcement', () => {
    it('should enforce single selection in budget selector', async () => {
      const user = userEvent.setup()
      
      await fc.assert(
        fc.asyncProperty(
          fc.constantFrom('cheap', 'moderate', 'luxury'),
          fc.constantFrom('cheap', 'moderate', 'luxury'),
          async (firstSelection: BudgetCategory, secondSelection: BudgetCategory) => {
            let selectedValue: BudgetCategory | '' = ''
            const handleChange = (budget: BudgetCategory) => {
              selectedValue = budget
            }

            const { rerender, unmount } = render(
              <BudgetSelector value={selectedValue} onChange={handleChange} />
            )

            try {
              // Select first option using the correct aria-label pattern
              const firstLabel = getBudgetLabel(firstSelection)
              const firstButton = screen.getByRole('button', { 
                name: `Select ${firstLabel} budget option` 
              })
              await user.click(firstButton)
              
              // Rerender with updated state
              rerender(<BudgetSelector value={selectedValue} onChange={handleChange} />)
              
              // Verify first selection is active
              expect(selectedValue).toBe(firstSelection)
              expect(firstButton).toHaveClass('border-black')
              expect(firstButton).toHaveAttribute('aria-pressed', 'true')
              
              // Select second option
              const secondLabel = getBudgetLabel(secondSelection)
              const secondButton = screen.getByRole('button', { 
                name: `Select ${secondLabel} budget option` 
              })
              await user.click(secondButton)
              
              // Rerender with updated state
              rerender(<BudgetSelector value={selectedValue} onChange={handleChange} />)
              
              // Property: Only one selection should be active at a time
              expect(selectedValue).toBe(secondSelection)
              expect(secondButton).toHaveAttribute('aria-pressed', 'true')
              
              // Check visual feedback - only the second selection should have black border
              if (firstSelection !== secondSelection) {
                expect(firstButton).not.toHaveClass('border-black')
                expect(firstButton).toHaveAttribute('aria-pressed', 'false')
              }
              expect(secondButton).toHaveClass('border-black')
            } finally {
              unmount()
            }
          }
        ),
        { numRuns: 20 }
      )
    })

    it('should enforce single selection in traveler type selector', async () => {
      const user = userEvent.setup()
      
      await fc.assert(
        fc.asyncProperty(
          fc.constantFrom('just-me', 'couple', 'family', 'friends'),
          fc.constantFrom('just-me', 'couple', 'family', 'friends'),
          async (firstSelection: TravelerType, secondSelection: TravelerType) => {
            let selectedValue: TravelerType | '' = ''
            const handleChange = (travelerType: TravelerType) => {
              selectedValue = travelerType
            }

            const { rerender, unmount } = render(
              <TravelerTypeSelector value={selectedValue} onChange={handleChange} />
            )

            try {
              // Select first option using the correct aria-label pattern
              const firstLabel = getTravelerTypeLabel(firstSelection)
              const firstButton = screen.getByRole('button', { 
                name: `Select ${firstLabel} traveler type` 
              })
              await user.click(firstButton)
              
              // Rerender with updated state
              rerender(<TravelerTypeSelector value={selectedValue} onChange={handleChange} />)
              
              // Verify first selection is active
              expect(selectedValue).toBe(firstSelection)
              expect(firstButton).toHaveClass('border-black')
              expect(firstButton).toHaveAttribute('aria-pressed', 'true')
              
              // Select second option
              const secondLabel = getTravelerTypeLabel(secondSelection)
              const secondButton = screen.getByRole('button', { 
                name: `Select ${secondLabel} traveler type` 
              })
              await user.click(secondButton)
              
              // Rerender with updated state
              rerender(<TravelerTypeSelector value={selectedValue} onChange={handleChange} />)
              
              // Property: Only one selection should be active at a time
              expect(selectedValue).toBe(secondSelection)
              expect(secondButton).toHaveAttribute('aria-pressed', 'true')
              
              // Check visual feedback - only the second selection should have black border
              if (firstSelection !== secondSelection) {
                expect(firstButton).not.toHaveClass('border-black')
                expect(firstButton).toHaveAttribute('aria-pressed', 'false')
              }
              expect(secondButton).toHaveClass('border-black')
            } finally {
              unmount()
            }
          }
        ),
        { numRuns: 20 }
      )
    })

    it('should provide visual feedback for selected options', async () => {
      const user = userEvent.setup()
      
      await fc.assert(
        fc.asyncProperty(
          fc.constantFrom('cheap', 'moderate', 'luxury'),
          async (selection: BudgetCategory) => {
            let selectedValue: BudgetCategory | '' = ''
            const handleChange = (budget: BudgetCategory) => {
              selectedValue = budget
            }

            const { rerender, unmount } = render(
              <BudgetSelector value={selectedValue} onChange={handleChange} />
            )

            try {
              // Select option using the correct aria-label pattern
              const label = getBudgetLabel(selection)
              const button = screen.getByRole('button', { 
                name: `Select ${label} budget option` 
              })
              await user.click(button)
              
              // Rerender with updated state
              rerender(<BudgetSelector value={selectedValue} onChange={handleChange} />)
              
              // Property: Selected option should have visual feedback (black border)
              expect(button).toHaveClass('border-black')
              expect(button).toHaveAttribute('aria-pressed', 'true')
              
              // Property: Selected option should show "Selected" text
              expect(screen.getByText('Selected')).toBeInTheDocument()
            } finally {
              unmount()
            }
          }
        ),
        { numRuns: 15 }
      )
    })
  })
})