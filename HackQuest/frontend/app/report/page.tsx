'use client';

import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { 
  Camera, 
  MapPin, 
  Upload,
  Loader2,
  X,
  CheckCircle2,
  AlertTriangle,
  Info,
  FileText,
  Building
} from 'lucide-react';

const CATEGORIES = [
  { value: 'ROADS', label: 'Roads & Paths', icon: '🛣️' },
  { value: 'WATER', label: 'Water Supply', icon: '🚰' },
  { value: 'ELECTRICITY', label: 'Electricity', icon: '💡' },
  { value: 'SANITATION', label: 'Sanitation/Drainage', icon: '🧹' },
  { value: 'AGRICULTURE', label: 'Agriculture', icon: '🌾' },
  { value: 'HEALTH', label: 'Health Center', icon: '🏥' },
  { value: 'EDUCATION', label: 'School/Anganwadi', icon: '🏫' },
  { value: 'OTHER', label: 'Other', icon: '📋' },
];

const PRIORITIES = [
  { value: 'LOW', label: 'Low', description: 'Minor inconvenience' },
  { value: 'MEDIUM', label: 'Medium', description: 'Should be fixed soon' },
  { value: 'HIGH', label: 'High', description: 'Urgent issue' },
  { value: 'CRITICAL', label: 'Critical', description: 'Safety hazard' },
];

const formSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(200),
  description: z.string().max(2000).optional(),
  category: z.string().min(1, 'Please select a category'),
  priority: z.string().optional(),
  building: z.string().optional(),
  floor: z.string().optional(),
  room: z.string().optional(),
  locationDescription: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

