/**
 * Oracle Redwood Design System Input Component
 * WCAG 2.1 AA compliant with full accessibility support
 */
import React from 'react';
import { cn } from '../../lib/utils';

interface RedwoodInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
  success?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'filled';
  inputSize?: 'sm' | 'md' | 'lg';
}

const RedwoodInput = React.forwardRef<HTMLInputElement, RedwoodInputProps>(
  ({
    className,
    type = 'text',
    label,
    helperText,
    error,
    success,
    leftIcon,
    rightIcon,
    variant = 'default',
    inputSize = 'md',
    id,
    disabled,
    required,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const helperTextId = `${inputId}-helper`;
    const errorId = `${inputId}-error`;

    const baseInputClasses = [
      'w-full transition-colors duration-200',
      'focus:outline-none focus:ring-2 focus:ring-[#ED6C02] focus:ring-opacity-50',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-[#999999]',
    ];

    const variantClasses = {
      default: [
        'border border-[#CCCCCC] bg-white',
        'hover:border-[#999999]',
        'focus:border-[#ED6C02]',
        error && 'border-[#F44336] focus:border-[#F44336] focus:ring-[#F44336]',
        success && 'border-[#4CAF50] focus:border-[#4CAF50] focus:ring-[#4CAF50]',
      ],
      filled: [
        'border-b-2 border-[#CCCCCC] bg-[#F5F5F5] rounded-t-md border-t-0 border-l-0 border-r-0',
        'hover:border-b-[#999999]',
        'focus:border-b-[#ED6C02]',
        error && 'border-b-[#F44336] focus:border-b-[#F44336] focus:ring-[#F44336]',
        success && 'border-b-[#4CAF50] focus:border-b-[#4CAF50] focus:ring-[#4CAF50]',
      ],
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    const radiusClasses = {
      default: 'rounded-md',
      filled: 'rounded-t-md',
    };

    const iconSizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    };

    const hasIcons = leftIcon || rightIcon;
    const paddingClasses = hasIcons ? {
      sm: leftIcon ? 'pl-10' : rightIcon ? 'pr-10' : '',
      md: leftIcon ? 'pl-12' : rightIcon ? 'pr-12' : '',
      lg: leftIcon ? 'pl-14' : rightIcon ? 'pr-14' : '',
    } : {};

    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              'block text-sm font-medium text-[#333333] mb-2',
              disabled && 'opacity-50'
            )}
          >
            {label}
            {required && (
              <span className="text-[#F44336] ml-1" aria-label="required">
                *
              </span>
            )}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div
              className={cn(
                'absolute left-3 top-1/2 transform -translate-y-1/2',
                'text-[#666666] pointer-events-none',
                disabled && 'opacity-50'
              )}
            >
              {React.cloneElement(leftIcon as React.ReactElement, {
                className: cn(iconSizeClasses[inputSize]),
                'aria-hidden': true,
              })}
            </div>
          )}

          {/* Input */}
          <input
            ref={ref}
            type={type}
            id={inputId}
            disabled={disabled}
            required={required}
            className={cn(
              baseInputClasses,
              variantClasses[variant],
              sizeClasses[inputSize],
              radiusClasses[variant],
              paddingClasses[inputSize],
              className
            )}
            aria-describedby={cn(
              helperText && helperTextId,
              error && errorId
            )}
            aria-invalid={error ? 'true' : 'false'}
            {...props}
          />

          {/* Right Icon */}
          {rightIcon && (
            <div
              className={cn(
                'absolute right-3 top-1/2 transform -translate-y-1/2',
                'text-[#666666] pointer-events-none',
                disabled && 'opacity-50'
              )}
            >
              {React.cloneElement(rightIcon as React.ReactElement, {
                className: cn(iconSizeClasses[inputSize]),
                'aria-hidden': true,
              })}
            </div>
          )}
        </div>

        {/* Helper Text, Error, or Success Message */}
        {(helperText || error || success) && (
          <div className="mt-2 space-y-1">
            {error && (
              <p
                id={errorId}
                className="text-sm text-[#F44336] flex items-center gap-1"
                role="alert"
              >
                <svg
                  className="w-4 h-4 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                {error}
              </p>
            )}
            
            {success && !error && (
              <p
                className="text-sm text-[#4CAF50] flex items-center gap-1"
                role="status"
              >
                <svg
                  className="w-4 h-4 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                {success}
              </p>
            )}
            
            {helperText && !error && !success && (
              <p
                id={helperTextId}
                className="text-sm text-[#666666]"
              >
                {helperText}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

RedwoodInput.displayName = 'RedwoodInput';

export { RedwoodInput };
export type { RedwoodInputProps };