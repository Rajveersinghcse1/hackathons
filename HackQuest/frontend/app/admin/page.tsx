'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area
} from 'recharts';
import { 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  TrendingUp,
  Users,
  Building,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Trophy,
  AlertOctagon
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const COLORS = ['#16a34a', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

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

export default function AdminDashboardPage() {
  const router = useRouter();
  const { token, user, isAuthenticated } = useAuthStore();

  // Redirect if not admin
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else if (user?.role !== 'ADMIN') {
      router.push('/issues');
    }
  }, [isAuthenticated, user, router]);

  const { data: publicStats, isLoading: loadingPublic } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.getStats(),
  });

  const { data: adminStats, isLoading: loadingAdmin } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => api.getAdminStats(),
    enabled: !!token && user?.role === 'ADMIN',
  });

  if (!isAuthenticated || user?.role !== 'ADMIN') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent"></div>
          <p className="text-slate-500">Verifying access...</p>
        </div>
      </div>
    );
  }

  const isLoading = loadingPublic || loadingAdmin;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Sarpanch Dashboard</h1>
          <p className="text-slate-500 dark:text-slate-400">Overview of village development status</p>
        </div>

        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-8"
        >
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { 
                label: 'Total Issues', 
                value: publicStats?.totalIssues || 0, 
                icon: Building, 
                color: 'text-emerald-600', 
                bg: 'bg-emerald-100 dark:bg-emerald-900/30',
                trend: '+12% from last month'
              },
              { 
                label: 'Open Issues', 
                value: publicStats?.statusCounts?.OPEN || 0, 
                icon: AlertTriangle, 
                color: 'text-orange-600', 
                bg: 'bg-orange-100 dark:bg-orange-900/30',
                trend: '-5% from last month'
              },
              { 
                label: 'Resolved', 
                value: publicStats?.statusCounts?.RESOLVED || 0, 
                icon: CheckCircle, 
                color: 'text-green-600', 
                bg: 'bg-green-100 dark:bg-green-900/30',
                trend: '+8% from last month'
              },
              { 
                label: 'Avg Resolution', 
                value: '24h', 
                icon: Clock, 
                color: 'text-purple-600', 
                bg: 'bg-purple-100 dark:bg-purple-900/30',
                trend: '-2h from last month'
              },
            ].map((stat, index) => (
              <motion.div key={index} variants={item}>
                <Card className="border-none shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`h-12 w-12 rounded-xl ${stat.bg} flex items-center justify-center`}>
                        <stat.icon className={`h-6 w-6 ${stat.color}`} />
                      </div>
                      {stat.trend.includes('+') ? (
                        <Badge variant="outline" className="text-green-600 bg-green-50 border-green-200">
                          <ArrowUpRight className="h-3 w-3 mr-1" />
                          {stat.trend.split(' ')[0]}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-red-600 bg-red-50 border-red-200">
                          <ArrowDownRight className="h-3 w-3 mr-1" />
                          {stat.trend.split(' ')[0]}
                        </Badge>
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
                      {isLoading ? (
                        <Skeleton className="h-8 w-24 mt-1" />
                      ) : (
                        <h3 className="text-3xl font-bold text-slate-900 dark:text-white">{stat.value}</h3>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Alert Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div variants={item}>
              <Card className="border-l-4 border-l-red-500 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-red-700 flex items-center gap-2">
                    <AlertOctagon className="h-5 w-5" />
                    Escalated Issues
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-12 w-16" />
                  ) : (
                    <p className="text-4xl font-bold text-red-700">
                      {adminStats?.escalatedIssues || 0}
                    </p>
                  )}
                  <p className="text-sm text-red-600 mt-1">Require immediate attention</p>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card className="border-l-4 border-l-orange-500 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-orange-700 flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Overdue Issues
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-12 w-16" />
                  ) : (
                    <p className="text-4xl font-bold text-orange-700">
                      {adminStats?.overdueIssues || 0}
                    </p>
                  )}
                  <p className="text-sm text-orange-600 mt-1">Open for more than 48 hours</p>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div variants={item}>
              <Card className="border-none shadow-sm">
                <CardHeader>
                  <CardTitle>Issues by Category</CardTitle>
                  <CardDescription>Distribution of reported problems</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px] w-full">
                    {isLoading ? (
                      <Skeleton className="h-full w-full" />
                    ) : (
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={Object.entries(publicStats?.categoryCounts || {}).map(([name, value]) => ({ name, value }))}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                          <XAxis 
                            dataKey="name" 
                            tick={{ fontSize: 12 }} 
                            tickFormatter={(val) => val.slice(0, 3)}
                            stroke="#94a3b8"
                          />
                          <YAxis stroke="#94a3b8" />
                          <Tooltip 
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            cursor={{ fill: '#f1f5f9' }}
                          />
                          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                            {Object.entries(publicStats?.categoryCounts || {}).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card className="border-none shadow-sm">
                <CardHeader>
                  <CardTitle>Status Distribution</CardTitle>
                  <CardDescription>Current state of all issues</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px] w-full">
                    {isLoading ? (
                      <Skeleton className="h-full w-full" />
                    ) : (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={Object.entries(publicStats?.statusCounts || {}).map(([name, value]) => ({ name, value }))}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {Object.entries(publicStats?.statusCounts || {}).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Staff Performance & Recent Issues */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Staff Performance */}
            <motion.div variants={item}>
              <Card className="border-none shadow-sm h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Staff Performance
                  </CardTitle>
                  <CardDescription>Issues resolved this month</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-4">
                      {[...Array(5)].map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {adminStats?.staffPerformance?.map((staff: any) => (
                        <div key={staff.id} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="h-8 w-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-medium text-sm">
                                {staff.name.charAt(0)}
                              </div>
                              <div>
                                <p className="font-medium text-sm">{staff.name}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className="text-sm font-medium">{staff.resolved}</span>
                              <span className="text-xs text-slate-500">/{staff.assigned}</span>
                            </div>
                          </div>
                          <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${staff.assigned > 0 ? (staff.resolved / staff.assigned) * 100 : 0}%` }}
                              transition={{ duration: 1, ease: "easeOut" }}
                              className="h-full bg-blue-600 rounded-full"
                            />
                          </div>
                        </div>
                      ))}
                      {(!adminStats?.staffPerformance || adminStats.staffPerformance.length === 0) && (
                        <div className="flex flex-col items-center justify-center py-8 text-slate-500">
                          <Users className="h-8 w-8 mb-2 opacity-20" />
                          <p>No staff data available</p>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Issues */}
            <motion.div variants={item}>
              <Card className="border-none shadow-sm h-full">
                <CardHeader>
                  <CardTitle>Recent Issues</CardTitle>
                  <CardDescription>Latest reported problems</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="space-y-4">
                      {[...Array(5)].map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {publicStats?.recentIssues?.map((issue: any) => (
                        <Link key={issue.id} href={`/issues/${issue.id}`}>
                          <div className="group flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors border border-transparent hover:border-slate-100 dark:hover:border-slate-800">
                            <div className="flex-1 min-w-0">
                              <p className="font-medium truncate group-hover:text-blue-600 transition-colors">{issue.title}</p>
                              <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                                <Building className="h-3 w-3" />
                                {issue.building}
                                <span>•</span>
                                {issue.category}
                              </p>
                            </div>
                            <Badge
                              variant="secondary"
                              className={
                                issue.status === 'OPEN' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                                issue.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                                'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                              }
                            >
                              {issue.status}
                            </Badge>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Leaderboard */}
          <motion.div variants={item}>
            <Card className="border-none shadow-sm bg-gradient-to-r from-slate-50 to-white dark:from-slate-900 dark:to-slate-950">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-yellow-500" />
                  Top Reporters
                </CardTitle>
                <CardDescription>Citizens who report the most issues</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {publicStats?.topReporters?.slice(0, 5).map((user: any, index: number) => (
                      <div
                        key={user.id}
                        className="flex items-center gap-3 p-4 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800"
                      >
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-inner ${
                          index === 0 ? 'bg-yellow-100 text-yellow-600' :
                          index === 1 ? 'bg-slate-100 text-slate-600' :
                          index === 2 ? 'bg-orange-100 text-orange-600' :
                          'bg-blue-50 text-blue-600'
                        }`}>
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-sm truncate w-24" title={user.name}>{user.name}</p>
                          <p className="text-xs text-slate-500">{user.issueCount} issues</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
