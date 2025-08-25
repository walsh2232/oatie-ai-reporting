/**
 * Error Message Component with accessibility features
 */

import React from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface ErrorMessageProps {
  title?: string
  message: string
  onRetry?: () => void
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Error',
  message,
  onRetry,
}) => {
  return (
    <div className="card max-w-md mx-auto text-center" role="alert" aria-live="polite">
      <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-lg mx-auto mb-4">
        <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
      </div>
      <h3 className="text-heading-sm mb-2 text-red-900">{title}</h3>
      <p className="text-body-sm text-gray-600 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-secondary"
          aria-label="Retry the failed operation"
        >
          Try Again
        </button>
      )}
    </div>
  )
}

export default ErrorMessage