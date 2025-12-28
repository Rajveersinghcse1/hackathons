import { useAuthStore } from './store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'ADMIN' | 'STAFF' | 'CITIZEN';
  department?: string;
  phone?: string;
  avatarUrl?: string;
  createdAt: string;
}

export interface Issue {
  id: string;
  title: string;
  description: string | null;
  category: string;
  status: string;
  priority: string;
  latitude: number;
  longitude: number;
  building?: string;
  floor?: string;
  room?: string;
  locationDescription?: string;
  photoUrl?: string;
  resolvedPhotoUrl?: string;
  isUpvoted?: boolean;
  createdAt: string;
  updatedAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  escalatedAt?: string;
  escalationLevel: number;
  reporterId: string;
  assigneeId?: string;
  reporter: {
    id: string;
    name: string;
    avatarUrl?: string;
  };
  assignee?: {
    id: string;
    name: string;
    avatarUrl?: string;
    role?: string;
  };
  comments?: Comment[];
  activityLogs?: ActivityLog[];
  _count?: {
    upvotes: number;
    comments: number;
  };
}

export interface Comment {
  id: string;
  content: string;
  createdAt: string;
  author: User;
}

export interface ActivityLog {
  id: string;
  action: string;
  details?: string;
  createdAt: string;
  user: User;
}

export interface Stats {
  totalIssues: number;
  openIssues: number;
  resolvedThisWeek: number;
  resolutionRate: number;
  avgResolutionHours: number | null;
  categoryStats: { category: string; count: number }[];
  priorityStats: { priority: string; count: number }[];
  recentIssues: {
    id: string;
    title: string;
    category: string;
    status: string;
    createdAt: string;
    building: string;
  }[];
  topReporters: {
    id: string;
    name: string;
    avatarUrl: string | null;
    department: string;
    issueCount: number;
  }[];
}

export interface HeatmapPoint {
  id: string;
  lat: number;
  lng: number;
  weight: number;
  category: string;
  building: string | null;
  upvotes: number;
}

export interface HeatmapData {
  points: HeatmapPoint[];
  buildings: { name: string; count: number }[];
}

export interface AdminStats {
  dailyIssues: { date: string; count: number }[];
  staffPerformance: {
    id: string;
    name: string;
    assigned: number;
    resolved: number;
    avgResolutionHours: number | null;
  }[];
  escalatedIssues: number;
  overdueIssues: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface IssueFilters {
  page?: number;
  limit?: number;
  status?: string;
  category?: string;
  search?: string;
  reporterId?: string;
  upvotedBy?: string;
}

interface ApiOptions extends RequestInit {
  token?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { token, ...fetchOptions } = options;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        useAuthStore.getState().logout();
      }
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || 'Request failed');
    }

    return response.json();
  }

  // Auth endpoints
  async register(data: { email: string; password: string; name: string }) {
    return this.request<{ user: any; token: string }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }) {
    return this.request<{ user: any; token: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMe(token: string) {
    return this.request<{ user: any }>('/api/auth/me', { token });
  }

  async updateProfile(token: string, data: { name?: string; department?: string; phone?: string }) {
    return this.request<{ user: any }>('/api/auth/me', {
      method: 'PATCH',
      token,
      body: JSON.stringify(data),
    });
  }

  async changePassword(token: string, data: { oldPassword: string; newPassword: string }) {
    return this.request<{ message: string }>('/api/auth/change-password', {
      method: 'POST',
      token,
      body: JSON.stringify(data),
    });
  }

  // Issues endpoints
  async getIssues(filters?: IssueFilters): Promise<PaginatedResponse<Issue>> {
    const params: Record<string, string> = {};
    if (filters?.page) params.page = String(filters.page);
    if (filters?.limit) params.limit = String(filters.limit);
    if (filters?.status) params.status = filters.status;
    if (filters?.category) params.category = filters.category;
    if (filters?.search) params.search = filters.search;
    
    const queryString = Object.keys(params).length > 0 
      ? '?' + new URLSearchParams(params).toString() 
      : '';
    const result = await this.request<{ issues: Issue[]; pagination: any }>(`/api/issues${queryString}`);
    return {
      data: result.issues,
      pagination: result.pagination,
    };
  }

  async getIssue(id: string): Promise<Issue> {
    const result = await this.request<{ issue: Issue }>(`/api/issues/${id}`);
    return result.issue;
  }

  async getNearbyIssues(lat: number, lng: number, radius?: number): Promise<Issue[]> {
    const params = new URLSearchParams({
      lat: String(lat),
      lng: String(lng),
      ...(radius && { radius: String(radius) }),
    });
    const result = await this.request<{ issues: Issue[] }>(`/api/issues/nearby?${params}`);
    return result.issues;
  }

  async createIssue(data: {
    title: string;
    description?: string;
    category: string;
    priority?: string;
    photoUrl: string;
    latitude: number;
    longitude: number;
    building?: string;
    floor?: string;
    room?: string;
    locationDescription?: string;
  }): Promise<Issue> {
    const token = useAuthStore.getState().token;
    
    const result = await this.request<{ issue: Issue }>('/api/issues', {
      method: 'POST',
      body: JSON.stringify(data),
      token: token || undefined,
    });
    return result.issue;
  }

  async updateIssue(id: string, data: any, token: string): Promise<Issue> {
    const result = await this.request<{ issue: Issue }>(`/api/issues/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
      token,
    });
    return result.issue;
  }

  async updateIssueStatus(id: string, status: string, assigneeId?: string): Promise<Issue> {
    const token = useAuthStore.getState().token;
    
    const result = await this.request<{ issue: Issue }>(`/api/issues/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, assigneeId }),
      token: token || undefined,
    });
    return result.issue;
  }

  async upvoteIssue(id: string): Promise<{ upvoted: boolean }> {
    const token = useAuthStore.getState().token;
    
    return this.request<{ upvoted: boolean }>(`/api/issues/${id}/upvote`, {
      method: 'POST',
      body: JSON.stringify({}),
      token: token || undefined,
    });
  }

  async addComment(id: string, content: string): Promise<Comment> {
    const token = useAuthStore.getState().token;
    
    const result = await this.request<{ comment: Comment }>(`/api/issues/${id}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
      token: token || undefined,
    });
    return result.comment;
  }

  // Stats endpoints
  async getStats(): Promise<Stats> {
    return this.request<Stats>('/api/stats/dashboard');
  }

  async getHeatmap(): Promise<HeatmapData> {
    return this.request<HeatmapData>('/api/stats/heatmap');
  }

  async getAdminStats(): Promise<AdminStats> {
    const token = useAuthStore.getState().token;
    
    return this.request<AdminStats>('/api/stats/admin', { token: token || undefined });
  }

  // Upload
  async uploadImage(file: File, token: string): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/upload/image`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    return response.json();
  }
}

export const api = new ApiClient(API_BASE_URL);
