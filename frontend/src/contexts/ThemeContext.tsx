/**
 * Theme Context Provider for Oracle Redwood Design System
 * Manages theme state, dark mode, and accessibility preferences
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeState {
  theme: Theme
  isDark: boolean
  highContrast: boolean
  reducedMotion: boolean
}

type ThemeAction =
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'TOGGLE_HIGH_CONTRAST' }
  | { type: 'SET_REDUCED_MOTION'; payload: boolean }
  | { type: 'UPDATE_DARK_MODE'; payload: boolean }

const initialState: ThemeState = {
  theme: (localStorage.getItem('theme') as Theme) || 'system',
  isDark: false,
  highContrast: localStorage.getItem('highContrast') === 'true',
  reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
}

function themeReducer(state: ThemeState, action: ThemeAction): ThemeState {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload }
    case 'TOGGLE_HIGH_CONTRAST':
      return { ...state, highContrast: !state.highContrast }
    case 'SET_REDUCED_MOTION':
      return { ...state, reducedMotion: action.payload }
    case 'UPDATE_DARK_MODE':
      return { ...state, isDark: action.payload }
    default:
      return state
  }
}

interface ThemeContextType {
  state: ThemeState
  setTheme: (theme: Theme) => void
  toggleHighContrast: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(themeReducer, initialState)

  // Handle theme changes
  useEffect(() => {
    const updateDarkMode = () => {
      let isDark = false
      
      if (state.theme === 'dark') {
        isDark = true
      } else if (state.theme === 'system') {
        isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      
      dispatch({ type: 'UPDATE_DARK_MODE', payload: isDark })
      
      // Update DOM
      if (isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }

    updateDarkMode()

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (state.theme === 'system') {
        updateDarkMode()
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [state.theme])

  // Handle high contrast mode
  useEffect(() => {
    if (state.highContrast) {
      document.documentElement.classList.add('high-contrast')
    } else {
      document.documentElement.classList.remove('high-contrast')
    }
    
    localStorage.setItem('highContrast', state.highContrast.toString())
  }, [state.highContrast])

  // Handle reduced motion
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const handleChange = () => {
      dispatch({ type: 'SET_REDUCED_MOTION', payload: mediaQuery.matches })
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const setTheme = (theme: Theme) => {
    dispatch({ type: 'SET_THEME', payload: theme })
    localStorage.setItem('theme', theme)
  }

  const toggleHighContrast = () => {
    dispatch({ type: 'TOGGLE_HIGH_CONTRAST' })
  }

  const contextValue: ThemeContextType = {
    state,
    setTheme,
    toggleHighContrast,
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}