'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useToast } from '@/components/ui/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Clock, 
  ThumbsUp,
  MessageSquare,
  Send,
  User,
  History,
  ExternalLink,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Upload,
  X,
  Loader2,
  Shield
} from 'lucide-react';
import { formatDate, formatRelativeTime, getStatusColor, getPriorityColor, getCategoryIcon } from '@/lib/utils';

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

export default function IssueDetailPage() {
  const params = useParams();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { token, isAuthenticated, user } = useAuthStore();
  const [comment, setComment] = useState('');
  const [isResolving, setIsResolving] = useState(false);
  const [resolutionFile, setResolutionFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const issueId = params.id as string;

  const { data, isLoading, error } = useQuery({
    queryKey: ['issue', issueId],
    queryFn: () => api.getIssue(issueId),
    enabled: !!issueId,
  });

  const updateStatusMutation = useMutation({
    mutationFn: async (data: { status: string; resolvedPhotoUrl?: string }) => {
      if (!token) throw new Error('Not authenticated');
      return api.updateIssue(issueId, data, token);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue', issueId] });
      setIsResolving(false);
      setResolutionFile(null);
      toast({
        title: 'Status updated',
        description: 'The issue status has been updated successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to update status. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const handleStatusChange = (newStatus: string) => {
    if (newStatus === 'RESOLVED') {
      setIsResolving(true);
    } else {
      updateStatusMutation.mutate({ status: newStatus });
    }
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolutionFile || !token) return;

    setIsUploading(true);
    try {
      const { url } = await api.uploadImage(resolutionFile, token);
      updateStatusMutation.mutate({ 
        status: 'RESOLVED', 
        resolvedPhotoUrl: url 
      });
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: 'Failed to upload resolution photo.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const upvoteMutation = useMutation({
    mutationFn: () => api.upvoteIssue(issueId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue', issueId] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to upvote. Please login first.',
        variant: 'destructive',
      });
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content: string) => api.addComment(issueId, content),
    onSuccess: () => {
      setComment('');
      queryClient.invalidateQueries({ queryKey: ['issue', issueId] });
      toast({
        title: 'Comment added',
        description: 'Your comment has been posted.',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to post comment.',
        variant: 'destructive',
      });
    },
  });

  const handleUpvote = () => {
    if (!isAuthenticated) {
      toast({
        title: 'Login required',
        description: 'Please login to upvote.',
        variant: 'destructive',
      });
      return;
    }
    upvoteMutation.mutate();
  };

  const handleComment = () => {
    if (!isAuthenticated) {
      toast({
        title: 'Login required',
        description: 'Please login to comment.',
        variant: 'destructive',
      });
      return;
    }
    if (!comment.trim()) return;
    commentMutation.mutate(comment);
  };

  const issue = data;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <div className="container mx-auto px-4 py-8 max-w-5xl">
          <Skeleton className="h-8 w-32 mb-6" />
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <Skeleton className="h-[400px] w-full rounded-xl" />
              <Skeleton className="h-48 w-full rounded-xl" />
            </div>
            <div className="space-y-6">
              <Skeleton className="h-64 w-full rounded-xl" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <Card className="text-center p-8 max-w-md w-full border-none shadow-lg">
          <div className="flex justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <h2 className="text-xl font-bold mb-2">Issue not found</h2>
          <p className="text-slate-500 mb-6">The issue you are looking for does not exist or has been removed.</p>
          <Link href="/issues">
            <Button className="w-full">Back to Issues</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
        >
          <motion.div variants={item} className="mb-6">
            <Link href="/issues" className="inline-flex items-center text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Issues
            </Link>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Photo */}
              <motion.div variants={item}>
                <div className="relative aspect-video rounded-xl overflow-hidden shadow-md group">
                  <img
                    src={issue.photoUrl}
                    alt={issue.title}
                    className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="absolute bottom-4 left-4 right-4 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <p className="text-sm font-medium flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {[issue.building, issue.floor, issue.room].filter(Boolean).join(', ')}
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Title & Info */}
              <motion.div variants={item}>
                <Card className="border-none shadow-sm overflow-hidden">
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-3">
                          <Badge 
                            variant="secondary" 
                            className={`${getPriorityColor(issue.priority)} bg-opacity-10 border-none`}
                          >
                            {issue.priority} Priority
                          </Badge>
                          <Badge 
                            variant="outline" 
                            className={`${getStatusColor(issue.status)} border-current bg-transparent`}
                          >
                            {issue.status.replace('_', ' ')}
                          </Badge>
                        </div>
                        <CardTitle className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                          {issue.title}
                        </CardTitle>
                      </div>
                      <Button
                        variant={issue.isUpvoted ? "default" : "outline"}
                        size="sm"
                        onClick={handleUpvote}
                        disabled={upvoteMutation.isPending}
                        className={`gap-2 transition-all ${issue.isUpvoted ? 'bg-green-600 hover:bg-green-700' : ''}`}
                      >
                        <ThumbsUp className={`h-4 w-4 ${issue.isUpvoted ? 'fill-current' : ''}`} />
                        {issue._count?.upvotes || 0}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Process Tracker */}
                    <div className="py-4 px-2">
                      <div className="relative">
                        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-100 dark:bg-slate-800 -translate-y-1/2 rounded-full"></div>
                        <div 
                          className={`absolute top-1/2 left-0 h-1 -translate-y-1/2 rounded-full transition-all duration-500 ${
                            issue.status === 'RESOLVED' ? 'bg-green-500 w-full' :
                            issue.status === 'IN_PROGRESS' ? 'bg-amber-500 w-2/3' :
                            issue.status === 'OPEN' ? 'bg-blue-500 w-1/3' : 'bg-slate-300 w-0'
                          }`}
                        ></div>
                        
                        <div className="relative flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                          <div className="flex flex-col items-center gap-2">
                            <div className={`w-3 h-3 rounded-full border-2 bg-white dark:bg-slate-950 ${['OPEN', 'IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-blue-500 bg-blue-500' : 'border-slate-300 dark:border-slate-700'}`}></div>
                            <span>Reported</span>
                          </div>
                          <div className="flex flex-col items-center gap-2">
                            <div className={`w-3 h-3 rounded-full border-2 bg-white dark:bg-slate-950 ${['IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-amber-500 bg-amber-500' : 'border-slate-300 dark:border-slate-700'}`}></div>
                            <span>In Progress</span>
                          </div>
                          <div className="flex flex-col items-center gap-2">
                            <div className={`w-3 h-3 rounded-full border-2 bg-white dark:bg-slate-950 ${issue.status === 'RESOLVED' ? 'border-green-500 bg-green-500' : 'border-slate-300 dark:border-slate-700'}`}></div>
                            <span>Resolved</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="prose dark:prose-invert max-w-none">
                      <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                        {issue.description || "No description provided."}
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-100 dark:border-slate-800">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600">
                          {getCategoryIcon(issue.category)}
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase font-semibold tracking-wider">Category</p>
                          <p className="font-medium text-slate-900 dark:text-white">{issue.category.replace('_', ' ')}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600">
                          <User className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase font-semibold tracking-wider">Reported By</p>
                          <p className="font-medium text-slate-900 dark:text-white">{issue.reporter.name}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600">
                          <MapPin className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase font-semibold tracking-wider">Location</p>
                          <p className="font-medium text-slate-900 dark:text-white truncate" title={[issue.building, issue.floor, issue.room].filter(Boolean).join(', ')}>
                            {[issue.building, issue.floor, issue.room].filter(Boolean).join(', ')}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600">
                          <Clock className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 uppercase font-semibold tracking-wider">Reported</p>
                          <p className="font-medium text-slate-900 dark:text-white">{formatRelativeTime(issue.createdAt)}</p>
                        </div>
                      </div>
                    </div>

                    {/* Map link */}
                    <div className="flex justify-end">
                      <a
                        href={`https://www.openstreetmap.org/?mlat=${issue.latitude}&mlon=${issue.longitude}&zoom=18`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-sm font-medium text-green-600 hover:text-green-700 hover:underline transition-colors"
                      >
                        <MapPin className="h-4 w-4" />
                        View exact location on OpenStreetMap
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Comments */}
              <motion.div variants={item}>
                <Card className="border-none shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <MessageSquare className="h-5 w-5 text-slate-500" />
                      Comments 
                      <Badge variant="secondary" className="ml-2">{issue.comments?.length || 0}</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Add comment */}
                    {isAuthenticated ? (
                      <div className="flex gap-4">
                        <Avatar className="h-10 w-10 border-2 border-white shadow-sm">
                          <AvatarFallback className="bg-blue-100 text-blue-600">
                            {user?.name?.charAt(0).toUpperCase() || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 space-y-2">
                          <Textarea
                            placeholder="Add a comment..."
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            rows={3}
                            className="resize-none bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800 focus:ring-blue-500"
                          />
                          <div className="flex justify-end">
                            <Button
                              size="sm"
                              onClick={handleComment}
                              disabled={commentMutation.isPending || !comment.trim()}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              {commentMutation.isPending ? (
                                <span className="animate-spin mr-2">⏳</span>
                              ) : (
                                <Send className="h-3 w-3 mr-2" />
                              )}
                              Post Comment
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg text-center">
                        <p className="text-sm text-slate-500 mb-2">Please login to join the discussion</p>
                        <Link href="/login">
                          <Button variant="outline" size="sm">Login</Button>
                        </Link>
                      </div>
                    )}

                    {/* Comments list */}
                    <div className="space-y-6">
                      {(!issue.comments || issue.comments.length === 0) ? (
                        <div className="text-center py-8 text-slate-400">
                          <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-20" />
                          <p>No comments yet. Be the first to share your thoughts!</p>
                        </div>
                      ) : (
                        issue.comments.map((c: any) => (
                          <div key={c.id} className="flex gap-4 group">
                            <Avatar className="h-10 w-10 border border-slate-100 shadow-sm">
                              <AvatarFallback className="bg-slate-100 text-slate-600">
                                {c.user.name.charAt(0).toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-2xl rounded-tl-none">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center gap-2">
                                    <span className="font-semibold text-sm text-slate-900 dark:text-white">{c.user.name}</span>
                                    {c.user.role === 'ADMIN' && (
                                      <Badge variant="secondary" className="text-[10px] h-5 px-1.5 bg-blue-100 text-blue-700">
                                        ADMIN
                                      </Badge>
                                    )}
                                  </div>
                                  <span className="text-xs text-slate-400">
                                    {formatRelativeTime(c.createdAt)}
                                  </span>
                                </div>
                                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{c.content}</p>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Admin Controls */}
              {(user?.role === 'ADMIN' || user?.role === 'STAFF') && (
                <motion.div variants={item}>
                  <Card className="border-none shadow-sm bg-slate-900 text-white">
                    <CardHeader className="pb-3 border-b border-slate-800">
                      <CardTitle className="flex items-center gap-2 text-base font-semibold">
                        <Shield className="h-5 w-5 text-blue-400" />
                        Admin Controls
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-4">
                      <div className="space-y-2">
                        <Label className="text-slate-300">Status</Label>
                        <Select 
                          defaultValue={issue.status} 
                          onValueChange={handleStatusChange}
                          disabled={updateStatusMutation.isPending}
                        >
                          <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="OPEN">Open</SelectItem>
                            <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                            <SelectItem value="RESOLVED">Resolved</SelectItem>
                            <SelectItem value="REJECTED">Rejected</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              <motion.div variants={item}>
                <Card className="border-none shadow-sm sticky top-24">
                  <CardHeader className="pb-3 border-b border-slate-100 dark:border-slate-800">
                    <CardTitle className="flex items-center gap-2 text-base font-semibold">
                      <History className="h-5 w-5 text-slate-500" />
                      Activity Log
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {(!issue.activityLogs || issue.activityLogs.length === 0) ? (
                      <p className="text-slate-500 text-sm text-center py-4">No activity recorded yet</p>
                    ) : (
                      <div className="relative pl-4 border-l-2 border-slate-100 dark:border-slate-800 space-y-6">
                        {issue.activityLogs.map((log: any) => (
                          <div key={log.id} className="relative">
                            <div className="absolute -left-[21px] top-1.5 h-3 w-3 rounded-full border-2 border-white dark:border-slate-950 bg-blue-500 shadow-sm" />
                            <div className="text-sm">
                              <p className="text-slate-900 dark:text-white font-medium">
                                {log.user.name}
                              </p>
                              <p className="text-slate-500 text-xs mb-1">
                                {log.action.toLowerCase().replace('_', ' ')}
                              </p>
                              <p className="text-[10px] text-slate-400 uppercase tracking-wide">
                                {formatRelativeTime(log.createdAt)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              {/* Resolution Photo */}
              {issue.resolvedPhotoUrl && (
                <motion.div variants={item}>
                  <Card className="border-none shadow-sm overflow-hidden bg-green-50 dark:bg-green-900/10 border-green-100 dark:border-green-900/30">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base text-green-700 dark:text-green-400 flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5" />
                        Resolution Proof
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="relative aspect-video m-4 mt-0 rounded-lg overflow-hidden shadow-sm">
                        <img
                          src={issue.resolvedPhotoUrl}
                          alt="Resolution proof"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
              
              {issue.assignee && (
                <motion.div variants={item}>
                  <Card className="border-none shadow-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Assigned To</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10 border border-slate-100">
                          <AvatarFallback className="bg-slate-100 text-slate-600">
                            {issue.assignee.name.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-white">{issue.assignee.name}</p>
                          <p className="text-xs text-slate-500">{issue.assignee.role}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Resolution Modal */}
      {isResolving && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Resolve Issue</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleResolveSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label>Resolution Proof (Photo)</Label>
                  <div className="border-2 border-dashed border-slate-200 rounded-lg p-6 text-center hover:bg-slate-50 transition-colors cursor-pointer relative">
                    <input 
                      type="file" 
                      accept="image/*"
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      onChange={(e) => setResolutionFile(e.target.files?.[0] || null)}
                      required
                    />
                    {resolutionFile ? (
                      <div className="flex items-center justify-center gap-2 text-green-600">
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="text-sm font-medium truncate max-w-[200px]">{resolutionFile.name}</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-slate-500">
                        <Upload className="h-8 w-8 text-slate-400" />
                        <span className="text-sm">Click to upload photo</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => {
                    setIsResolving(false);
                    setResolutionFile(null);
                  }}>Cancel</Button>
                  <Button type="submit" disabled={isUploading || !resolutionFile}>
                    {isUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Resolve Issue
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
