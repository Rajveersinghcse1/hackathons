'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { api, User, Issue } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, MapPin, Calendar, ThumbsUp, MessageSquare, Clock, CheckCircle2, AlertTriangle, Edit2, X } from 'lucide-react';
import { formatRelativeTime, getStatusColor, getStatusIcon } from '@/lib/utils';
import Link from 'next/link';
import { useToast } from '@/components/ui/use-toast';

interface UserProfile extends User {
  phone?: string;
  department?: string;
  _count?: {
    reportedIssues: number;
    upvotes: number;
  };
}

export default function ProfilePage() {
  const router = useRouter();
  const { toast } = useToast();
  const { user: authUser, isAuthenticated, logout } = useAuthStore();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [myIssues, setMyIssues] = useState<Issue[]>([]);
  const [upvotedIssues, setUpvotedIssues] = useState<Issue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Edit Profile State
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    department: '',
    phone: ''
  });
  const [isSaving, setIsSaving] = useState(false);

  // Change Password State
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const token = useAuthStore.getState().token;
        if (!token) return;

        // Fetch full profile
        const { user } = await api.getMe(token);
        setProfile(user);
        setEditForm({
          name: user.name || '',
          department: user.department || '',
          phone: user.phone || ''
        });

        // Fetch my issues
        const { data: myIssuesData } = await api.getIssues({ reporterId: user.id, limit: 50 });
        setMyIssues(myIssuesData);

        // Fetch upvoted issues
        const { data: upvotedData } = await api.getIssues({ upvotedBy: user.id, limit: 50 });
        setUpvotedIssues(upvotedData);
      } catch (error) {
        console.error('Failed to fetch profile:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, router]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const token = useAuthStore.getState().token;
      if (!token) return;

      const { user } = await api.updateProfile(token, editForm);
      setProfile(prev => prev ? { ...prev, ...user } : user);
      setIsEditing(false);
      toast({
        title: "Profile updated",
        description: "Your profile information has been updated successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast({
        title: "Error",
        description: "New passwords do not match.",
        variant: "destructive"
      });
      return;
    }

    setIsSaving(true);
    try {
      const token = useAuthStore.getState().token;
      if (!token) return;

      await api.changePassword(token, {
        oldPassword: passwordForm.oldPassword,
        newPassword: passwordForm.newPassword
      });
      
      setIsChangingPassword(false);
      setPasswordForm({ oldPassword: '', newPassword: '', confirmPassword: '' });
      toast({
        title: "Success",
        description: "Password changed successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to change password. Please check your old password.",
        variant: "destructive"
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="min-h-screen bg-slate-50 py-8 relative">
      {/* Edit Profile Modal Overlay */}
      {isEditing && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-all duration-200">
          <Card className="w-full max-w-md bg-white shadow-2xl animate-in fade-in zoom-in duration-200 border-none">
            <CardHeader className="flex flex-row items-center justify-between border-b pb-4">
              <CardTitle className="text-xl">Edit Profile</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-slate-100" onClick={() => setIsEditing(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input 
                    id="name" 
                    value={editForm.name} 
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    required 
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Input 
                    id="department" 
                    value={editForm.department} 
                    onChange={(e) => setEditForm({...editForm, department: e.target.value})}
                    placeholder="e.g. Engineering, HR"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input 
                    id="phone" 
                    value={editForm.phone} 
                    onChange={(e) => setEditForm({...editForm, phone: e.target.value})}
                    placeholder="+91..."
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>Cancel</Button>
                  <Button type="submit" disabled={isSaving}>
                    {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Change Password Modal Overlay */}
      {isChangingPassword && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-all duration-200">
          <Card className="w-full max-w-md bg-white shadow-2xl animate-in fade-in zoom-in duration-200 border-none">
            <CardHeader className="flex flex-row items-center justify-between border-b pb-4">
              <CardTitle className="text-xl">Change Password</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-slate-100" onClick={() => setIsChangingPassword(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="oldPassword">Current Password</Label>
                  <Input 
                    id="oldPassword" 
                    type="password"
                    value={passwordForm.oldPassword} 
                    onChange={(e) => setPasswordForm({...passwordForm, oldPassword: e.target.value})}
                    required 
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input 
                    id="newPassword" 
                    type="password"
                    value={passwordForm.newPassword} 
                    onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                    required 
                    minLength={8}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input 
                    id="confirmPassword" 
                    type="password"
                    value={passwordForm.confirmPassword} 
                    onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                    required 
                    minLength={8}
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsChangingPassword(false)}>Cancel</Button>
                  <Button type="submit" disabled={isSaving}>
                    {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Update Password
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="container mx-auto px-4 max-w-5xl">
        
        {/* Header Profile Card */}
        <Card className="mb-8 border-none shadow-xl bg-white overflow-hidden">
          <div className="h-40 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          </div>
          <CardContent className="relative pt-0 pb-8 px-8">
            <div className="flex flex-col md:flex-row items-start md:items-end -mt-16 mb-8 gap-6">
              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full opacity-75 group-hover:opacity-100 transition duration-200 blur"></div>
                <Avatar className="h-32 w-32 border-4 border-white shadow-2xl relative">
                  <AvatarImage src={profile.avatarUrl} className="object-cover" />
                  <AvatarFallback className="text-4xl bg-slate-100 text-slate-600 font-bold">
                    {profile.name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className="absolute bottom-2 right-2 bg-green-500 h-5 w-5 rounded-full border-4 border-white"></div>
              </div>
              
              <div className="flex-1 pt-16 md:pt-0">
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-3xl font-bold text-slate-900">{profile.name}</h1>
                  <Badge variant="secondary" className="uppercase tracking-wider text-[10px] font-bold bg-blue-50 text-blue-700 border-blue-100">
                    {profile.role}
                  </Badge>
                </div>
                
                <div className="flex flex-wrap gap-4 mt-3 text-slate-600">
                  {profile.department && (
                    <span className="flex items-center gap-1.5 text-sm font-medium bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
                      <MapPin className="h-3.5 w-3.5 text-slate-400" />
                      {profile.department}
                    </span>
                  )}
                  <span className="flex items-center gap-1.5 text-sm font-medium bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    Joined {new Date(profile.createdAt).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                  </span>
                  {profile.phone && (
                    <span className="flex items-center gap-1.5 text-sm font-medium bg-slate-50 px-3 py-1 rounded-full border border-slate-100">
                      <MessageSquare className="h-3.5 w-3.5 text-slate-400" />
                      {profile.phone}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex gap-3 mt-4 md:mt-0 w-full md:w-auto">
                <Button variant="outline" className="flex-1 md:flex-none shadow-sm hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200 transition-all" onClick={() => setIsEditing(true)}>
                  <Edit2 className="mr-2 h-4 w-4" />
                  Edit Profile
                </Button>
                <Button variant="outline" className="flex-1 md:flex-none shadow-sm hover:bg-slate-50" onClick={() => setIsChangingPassword(true)}>
                  Change Password
                </Button>
                <Button variant="ghost" className="text-red-600 hover:bg-red-50 hover:text-red-700" onClick={() => logout()}>
                  Log Out
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t pt-8">
              <div className="group p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 cursor-default">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-slate-500 font-medium">Issues Reported</div>
                  <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-slate-900">{profile._count?.reportedIssues || 0}</div>
              </div>
              
              <div className="group p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-green-200 hover:shadow-md transition-all duration-200 cursor-default">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-slate-500 font-medium">Issues Resolved</div>
                  <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-600 group-hover:text-white transition-colors">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-slate-900">
                  {myIssues.filter(i => i.status === 'RESOLVED').length}
                </div>
              </div>
              
              <div className="group p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-amber-200 hover:shadow-md transition-all duration-200 cursor-default">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-slate-500 font-medium">Upvotes Given</div>
                  <div className="p-2 bg-amber-100 rounded-lg group-hover:bg-amber-600 group-hover:text-white transition-colors">
                    <ThumbsUp className="h-4 w-4" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-slate-900">{profile._count?.upvotes || 0}</div>
              </div>
              
              <div className="group p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-purple-200 hover:shadow-md transition-all duration-200 cursor-default">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-slate-500 font-medium">Impact Score</div>
                  <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-600 group-hover:text-white transition-colors">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-slate-900">
                  {myIssues.reduce((acc, issue) => acc + (issue._count?.upvotes || 0), 0)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="issues" className="space-y-8">
          <TabsList className="bg-white p-1.5 shadow-sm border rounded-xl w-full md:w-auto inline-flex h-auto">
            <TabsTrigger value="issues" className="px-6 py-2.5 rounded-lg data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 data-[state=active]:shadow-none transition-all">
              My Reports
            </TabsTrigger>
            <TabsTrigger value="upvoted" className="px-6 py-2.5 rounded-lg data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 data-[state=active]:shadow-none transition-all">
              Upvoted
            </TabsTrigger>
            <TabsTrigger value="activity" className="px-6 py-2.5 rounded-lg data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 data-[state=active]:shadow-none transition-all">
              Activity Log
            </TabsTrigger>
          </TabsList>

          <TabsContent value="issues" className="space-y-6">
            <div className="grid gap-4">
              {myIssues.length === 0 ? (
                <Card className="p-12 text-center text-slate-500">
                  <div className="flex justify-center mb-4">
                    <div className="p-4 bg-slate-100 rounded-full">
                      <AlertTriangle className="h-8 w-8 text-slate-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">No issues reported yet</h3>
                  <p className="mb-6">You haven't reported any infrastructure issues yet.</p>
                  <Link href="/report">
                    <Button>Report an Issue</Button>
                  </Link>
                </Card>
              ) : (
                myIssues.map((issue) => (
                  <Card key={issue.id} className="hover:shadow-md transition-shadow overflow-hidden">
                    <div className="flex flex-col md:flex-row">
                      <div className="w-full md:w-48 h-48 md:h-auto relative bg-slate-100">
                        {issue.photoUrl ? (
                          <img 
                            src={issue.photoUrl} 
                            alt={issue.title}
                            className="absolute inset-0 w-full h-full object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-slate-400">
                            <MapPin className="h-8 w-8" />
                          </div>
                        )}
                        <div className="absolute top-2 left-2">
                          <Badge className={getStatusColor(issue.status)}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(issue.status)}
                              {issue.status.replace('_', ' ')}
                            </span>
                          </Badge>
                        </div>
                      </div>
                      <div className="flex-1 p-6">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-slate-900 mb-1">
                              <Link href={`/issues/${issue.id}`} className="hover:text-blue-600 transition-colors">
                                {issue.title}
                              </Link>
                            </h3>
                            <div className="flex items-center gap-2 text-sm text-slate-500 mb-4">
                              <MapPin className="h-4 w-4" />
                              {issue.building} {issue.floor && `- Floor ${issue.floor}`}
                              <span className="mx-1">•</span>
                              <Calendar className="h-4 w-4" />
                              {formatRelativeTime(issue.createdAt)}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge variant="outline" className="font-mono">
                              #{issue.id.slice(0, 8)}
                            </Badge>
                          </div>
                        </div>

                        {/* Process Tracker */}
                        <div className="mt-6">
                          <div className="relative">
                            <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-100 -translate-y-1/2 rounded-full"></div>
                            <div 
                              className={`absolute top-1/2 left-0 h-1 -translate-y-1/2 rounded-full transition-all duration-500 ${
                                issue.status === 'RESOLVED' ? 'bg-green-500 w-full' :
                                issue.status === 'IN_PROGRESS' ? 'bg-amber-500 w-2/3' :
                                issue.status === 'OPEN' ? 'bg-blue-500 w-1/3' : 'bg-slate-300 w-0'
                              }`}
                            ></div>
                            
                            <div className="relative flex justify-between text-xs font-medium text-slate-500">
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${['OPEN', 'IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-blue-500 bg-blue-500' : 'border-slate-300'}`}></div>
                                <span>Reported</span>
                              </div>
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${['IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-amber-500 bg-amber-500' : 'border-slate-300'}`}></div>
                                <span>In Progress</span>
                              </div>
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${issue.status === 'RESOLVED' ? 'border-green-500 bg-green-500' : 'border-slate-300'}`}></div>
                                <span>Resolved</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-6 mt-6 pt-4 border-t text-sm text-slate-500">
                          <div className="flex items-center gap-2">
                            <ThumbsUp className="h-4 w-4" />
                            {issue._count?.upvotes || 0} Upvotes
                          </div>
                          <div className="flex items-center gap-2">
                            <MessageSquare className="h-4 w-4" />
                            {issue._count?.comments || 0} Comments
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="upvoted" className="space-y-6">
            <div className="grid gap-4">
              {upvotedIssues.length === 0 ? (
                <Card className="p-12 text-center text-slate-500">
                  <div className="flex justify-center mb-4">
                    <div className="p-4 bg-slate-100 rounded-full">
                      <ThumbsUp className="h-8 w-8 text-slate-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">No upvoted issues</h3>
                  <p className="mb-6">You haven't upvoted any issues yet.</p>
                  <Link href="/issues">
                    <Button>Browse Issues</Button>
                  </Link>
                </Card>
              ) : (
                upvotedIssues.map((issue) => (
                  <Card key={issue.id} className="hover:shadow-md transition-shadow overflow-hidden">
                    <div className="flex flex-col md:flex-row">
                      <div className="w-full md:w-48 h-48 md:h-auto relative bg-slate-100">
                        {issue.photoUrl ? (
                          <img 
                            src={issue.photoUrl} 
                            alt={issue.title}
                            className="absolute inset-0 w-full h-full object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full text-slate-400">
                            <MapPin className="h-8 w-8" />
                          </div>
                        )}
                        <div className="absolute top-2 left-2">
                          <Badge className={getStatusColor(issue.status)}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(issue.status)}
                              {issue.status.replace('_', ' ')}
                            </span>
                          </Badge>
                        </div>
                      </div>
                      <div className="flex-1 p-6">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-slate-900 mb-1">
                              <Link href={`/issues/${issue.id}`} className="hover:text-blue-600 transition-colors">
                                {issue.title}
                              </Link>
                            </h3>
                            <div className="flex items-center gap-2 text-sm text-slate-500 mb-4">
                              <MapPin className="h-4 w-4" />
                              {issue.building} {issue.floor && `- Floor ${issue.floor}`}
                              <span className="mx-1">•</span>
                              <Calendar className="h-4 w-4" />
                              {formatRelativeTime(issue.createdAt)}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge variant="outline" className="font-mono">
                              #{issue.id.slice(0, 8)}
                            </Badge>
                          </div>
                        </div>

                        {/* Process Tracker */}
                        <div className="mt-6">
                          <div className="relative">
                            <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-100 -translate-y-1/2 rounded-full"></div>
                            <div 
                              className={`absolute top-1/2 left-0 h-1 -translate-y-1/2 rounded-full transition-all duration-500 ${
                                issue.status === 'RESOLVED' ? 'bg-green-500 w-full' :
                                issue.status === 'IN_PROGRESS' ? 'bg-amber-500 w-2/3' :
                                issue.status === 'OPEN' ? 'bg-blue-500 w-1/3' : 'bg-slate-300 w-0'
                              }`}
                            ></div>
                            
                            <div className="relative flex justify-between text-xs font-medium text-slate-500">
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${['OPEN', 'IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-blue-500 bg-blue-500' : 'border-slate-300'}`}></div>
                                <span>Reported</span>
                              </div>
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${['IN_PROGRESS', 'RESOLVED'].includes(issue.status) ? 'border-amber-500 bg-amber-500' : 'border-slate-300'}`}></div>
                                <span>In Progress</span>
                              </div>
                              <div className="flex flex-col items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 bg-white ${issue.status === 'RESOLVED' ? 'border-green-500 bg-green-500' : 'border-slate-300'}`}></div>
                                <span>Resolved</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-6 mt-6 pt-4 border-t text-sm text-slate-500">
                          <div className="flex items-center gap-2">
                            <ThumbsUp className="h-4 w-4" />
                            {issue._count?.upvotes || 0} Upvotes
                          </div>
                          <div className="flex items-center gap-2">
                            <MessageSquare className="h-4 w-4" />
                            {issue._count?.comments || 0} Comments
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="activity">
            <Card className="border-none shadow-md overflow-hidden">
              <CardHeader className="bg-slate-50/50 border-b">
                <div className="flex items-center gap-2">
                  <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                    <Clock className="h-5 w-5" />
                  </div>
                  <div>
                    <CardTitle>Recent Activity</CardTitle>
                    <CardDescription>Your recent interactions and reports timeline</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="space-y-0">
                  {myIssues.map((issue, index) => (
                    <div key={issue.id} className="flex gap-6 group">
                      <div className="flex flex-col items-center">
                        <div className={`relative z-10 flex h-10 w-10 items-center justify-center rounded-full border-4 border-white shadow-sm transition-colors ${
                          issue.status === 'RESOLVED' ? 'bg-green-100 text-green-600' : 
                          issue.status === 'IN_PROGRESS' ? 'bg-amber-100 text-amber-600' : 
                          'bg-blue-100 text-blue-600'
                        }`}>
                          {issue.status === 'RESOLVED' ? <CheckCircle2 className="h-5 w-5" /> : 
                           issue.status === 'IN_PROGRESS' ? <Clock className="h-5 w-5" /> : 
                           <AlertTriangle className="h-5 w-5" />}
                        </div>
                        <div className="h-full w-px bg-slate-200 my-2 group-last:hidden"></div>
                      </div>
                      <div className="flex-1 pb-8 group-last:pb-0">
                        <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start mb-2">
                            <p className="text-sm font-medium text-slate-900">
                              You reported an issue: <Link href={`/issues/${issue.id}`} className="text-blue-600 hover:underline">{issue.title}</Link>
                            </p>
                            <span className="text-xs text-slate-400 whitespace-nowrap">
                              {formatRelativeTime(issue.createdAt)}
                            </span>
                          </div>
                          <p className="text-sm text-slate-500 line-clamp-2 mb-3">{issue.description}</p>
                          <div className="flex items-center gap-3 text-xs text-slate-400">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(issue.createdAt).toLocaleDateString()}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(issue.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <div className="flex gap-6 group">
                    <div className="flex flex-col items-center">
                      <div className="relative z-10 flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600 border-4 border-white shadow-sm">
                        <Calendar className="h-5 w-5" />
                      </div>
                    </div>
                    <div className="flex-1 pt-2">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 border-dashed">
                        <p className="text-sm font-medium text-slate-900">
                          Joined GramSeva Platform
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Welcome to the community!
                        </p>
                        <p className="text-xs text-slate-400 mt-2">
                          {new Date(profile.createdAt).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
