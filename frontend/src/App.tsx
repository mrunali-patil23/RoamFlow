import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { CurrencyProvider } from './contexts/CurrencyContext'
import AuthGuard from './components/auth/AuthGuard'
import { AuthPage, TripPlannerPage, TripResultsPage } from './pages'
import SharedTripPage from './pages/SharedTripPage'
import ThemeToggle from './components/ui/ThemeToggle'
import CurrencyToggle from './components/ui/CurrencyToggle'
import ErrorBoundary from './components/ui/ErrorBoundary'
import { NetworkStatusIndicator } from './components/ui/NetworkStatus'

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <CurrencyProvider>
          <AuthProvider>
            <Router>
              <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Routes>
                  <Route path="/auth" element={<AuthPage />} />
                  <Route path="/shared-trip/:encodedData" element={<SharedTripPage />} />
                  <Route path="/trip-results" element={
                    <AuthGuard>
                      <TripResultsPage />
                    </AuthGuard>
                  } />
                  <Route path="/" element={
                    <AuthGuard>
                      <MainApp />
                    </AuthGuard>
                  } />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </div>
            </Router>
          </AuthProvider>
        </CurrencyProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

function MainApp() {
  const { user, logout } = useAuth();

  return (
    <>
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Roamflow: AI Trip Planner
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <NetworkStatusIndicator />
              <CurrencyToggle />
              <ThemeToggle />
              <span className="text-gray-700 dark:text-gray-300">
                Welcome, {user?.username}!
              </span>
              <button
                onClick={logout}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <HomePage />
      </main>
    </>
  );
}

function HomePage() {
  return (
    <div className="text-center">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
        Welcome to Roamflow: AI Trip Planner
      </h2>
      <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
        Plan your perfect trip with AI-powered recommendations and real-time data
      </p>
      <div className="max-w-md mx-auto">
        <TripPlannerPage />
      </div>
    </div>
  )
}

export default App