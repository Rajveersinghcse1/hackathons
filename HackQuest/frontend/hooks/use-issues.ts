"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Issue, type IssueFilters, type PaginatedResponse } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

export function useIssues(filters: IssueFilters = {}) {
  return useQuery<PaginatedResponse<Issue>>({
    queryKey: ["issues", filters],
    queryFn: () => api.getIssues(filters),
    staleTime: 1000 * 60, // 1 minute
  });
}

export function useIssue(id: string) {
  return useQuery<Issue>({
    queryKey: ["issue", id],
    queryFn: () => api.getIssue(id),
    enabled: !!id,
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useNearbyIssues(lat: number, lng: number, radius?: number) {
  return useQuery<Issue[]>({
    queryKey: ["issues", "nearby", lat, lng, radius],
    queryFn: () => api.getNearbyIssues(lat, lng, radius),
    enabled: !!lat && !!lng,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export interface CreateIssueData {
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
}

export function useCreateIssue() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreateIssueData) => api.createIssue(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["issues"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      toast({
        title: "Issue Reported",
        description: "Your issue has been submitted successfully!",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to submit issue",
        variant: "destructive",
      });
    },
  });
}

export function useUpvoteIssue() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (issueId: string) => api.upvoteIssue(issueId),
    onSuccess: (_, issueId) => {
      queryClient.invalidateQueries({ queryKey: ["issue", issueId] });
      queryClient.invalidateQueries({ queryKey: ["issues"] });
      toast({
        title: "Upvoted!",
        description: "Your support has been recorded.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to upvote",
        variant: "destructive",
      });
    },
  });
}

export function useAddComment() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ issueId, content }: { issueId: string; content: string }) =>
      api.addComment(issueId, content),
    onSuccess: (_, { issueId }) => {
      queryClient.invalidateQueries({ queryKey: ["issue", issueId] });
      toast({
        title: "Comment Added",
        description: "Your comment has been posted.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to add comment",
        variant: "destructive",
      });
    },
  });
}

export function useUpdateIssueStatus() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      issueId,
      status,
      assigneeId,
    }: {
      issueId: string;
      status: string;
      assigneeId?: string;
    }) => api.updateIssueStatus(issueId, status, assigneeId),
    onSuccess: (_, { issueId }) => {
      queryClient.invalidateQueries({ queryKey: ["issue", issueId] });
      queryClient.invalidateQueries({ queryKey: ["issues"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      toast({
        title: "Status Updated",
        description: "Issue status has been updated.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update status",
        variant: "destructive",
      });
    },
  });
}
