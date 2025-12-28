"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type Stats, type HeatmapData, type AdminStats } from "@/lib/api";

export function useStats() {
  return useQuery<Stats>({
    queryKey: ["stats"],
    queryFn: () => api.getStats(),
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });
}

export function useHeatmapData() {
  return useQuery<HeatmapData>({
    queryKey: ["heatmap"],
    queryFn: () => api.getHeatmap(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useAdminStats() {
  return useQuery<AdminStats>({
    queryKey: ["admin", "stats"],
    queryFn: () => api.getAdminStats(),
    staleTime: 1000 * 60, // 1 minute
  });
}
