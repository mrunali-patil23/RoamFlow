import { render, screen, waitFor, act, cleanup } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fc from 'fast-check';
import AuthGuard from './AuthGuard';
import { AuthProvider } from '../../contexts/AuthContext';
import { ReactNode } from 'react';

// Mock fetch to prevent actual HTTP requests
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Helper to render AuthGuard with AuthProvider
const renderAuthGuard = (children: ReactNode, fallback?: ReactNode) => {
  return render(
    <AuthProvider>
      <AuthGuard fallback={fallback}>
        {children}
      </AuthGuard>
    </AuthProvider>
  );
};

describe('AuthGuard Property Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    (global.fetch as any).mockClear();
    cleanup();
  });

  afterEach(() => {
    vi.clearAllMocks();
    cleanup();
  });

  // Feature: ai-trip-planner, Property 4: Authentication Guard Protection
  // **Validates: Requirements 1.6**
  
  it('Property 4: Authentication Guard Protection - Unauthenticated users should be redirected to login', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          contentText: fc.string({ minLength: 1, maxLength: 10 }),
          hasCustomFallback: fc.boolean(),
          fallbackText: fc.string({ minLength: 1, maxLength: 10 })
        }),
        async ({ contentText, hasCustomFallback, fallbackText }) => {
          cleanup(); // Ensure clean state
          
          // Clear any existing auth state
          localStorageMock.getItem.mockReturnValue(null);
          
          // Create protected content component with unique ID
          const testId = `protected-${Math.random().toString(36).substr(2, 5)}`;
          const ProtectedComponent = () => <div data-testid={testId}>{contentText}</div>;
          
          // Create fallback component if specified
          const fallbackId = `fallback-${Math.random().toString(36).substr(2, 5)}`;
          const FallbackComponent = hasCustomFallback ? () => <div data-testid={fallbackId}>{fallbackText}</div> : undefined;
          
          // Render AuthGuard with unauthenticated state
          const { unmount } = await act(async () => {
            return renderAuthGuard(
              <ProtectedComponent />,
              FallbackComponent ? <FallbackComponent /> : undefined
            );
          });
          
          try {
            // Property: Unauthenticated users should NOT see protected content
            expect(screen.queryByTestId(testId)).not.toBeInTheDocument();
            expect(screen.queryByText(contentText)).not.toBeInTheDocument();
            
            if (hasCustomFallback) {
              // Property: Custom fallback should be displayed when provided
              await waitFor(() => {
                expect(screen.getByTestId(fallbackId)).toBeInTheDocument();
                expect(screen.getByText(fallbackText)).toBeInTheDocument();
              }, { timeout: 1000 });
            } else {
              // Property: Default login form should be displayed when no fallback provided
              await waitFor(() => {
                expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
              }, { timeout: 1000 });
            }
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 2, timeout: 3000 }
    );
  }, 5000);

  it('Property 4: Authentication Guard Protection - Authenticated users should see protected content', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          userId: fc.string({ minLength: 1, maxLength: 10 }),
          username: fc.string({ minLength: 3, maxLength: 10 }).filter(s => /^[a-zA-Z0-9_-]+$/.test(s)),
          email: fc.emailAddress(),
          contentText: fc.string({ minLength: 1, maxLength: 10 }),
          token: fc.string({ minLength: 10, maxLength: 20 })
        }),
        async ({ userId, username, email, contentText, token }) => {
          cleanup(); // Ensure clean state
          
          // Mock authenticated state in localStorage BEFORE rendering
          const mockUser = {
            id: userId,
            username,
            email,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          };
          
          localStorageMock.getItem.mockImplementation((key: string) => {
            if (key === 'access_token') return token;
            if (key === 'user') return JSON.stringify(mockUser);
            return null;
          });
          
          // Create protected content component with unique ID
          const testId = `protected-${Math.random().toString(36).substr(2, 5)}`;
          const ProtectedComponent = () => <div data-testid={testId}>{contentText}</div>;
          
          // Render AuthGuard with authenticated state
          const { unmount } = await act(async () => {
            return renderAuthGuard(<ProtectedComponent />);
          });
          
          try {
            // Property: Authenticated users should see protected content
            await waitFor(() => {
              expect(screen.getByTestId(testId)).toBeInTheDocument();
              expect(screen.getByText(contentText)).toBeInTheDocument();
            }, { timeout: 2000 });
            
            // Property: Login form should NOT be displayed for authenticated users
            expect(screen.queryByRole('button', { name: 'Sign In' })).not.toBeInTheDocument();
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 2, timeout: 4000 }
    );
  }, 6000);

  // Simplified test for core authentication guard behavior
  it('Property 4: Authentication Guard Protection - Core behavior verification', async () => {
    // Test unauthenticated access
    localStorageMock.getItem.mockReturnValue(null);
    
    const ProtectedContent = () => <div data-testid="protected">Protected Content</div>;
    const { unmount: unmount1 } = render(
      <AuthProvider>
        <AuthGuard>
          <ProtectedContent />
        </AuthGuard>
      </AuthProvider>
    );
    
    // Should not show protected content
    expect(screen.queryByTestId('protected')).not.toBeInTheDocument();
    
    // Should show login form
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    }, { timeout: 1000 });
    
    unmount1();
    cleanup();
    
    // Test authenticated access
    const mockUser = {
      id: 'test-user',
      username: 'testuser',
      email: 'test@example.com',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };
    
    localStorageMock.getItem.mockImplementation((key: string) => {
      if (key === 'access_token') return 'valid-token';
      if (key === 'user') return JSON.stringify(mockUser);
      return null;
    });
    
    const { unmount: unmount2 } = render(
      <AuthProvider>
        <AuthGuard>
          <ProtectedContent />
        </AuthGuard>
      </AuthProvider>
    );
    
    // Should show protected content
    await waitFor(() => {
      expect(screen.getByTestId('protected')).toBeInTheDocument();
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    }, { timeout: 1000 });
    
    // Should not show login form
    expect(screen.queryByRole('button', { name: 'Sign In' })).not.toBeInTheDocument();
    
    unmount2();
    cleanup();
  });
});