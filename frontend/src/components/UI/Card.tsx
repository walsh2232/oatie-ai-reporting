/**
 * Reusable Card Component with Oracle Redwood Design System
 * WCAG 2.1 AA compliant with proper focus management
 */

import React from 'react'
import classNames from 'classnames'

interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  role?: string
  tabIndex?: number
  'aria-label'?: string
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  onClick,
  role,
  tabIndex,
  'aria-label': ariaLabel,
  ...props
}) => {
  const cardClasses = classNames(
    'card',
    {
      'cursor-pointer hover:shadow-md transition-shadow duration-200': onClick,
      'focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2': onClick,
    },
    className
  )

  const Component = onClick ? 'button' : 'div'

  return (
    <Component
      className={cardClasses}
      onClick={onClick}
      role={role}
      tabIndex={tabIndex}
      aria-label={ariaLabel}
      {...props}
    >
      {children}
    </Component>
  )
}

export default Card