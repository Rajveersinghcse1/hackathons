'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Camera, 
  MapPin, 
  ThumbsUp, 
  MessageSquare,
  Search,
  Clock,
  AlertCircle,
  Filter
} from 'lucide-react';
import { formatRelativeTime, getStatusColor } from '@/lib/utils';

const CATEGORIES = [
  'ROADS',
  'WATER', 
  'ELECTRICITY',
  'SANITATION',
  'AGRICULTURE',
  'HEALTH',
  'EDUCATION',
  'OTHER',
];

const STATUSES = [
  'OPEN',
  'ACKNOWLEDGED',
  'IN_PROGRESS',
  'RESOLVED',
  'CLOSED',
  'ESCALATED',
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export default function IssuesPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ['issues', { page, search, category, status }],
    queryFn: () => {
      return api.getIssues({
        page,
        search: search || undefined,
        category: category && category !== 'all' ? category : undefined,
        status: status && status !== 'all' ? status : undefined,
      });
    },
  });

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-emerald-200/40 rounded-full blur-3xl" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-green-200/40 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <div className="sticky top-0 z-20 bg-white/70 backdrop-blur-xl border-b border-white/50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Village Issues</h1>
              <p className="text-sm text-slate-500">Track and manage reported problems in your area</p>
            </div>
            <Link href="/report">
              <Button className="gap-2 shadow-lg shadow-green-600/20 bg-green-600 hover:bg-green-700 text-white rounded-xl">
                <Camera className="h-4 w-4" />
                Report New Issue
              </Button>
            </Link>
          </div>

          {/* Filters */}
          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search issues..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 bg-white/50 border-white/50 focus:bg-white transition-all rounded-xl"
              />
            </div>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger className="w-full sm:w-40 bg-white/50 border-white/50 focus:bg-white rounded-xl">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    <span className="flex items-center gap-2">
                      {cat.replace('_', ' ')}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-full sm:w-40 bg-white/50 border-white/50 focus:bg-white rounded-xl">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {STATUSES.map((stat) => (
                  <SelectItem key={stat} value={stat}>
                    {stat.replace('_', ' ')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 relative z-10">
        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="overflow-hidden bg-white/40 border-white/60">
                <Skeleton className="h-48 w-full bg-slate-200/50" />
                <CardContent className="p-4">
                  <Skeleton className="h-4 w-2/3 mb-4 bg-slate-200/50" />
                  <Skeleton className="h-4 w-1/2 bg-slate-200/50" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-20 bg-white/40 backdrop-blur-md rounded-3xl border border-white/50">
            <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 mb-4">
              <AlertCircle className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-medium text-slate-900">Failed to load issues</h3>
            <p className="text-slate-500 mt-2">Please try again later</p>
          </div>
        ) : (
          <>
            <motion.div 
              variants={container}
              initial="hidden"
              animate="show"
              className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
            >
              <AnimatePresence mode='popLayout'>
                {data?.data.map((issue: any) => (
                  <motion.div key={issue.id} variants={item} layout>
                    <Link href={`/issues/${issue.id}`}>
                      <Card className="group h-full overflow-hidden bg-white/60 backdrop-blur-sm border-white/60 hover:border-green-300 hover:shadow-xl hover:shadow-green-900/5 transition-all duration-300 hover:-translate-y-1 rounded-2xl">
                        <div className="relative h-48 bg-slate-100 overflow-hidden">
                          {issue.photoUrl ? (
                            <img
                              src={issue.photoUrl}
                              alt={issue.title}
                              className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                            />
                          ) : (
                            <div className="flex h-full items-center justify-center bg-slate-50 text-slate-300">
                              <Camera className="h-12 w-12 opacity-50" />
                            </div>
                          )}
                          <div className="absolute top-3 right-3">
                            <Badge className={`${getStatusColor(issue.status)} shadow-sm backdrop-blur-md bg-opacity-90`}>
                              {issue.status.replace('_', ' ')}
                            </Badge>
                          </div>
                          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent p-4 pt-12">
                            <div className="flex items-center gap-2 text-white text-sm font-medium">
                              <MapPin className="h-3.5 w-3.5 text-blue-400" />
                              <span className="truncate">{issue.building}</span>
                            </div>
                          </div>
                        </div>
                        <CardContent className="p-5">
                          <div className="flex items-start justify-between gap-2 mb-3">
                            <Badge variant="outline" className="text-xs font-medium border-slate-300 text-slate-600 bg-slate-50/50">
                              {issue.category}
                            </Badge>
                            <span className="text-xs text-slate-400 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatRelativeTime(issue.createdAt)}
                            </span>
                          </div>
                          <h3 className="font-bold text-lg mb-2 line-clamp-1 text-slate-800 group-hover:text-blue-600 transition-colors">
                            {issue.title}
                          </h3>
                          <p className="text-sm text-slate-500 line-clamp-2 mb-5 leading-relaxed">
                            {issue.description}
                          </p>
                          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                            <div className="flex items-center gap-4 text-sm text-slate-500">
                              <span className="flex items-center gap-1.5 hover:text-blue-600 transition-colors">
                                <ThumbsUp className="h-4 w-4" />
                                {issue._count?.upvotes || 0}
                              </span>
                              <span className="flex items-center gap-1.5 hover:text-blue-600 transition-colors">
                                <MessageSquare className="h-4 w-4" />
                                {issue._count?.comments || 0}
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>

            {/* Pagination */}
            {data?.pagination && data.pagination.totalPages > 1 && (
              <div className="mt-12 flex justify-center gap-2">
                <Button
                  variant="outline"
                  disabled={page === 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="w-24 bg-white/50 border-white/50 hover:bg-white"
                >
                  Previous
                </Button>
                <div className="flex items-center gap-2 px-4 text-sm font-medium text-slate-600 bg-white/30 rounded-lg border border-white/30">
                  Page {page} of {data.pagination.totalPages}
                </div>
                <Button
                  variant="outline"
                  disabled={page === data.pagination.totalPages}
                  onClick={() => setPage((p) => Math.min(data.pagination.totalPages, p + 1))}
                  className="w-24 bg-white/50 border-white/50 hover:bg-white"
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
