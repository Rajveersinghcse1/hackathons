import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { AlertCircle, CheckCircle2, Clock, HelpCircle, AlertTriangle } from 'lucide-react';

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

export function getStatusIcon(status: string) {
  switch (status) {
    case 'OPEN':
      return <AlertCircle className="h-4 w-4" />;
    case 'ACKNOWLEDGED':
      return <HelpCircle className="h-4 w-4" />;
    case 'IN_PROGRESS':
      return <Clock className="h-4 w-4" />;
    case 'RESOLVED':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'ESCALATED':
      return <AlertTriangle className="h-4 w-4" />;
    default:
      return <HelpCircle className="h-4 w-4" />;
  }
}
