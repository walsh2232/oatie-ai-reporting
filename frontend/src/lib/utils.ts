/**
 * Utility function for merging class names with Tailwind CSS
 * Compatible with clsx and tailwind-merge for optimal class handling
 */
import { type ClassValue, clsx } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}