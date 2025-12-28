'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Camera, 
  MapPin, 
  Bell, 
  BarChart3, 
  Shield, 
  Clock,
  ArrowRight,
  Zap,
  CheckCircle2,
  Users,
  Activity
} from 'lucide-react';

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

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-emerald-200/40 rounded-full blur-3xl" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-green-200/40 rounded-full blur-3xl" />
        <div className="absolute top-[40%] left-[30%] w-[400px] h-[400px] bg-emerald-200/30 rounded-full blur-3xl" />
      </div>

      {/* Hero Section */}
      <section className="relative pt-24 pb-32 z-10">
        <div className="container relative mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center rounded-full border border-green-200 bg-white/60 backdrop-blur-sm px-4 py-1.5 text-sm font-medium text-green-600 mb-8 shadow-sm">
              <span className="flex h-2 w-2 rounded-full bg-green-600 mr-2 animate-pulse"></span>
              Live at Gram Panchayat
            </div>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-slate-900 leading-tight">
              Fix Your Village in{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">Real-Time</span>
            </h1>
            <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              The modern way to report and track rural infrastructure issues. 
              Snap a photo, tag the location, and watch it get fixed.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/report">
                <Button size="lg" className="h-14 px-8 text-lg gap-2 rounded-full shadow-xl shadow-green-600/20 bg-green-600 hover:bg-green-700 hover:scale-105 transition-all">
                  <Camera className="h-5 w-5" />
                  Report Issue Now
                </Button>
              </Link>
              <Link href="/issues">
                <Button size="lg" variant="outline" className="h-14 px-8 text-lg gap-2 rounded-full border-slate-300 bg-white/50 hover:bg-white hover:scale-105 transition-all">
                  View Live Issues
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-12 relative z-10">
        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6"
        >
          {[
            { label: 'Issues Reported', value: '500+', icon: Activity, color: 'text-green-600', bg: 'bg-green-50' },
            { label: 'Resolution Rate', value: '85%', icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
            { label: 'Avg Response', value: '24h', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
            { label: 'Active Users', value: '1000+', icon: Users, color: 'text-teal-600', bg: 'bg-teal-50' },
          ].map((stat, index) => (
            <motion.div key={index} variants={item}>
              <Card className="text-center border-white/50 shadow-lg shadow-slate-200/50 bg-white/60 backdrop-blur-md hover:-translate-y-1 transition-transform duration-300">
                <CardContent className="pt-6 flex flex-col items-center">
                  <div className={`p-3 rounded-2xl ${stat.bg} mb-4`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className={`text-3xl font-bold mb-1 ${stat.color}`}>{stat.value}</div>
                  <div className="text-sm font-medium text-slate-500">{stat.label}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-24 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-slate-900">Why GramSeva Works</h2>
          <p className="text-slate-600 max-w-2xl mx-auto text-lg">
            We've streamlined the entire process of rural maintenance reporting to ensure nothing falls through the cracks.
          </p>
        </div>
        
        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-8"
        >
          {[
            { icon: Camera, title: 'Photo Evidence', desc: 'Every report requires a photo. No vague complaints, just clear evidence.', color: 'text-green-600' },
            { icon: MapPin, title: 'GPS Location', desc: 'Automatic location tagging. Maintenance knows exactly where to go.', color: 'text-emerald-600' },
            { icon: Shield, title: 'Public Accountability', desc: 'All issues visible to everyone. Nothing gets swept under the rug.', color: 'text-teal-600' },
            { icon: Clock, title: 'Auto Escalation', desc: 'Unresolved issues automatically escalate to higher authorities.', color: 'text-amber-600' },
            { icon: Bell, title: 'Real-time Updates', desc: 'Get notified when your issue is acknowledged, in progress, or resolved.', color: 'text-red-600' },
            { icon: BarChart3, title: 'Analytics Dashboard', desc: 'Visualize problem hotspots on 3D village map. Data-driven decisions.', color: 'text-cyan-600' },
          ].map((feature, index) => (
            <motion.div key={index} variants={item}>
              <Card className="h-full border-white/50 shadow-lg shadow-slate-200/50 bg-white/60 backdrop-blur-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <CardHeader>
                  <div className={`w-14 h-14 rounded-2xl ${feature.color.replace('text-', 'bg-').replace('600', '100')} flex items-center justify-center mb-4 shadow-sm`}>
                    <feature.icon className={`h-7 w-7 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl font-bold text-slate-800">{feature.title}</CardTitle>
                  <CardDescription className="text-base mt-2 text-slate-600 leading-relaxed">
                    {feature.desc}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24 relative z-10">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-green-600 to-emerald-700 text-white shadow-2xl shadow-green-900/30"
        >
          <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-black/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
          
          <div className="relative px-6 py-20 md:px-12 md:py-24 text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
              Ready to improve your village?
            </h2>
            <p className="text-green-100 mb-10 max-w-2xl mx-auto text-xl leading-relaxed">
              Join hundreds of villagers already making their community a better place. 
              Report your first issue today and see the change.
            </p>
            <Link href="/register">
              <Button size="lg" variant="secondary" className="h-14 px-10 text-lg gap-2 rounded-full shadow-xl hover:scale-105 transition-all font-semibold text-green-700">
                Create Free Account
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      {/* Footer removed to avoid duplication with global layout */}
    </div>
  );
}
