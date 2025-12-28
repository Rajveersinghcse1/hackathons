import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

export function formatRelativeTime(date: Date | string): string {
  const now = new Date();
  const then = new Date(date);
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return formatDate(date);
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    OPEN: 'bg-red-500',
    ACKNOWLEDGED: 'bg-yellow-500',
    IN_PROGRESS: 'bg-blue-500',
    RESOLVED: 'bg-green-500',
    CLOSED: 'bg-gray-500',
    ESCALATED: 'bg-purple-500',
  };
  return colors[status] || 'bg-gray-500';
}

export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    LOW: 'text-gray-600 bg-gray-100',
    MEDIUM: 'text-yellow-700 bg-yellow-100',
    HIGH: 'text-orange-700 bg-orange-100',
    CRITICAL: 'text-red-700 bg-red-100',
  };
  return colors[priority] || 'text-gray-600 bg-gray-100';
}

export function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    ELECTRICAL: '⚡',
    PLUMBING: '🚿',
    FURNITURE: '🪑',
    CLEANING: '🧹',
    CIVIL: '🏗️',
    IT_EQUIPMENT: '💻',
    SAFETY: '⚠️',
    OTHER: '📋',
  };
  return icons[category] || '📋';
}
