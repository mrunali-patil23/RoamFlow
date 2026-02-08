# Testing Framework Setup

This document describes the testing frameworks configured for the AI Travel Planner project.

## Overview

The project uses a dual testing approach with both unit tests and property-based tests:

- **Unit Tests**: Verify specific examples, edge cases, and error conditions
- **Property-Based Tests**: Verify universal properties across all valid inputs
- Both approaches are complementary and necessary for comprehensive coverage

## Frontend Testing (Jest + React Testing Library + fast-check)

### Configuration Files
- `frontend/jest.config.js` - Jest configuration with Next.js integration
- `frontend/jest.setup.js` - Test setup and mocks
- `frontend/package.json` - Test scripts and dependencies

### Dependencies Installed
- `jest` - Testing framework
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers for DOM
- `@testing-library/user-event` - User interaction simulation
- `jest-environment-jsdom` - DOM environment for tests
- `@types/jest` - TypeScript definitions
- `fast-check` - Property-based testing library

### Running Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Example Test Structure
```typescript
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import fc from 'fast-check'

describe('Component Tests', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should support property-based testing', () => {
    fc.assert(
      fc.property(fc.string(), (str) => {
        expect(str.length).toBeGreaterThanOrEqual(0)
      })
    )
  })
})
```

## Backend Testing (pytest + FastAPI TestClient + Hypothesis)

### Configuration Files
- `backend/pytest.ini` - Pytest configuration
- `backend/conftest.py` - Test fixtures and setup
- `backend/requirements.txt` - Dependencies including test libraries

### Dependencies Installed
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `hypothesis` - Property-based testing library
- FastAPI TestClient (included with FastAPI)

### Running Backend Tests
```bash
cd backend

# Activate virtual environment (Windows)
venv\Scripts\activate

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_example.py

# Run with coverage
python -m pytest --cov=app
```

### Example Test Structure
```python
import pytest
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient

class TestAPI:
    def test_endpoint(self, client):
        """Unit test for specific endpoint behavior."""
        response = client.get("/api/test")
        assert response.status_code == 200

    @given(st.text())
    def test_property(self, text_input):
        """Property test for universal behavior."""
        result = process_text(text_input)
        assert len(result) >= 0
```

## Property-Based Testing Guidelines

### Configuration
- **Minimum iterations**: 100 per property test
- **Test tagging**: Each test must reference design document properties
- **Tag format**: `**Feature: ai-travel-planner, Property {number}: {property_text}**`

### Common Property Patterns
1. **Invariants**: Properties that remain constant after transformations
2. **Round Trip**: Operations with their inverse return to original value
3. **Idempotence**: Doing operation twice equals doing it once
4. **Metamorphic**: Relationships between inputs and outputs
5. **Error Conditions**: Invalid inputs properly signal errors

### Example Property Test
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_preserves_length(numbers):
    """Property: Sorting preserves list length."""
    sorted_numbers = sorted(numbers)
    assert len(sorted_numbers) == len(numbers)
```

## Test Organization

### Frontend Test Structure
```
frontend/
├── src/
│   ├── __tests__/          # Test files
│   │   ├── components/     # Component tests
│   │   ├── pages/          # Page tests
│   │   └── utils/          # Utility tests
│   └── components/
├── jest.config.js
└── jest.setup.js
```

### Backend Test Structure
```
backend/
├── tests/
│   ├── test_api/          # API endpoint tests
│   ├── test_services/     # Service layer tests
│   ├── test_models/       # Data model tests
│   └── test_integration/  # Integration tests
├── conftest.py
└── pytest.ini
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

- **Frontend**: `npm test` runs all Jest tests
- **Backend**: `python -m pytest` runs all pytest tests
- **Property tests**: Configured for deterministic execution
- **Coverage**: Both frameworks support coverage reporting

## Troubleshooting

### Common Issues

1. **Frontend tests fail with module resolution**
   - Check `moduleNameMapper` in `jest.config.js`
   - Ensure all imports use correct paths

2. **Backend tests fail with import errors**
   - Activate virtual environment before running tests
   - Check that all dependencies are installed

3. **Property tests are slow**
   - Reduce `max_examples` in Hypothesis settings for development
   - Use `@settings(max_examples=10)` for faster feedback

### Verification Script

Run the verification script to check all frameworks:
```bash
python test-setup.py
```

This script validates that both frontend and backend testing frameworks are properly configured and working.