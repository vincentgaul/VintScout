/**
 * Utility Functions
 *
 * This file contains helper functions used throughout the frontend.
 *
 * cn() - Combines CSS class names intelligently
 * This function merges Tailwind CSS classes without conflicts.
 * Example: cn("text-red-500", "text-blue-500") returns "text-blue-500"
 * (the later class wins, preventing duplicate styling)
 *
 * Used extensively with Shadcn/ui components for conditional styling.
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