export default function ReportPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { token, isAuthenticated } = useAuthStore();
  
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      priority: 'MEDIUM',
    },
  });

  const handlePhotoCapture = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const handleGetLocation = useCallback(() => {
    setIsLoadingLocation(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setIsLoadingLocation(false);
          toast({
            title: "Location acquired",
            description: "Your current location has been added to the report.",
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          setIsLoadingLocation(false);
          toast({
            variant: "destructive",
            title: "Location error",
            description: "Could not get your location. Please enable GPS.",
          });
        }
      );
    } else {
      setIsLoadingLocation(false);
      toast({
        variant: "destructive",
        title: "Not supported",
        description: "Geolocation is not supported by your browser.",
      });
    }
  }, [toast]);

  const onSubmit = async (data: FormData) => {
    if (!isAuthenticated) {
      toast({
        variant: "destructive",
        title: "Authentication required",
        description: "Please login to report an issue.",
      });
      router.push('/login');
      return;
    }

    if (!photo) {
      toast({
        variant: "destructive",
        title: "Photo required",
        description: "Please attach a photo of the issue.",
      });
      return;
    }

    if (!location) {
      toast({
        variant: "destructive",
        title: "Location required",
        description: "Please enable GPS to tag the issue location.",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      // 1. Upload photo
      if (!token) throw new Error("Not authenticated");
      const uploadRes = await api.uploadImage(photo, token);
      
      // 2. Create issue
      await api.createIssue({
        title: data.title,
        description: data.description || '',
        category: data.category,
        priority: data.priority || 'MEDIUM',
        photoUrl: uploadRes.url,
        latitude: location.lat,
        longitude: location.lng,
        building: data.building,
        floor: data.floor,
        room: data.room,
        locationDescription: data.locationDescription,
      });

      toast({
        title: "Issue reported",
        description: "Thank you for helping improve our village!",
      });
      router.push('/issues');
    } catch (error) {
      console.error('Error submitting report:', error);
      toast({
        variant: "destructive",
        title: "Submission failed",
        description: "There was an error submitting your report. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden py-8">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-200/40 rounded-full blur-3xl" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-blue-200/40 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 max-w-3xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Report Village Issue</h1>
            <p className="text-slate-500">Help us improve our village infrastructure</p>
          </div>

          <Card className="border-white/50 shadow-xl bg-white/80 backdrop-blur-md">
            <CardContent className="p-6 md:p-8">
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                
                {/* Photo Section */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-slate-800 font-semibold">
                    <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg">
                      <Camera className="w-4 h-4" />
                    </div>
                    <span>Photo Evidence</span>
                  </div>
                  
                  <div 
                    className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
                      photoPreview 
                        ? 'border-blue-500 bg-blue-50/50' 
                        : 'border-slate-300 hover:border-blue-400 hover:bg-white/50 bg-white/30'
                    }`}
                  >
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      className="hidden"
                      ref={fileInputRef}
                      onChange={handlePhotoCapture}
                    />
                    
                    {photoPreview ? (
                      <div className="relative aspect-video max-h-[300px] mx-auto rounded-xl overflow-hidden shadow-lg">
                        <img src={photoPreview} alt="Preview" className="w-full h-full object-cover" />
                        <Button
                          type="button"
                          variant="destructive"
                          size="icon"
                          className="absolute top-2 right-2 rounded-full shadow-lg"
                          onClick={(e) => {
                            e.stopPropagation();
                            setPhoto(null);
                            setPhotoPreview(null);
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <div 
                        className="cursor-pointer flex flex-col items-center gap-4 py-6"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <div className="h-20 w-20 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-500 shadow-sm group-hover:scale-110 transition-transform">
                          <Camera className="h-10 w-10" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 text-lg">Click to take a photo</p>
                          <p className="text-sm text-slate-500">or upload from gallery</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Details Section */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-slate-800 font-semibold">
                    <div className="p-1.5 bg-purple-100 text-purple-600 rounded-lg">
                      <FileText className="w-4 h-4" />
                    </div>
                    <span>Issue Details</span>
                  </div>

                  <div className="grid gap-5">
                    <div className="space-y-2">
                      <Label htmlFor="title" className="text-slate-600">Title</Label>
                      <Input 
                        id="title" 
                        placeholder="Brief summary of the issue" 
                        {...register('title')}
                        className={`bg-white/50 border-slate-200 focus:bg-white transition-all ${errors.title ? 'border-red-500' : ''}`}
                      />
                      {errors.title && (
                        <p className="text-xs text-red-500">{errors.title.message}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      <div className="space-y-2">
                        <Label htmlFor="category" className="text-slate-600">Category</Label>
                        <Select onValueChange={(val) => setValue('category', val)}>
                          <SelectTrigger className={`bg-white/50 border-slate-200 focus:bg-white transition-all ${errors.category ? 'border-red-500' : ''}`}>
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent>
                            {CATEGORIES.map((cat) => (
                              <SelectItem key={cat.value} value={cat.value}>
                                <span className="flex items-center gap-2">
                                  <span>{cat.icon}</span>
                                  {cat.label}
                                </span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {errors.category && (
                          <p className="text-xs text-red-500">{errors.category.message}</p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="priority" className="text-slate-600">Priority</Label>
                        <Select 
                          defaultValue="MEDIUM"
                          onValueChange={(val) => setValue('priority', val)}
                        >
                          <SelectTrigger className="bg-white/50 border-slate-200 focus:bg-white transition-all">
                            <SelectValue placeholder="Select priority" />
                          </SelectTrigger>
                          <SelectContent>
                            {PRIORITIES.map((p) => (
                              <SelectItem key={p.value} value={p.value}>
                                <div className="flex flex-col items-start py-1">
                                  <span className="font-medium">{p.label}</span>
                                  <span className="text-xs text-slate-500">{p.description}</span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="description" className="text-slate-600">Description</Label>
                      <Textarea 
                        id="description" 
                        placeholder="Provide more details about the issue..." 
                        className="min-h-[100px] bg-white/50 border-slate-200 focus:bg-white transition-all"
                        {...register('description')}
                      />
                    </div>
                  </div>
                </div>

                {/* Location Section */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-slate-800 font-semibold">
                    <div className="p-1.5 bg-emerald-100 text-emerald-600 rounded-lg">
                      <Building className="w-4 h-4" />
                    </div>
                    <span>Location</span>
                  </div>

                  <div className="grid gap-5">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="building" className="text-slate-600">Landmark/Area</Label>
                        <Input id="building" placeholder="e.g. Near Panchayat Bhawan" {...register('building')} className="bg-white/50 border-slate-200 focus:bg-white transition-all" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="floor" className="text-slate-600">Street/Lane</Label>
                        <Input id="floor" placeholder="e.g. Main Market Road" {...register('floor')} className="bg-white/50 border-slate-200 focus:bg-white transition-all" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="room" className="text-slate-600">House No./Details</Label>
                        <Input id="room" placeholder="e.g. House No. 45" {...register('room')} className="bg-white/50 border-slate-200 focus:bg-white transition-all" />
                      </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-slate-50/80 rounded-xl border border-slate-200">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                        <MapPin className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900">GPS Coordinates</p>
                        <p className="text-xs text-slate-500 font-mono mt-0.5">
                          {location 
                            ? `${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}`
                            : "Location not set"}
                        </p>
                      </div>
                      <Button
                        type="button"
                        variant={location ? "outline" : "secondary"}
                        size="sm"
                        onClick={handleGetLocation}
                        disabled={isLoadingLocation}
                        className={location ? "text-green-600 border-green-200 bg-green-50 hover:bg-green-100" : "bg-white shadow-sm hover:bg-slate-50"}
                      >
                        {isLoadingLocation ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : location ? (
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                        ) : (
                          <MapPin className="h-4 w-4 mr-2" />
                        )}
                        {location ? "Updated" : "Get Location"}
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <Button 
                    type="submit" 
                    className="w-full h-12 text-lg font-medium shadow-xl shadow-blue-600/20 bg-blue-600 hover:bg-blue-700 transition-all hover:scale-[1.02]" 
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      'Submit Report'
                    )}
                  </Button>
                  <p className="text-xs text-center text-slate-500 mt-4">
                    By submitting, you agree that the information provided is accurate.
                  </p>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
