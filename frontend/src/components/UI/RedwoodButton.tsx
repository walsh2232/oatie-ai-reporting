/**
 * Oracle Redwood Design System Button Component
 * WCAG 2.1 AA compliant with full accessibility support
 */
import React from 'react';
import { cn } from '../../lib/utils';

interface RedwoodButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

const RedwoodButton = React.forwardRef<HTMLButtonElement, RedwoodButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    icon,
    iconPosition = 'left',
    loading = false,
    fullWidth = false,
    children,
    disabled,
    ...props
  }, ref) => {
    const baseClasses = [
      // Base styles
      'inline-flex items-center justify-center font-medium transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      
      // Border radius following Oracle Redwood Design
      'rounded-md',
      
      // Full width option
      fullWidth && 'w-full',
    ];

    const variantClasses = {
      primary: [
        'bg-[#ED6C02] text-white border border-[#ED6C02]',
        'hover:bg-[#D84315] hover:border-[#D84315]',
        'focus:ring-[#ED6C02] focus:ring-opacity-50',
        'active:bg-[#BF360C] active:border-[#BF360C]',
      ],
      secondary: [
        'bg-white text-[#333333] border border-[#CCCCCC]',
        'hover:bg-[#F5F5F5] hover:border-[#999999]',
        'focus:ring-[#ED6C02] focus:ring-opacity-50',
        'active:bg-[#EEEEEE]',
      ],
      tertiary: [
        'bg-transparent text-[#ED6C02] border border-[#ED6C02]',
        'hover:bg-[#ED6C02] hover:text-white',
        'focus:ring-[#ED6C02] focus:ring-opacity-50',
        'active:bg-[#D84315] active:border-[#D84315]',
      ],
      danger: [
        'bg-[#F44336] text-white border border-[#F44336]',
        'hover:bg-[#D32F2F] hover:border-[#D32F2F]',
        'focus:ring-[#F44336] focus:ring-opacity-50',
        'active:bg-[#C62828] active:border-[#C62828]',
      ],
      ghost: [
        'bg-transparent text-[#333333] border-transparent',
        'hover:bg-[#F5F5F5]',
        'focus:ring-[#ED6C02] focus:ring-opacity-50',
        'active:bg-[#EEEEEE]',
      ],
    };

    const sizeClasses = {
      sm: ['px-3 py-1.5 text-sm', icon && 'gap-1.5'],
      md: ['px-4 py-2 text-base', icon && 'gap-2'],
      lg: ['px-6 py-3 text-lg', icon && 'gap-2.5'],
    };

    const iconSizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    };

    const LoadingSpinner = () => (
      <svg
        className={cn('animate-spin', iconSizeClasses[size])}
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    const renderIcon = () => {
      if (loading) {
        return <LoadingSpinner />;
      }
      if (icon) {
        return React.cloneElement(icon as React.ReactElement, {
          className: cn(iconSizeClasses[size], 'flex-shrink-0'),
          'aria-hidden': true,
        });
      }
      return null;
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        disabled={disabled || loading}
        aria-busy={loading}
        {...props}
      >
        {iconPosition === 'left' && renderIcon()}
        {children && <span className="truncate">{children}</span>}
        {iconPosition === 'right' && renderIcon()}
      </button>
    );
  }
);

RedwoodButton.displayName = 'RedwoodButton';

export { RedwoodButton };
export type { RedwoodButtonProps };