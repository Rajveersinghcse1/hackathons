'use client';

import { useState, useMemo, Suspense, useRef } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Environment, useCursor } from '@react-three/drei';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Navigation,
  Layers,
  Activity,
  Building as BuildingIcon
} from 'lucide-react';
import * as THREE from 'three';

// Village layout configuration
const LOCATIONS = [
  { id: 'panchayat', name: 'Panchayat Bhawan', position: [0, 0, 0], size: [4, 2, 4], color: '#f59e0b' },
  { id: 'school', name: 'Primary School', position: [-8, 0, -5], size: [6, 1.5, 3], color: '#3b82f6' },
  { id: 'market', name: 'Market Area', position: [6, 0, 5], size: [5, 0.5, 5], color: '#10b981' },
  { id: 'phc', name: 'Health Center', position: [-10, 0, 8], size: [4, 1.5, 4], color: '#ef4444' },
  { id: 'tank', name: 'Water Tank', position: [8, 0, -8], size: [2, 6, 2], color: '#0ea5e9' },
  { id: 'hall', name: 'Community Hall', position: [15, 0, 5], size: [5, 2, 5], color: '#8b5cf6' },
];

function Building({ building, issueCount, maxIssues, onClick }: { 
  building: any; 
  issueCount: number; 
  maxIssues: number;
  onClick: () => void;
}) {
  const [hovered, setHover] = useState(false);
  useCursor(hovered);

  // Color interpolation based on issue severity
  const color = useMemo(() => {
    if (issueCount === 0) return building.color;
    const intensity = Math.min(issueCount / 5, 1); // Cap at 5 issues for max redness
    return new THREE.Color(building.color).lerp(new THREE.Color('#ef4444'), intensity);
  }, [building.color, issueCount]);

  const height = building.size[1];

  return (
    <group position={building.position as [number, number, number]}>
      <mesh
        position={[0, height / 2, 0]}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={() => setHover(true)}
        onPointerOut={() => setHover(false)}
        castShadow
        receiveShadow
      >
        <boxGeometry args={building.size as [number, number, number]} />
        <meshStandardMaterial 
          color={hovered ? '#3b82f6' : color}
          roughness={0.2}
          metalness={0.1}
        />
      </mesh>
      
      {/* Windows effect */}
      <mesh position={[0, height / 2, 0.05]}>
        <boxGeometry args={[building.size[0] * 0.9, height * 0.8, building.size[2] * 1.01]} />
        <meshStandardMaterial color="#000" opacity={0.2} transparent />
      </mesh>

      {/* Label & Status Tooltip */}
      {(hovered || issueCount > 0) && (
        <Html position={[0, height + 1.5, 0]} center distanceFactor={15} style={{ pointerEvents: 'none' }}>
          <motion.div 
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className="bg-white/90 backdrop-blur-md p-3 rounded-xl shadow-xl border border-white/50 text-center min-w-[140px]"
          >
            <p className="font-bold text-sm text-slate-800">{building.name}</p>
            <div className={`flex items-center justify-center gap-1.5 mt-1.5 text-xs font-semibold ${
              issueCount > 0 ? 'text-red-500' : 'text-emerald-600'
            }`}>
              {issueCount > 0 ? (
                <>
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>{issueCount} Issues</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>All Clear</span>
                </>
              )}
            </div>
          </motion.div>
        </Html>
      )}
    </group>
  );
}

function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
      <planeGeometry args={[100, 100]} />
      <meshStandardMaterial color="#f1f5f9" />
    </mesh>
  );
}

function Roads() {
  return (
    <group>
      {/* Main horizontal road */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.09, 6]}>
        <planeGeometry args={[40, 3]} />
        <meshStandardMaterial color="#cbd5e1" />
      </mesh>
      {/* Main vertical road */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[6, -0.09, 0]}>
        <planeGeometry args={[3, 40]} />
        <meshStandardMaterial color="#cbd5e1" />
      </mesh>
    </group>
  );
}

function Scene({ heatmapData, onBuildingClick }: { 
  heatmapData: any; 
  onBuildingClick: (building: string) => void;
}) {
  
  // Calculate issue counts per building
  const buildingIssues = useMemo(() => {
    const counts: Record<string, number> = {};
    if (heatmapData?.buildings) {
      heatmapData.buildings.forEach((b: any) => {
        const key = b.name?.toLowerCase().replace(' block', '').replace(' ', '');
        counts[key] = b.count;
      });
    }
    return counts;
  }, [heatmapData]);

  const maxIssues = useMemo(() => {
    return Math.max(1, ...Object.values(buildingIssues));
  }, [buildingIssues]);

  return (
    <>
      <ambientLight intensity={0.7} />
      <directionalLight
        position={[10, 20, 10]}
        intensity={1.2}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      
      <Ground />
      <Roads />
      
      {LOCATIONS.map((building) => (
        <Building
          key={building.id}
          building={building}
          issueCount={buildingIssues[building.id] || 0}
          maxIssues={maxIssues}
          onClick={() => onBuildingClick(building.name)}
        />
      ))}

      {/* Issue markers from actual data */}
      {heatmapData?.points?.map((point: any, index: number) => (
        <mesh
          key={point.id || index}
          position={[
            (point.lng - 77.57) * 10000, // Scale for visualization
            0.5,
            (point.lat - 13.03) * 10000,
          ]}
        >
          <sphereGeometry args={[0.3 * point.weight, 16, 16]} />
          <meshStandardMaterial
            color={
              point.weight >= 4 ? '#ef4444' :
              point.weight >= 3 ? '#f97316' :
              point.weight >= 2 ? '#eab308' : '#22c55e'
            }
            emissive={point.weight >= 3 ? '#ff0000' : undefined}
            emissiveIntensity={0.4}
            transparent
            opacity={0.8}
          />
        </mesh>
      ))}

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={10}
        maxDistance={60}
        maxPolarAngle={Math.PI / 2.2}
      />
    </>
  );
}

export default function VillageMapPage() {
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);

  const { data: heatmapData, isLoading } = useQuery({
    queryKey: ['heatmap'],
    queryFn: () => api.getHeatmap(),
  });

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.getStats(),
  });

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-200/40 rounded-full blur-3xl" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-blue-200/40 rounded-full blur-3xl" />
      </div>

      <div className="flex h-[calc(100vh-64px)] relative z-10">
        {/* 3D Canvas */}
        <div className="flex-1 relative bg-slate-900/5 backdrop-blur-sm">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <div className="text-slate-600 font-medium">Loading Village Map...</div>
              </div>
            </div>
          ) : (
            <Canvas
              shadows
              camera={{ position: [25, 20, 25], fov: 45 }}
              gl={{ antialias: true }}
              className="w-full h-full"
            >
              <Suspense fallback={null}>
                <Scene
                  heatmapData={heatmapData}
                  onBuildingClick={(building) => setSelectedBuilding(building)}
                />
                <Environment preset="city" />
              </Suspense>
            </Canvas>
          )}

          {/* Floating Controls Hint */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="absolute bottom-6 left-6"
          >
            <div className="bg-white/80 backdrop-blur-md border border-white/40 p-3 rounded-2xl shadow-lg flex items-center gap-4 text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg">
                  <Navigation className="w-3.5 h-3.5" />
                </div>
                <span>Rotate & Zoom</span>
              </div>
              <div className="w-px h-4 bg-slate-200" />
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-purple-100 text-purple-600 rounded-lg">
                  <MapPin className="w-3.5 h-3.5" />
                </div>
                <span>Select Building</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="w-96 bg-white/60 backdrop-blur-xl border-l border-white/40 shadow-2xl overflow-y-auto p-6">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-2 bg-blue-600 rounded-xl shadow-lg shadow-blue-600/20">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-lg font-bold text-slate-800">Village Overview</h3>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-3 mb-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="bg-white/50 border-white/50 shadow-sm hover:shadow-md transition-all">
                <CardContent className="p-4 text-center">
                  <p className="text-2xl font-bold text-red-500">{stats?.openIssues || 0}</p>
                  <p className="text-xs font-medium text-slate-500 mt-1">Active Issues</p>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="bg-white/50 border-white/50 shadow-sm hover:shadow-md transition-all">
                <CardContent className="p-4 text-center">
                  <p className="text-2xl font-bold text-emerald-500">{stats?.resolvedThisWeek || 0}</p>
                  <p className="text-xs font-medium text-slate-500 mt-1">Resolved</p>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Building List */}
          <div className="mb-8">
            <h4 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
              <BuildingIcon className="w-3 h-3" />
              Locations Status
            </h4>
            <div className="space-y-2">
              {heatmapData?.buildings?.map((building: any, index: number) => (
                <motion.div
                  key={building.name}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Link href={`/issues?building=${encodeURIComponent(building.name)}`}>
                    <div className="group flex items-center justify-between p-3 bg-white/40 hover:bg-white/80 border border-white/40 hover:border-blue-200 rounded-xl transition-all cursor-pointer">
                      <span className="text-slate-700 text-sm font-medium group-hover:text-blue-700 transition-colors">
                        {building.name}
                      </span>
                      <Badge variant={building.count > 0 ? "destructive" : "secondary"} className={building.count === 0 ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200" : ""}>
                        {building.count} issues
                      </Badge>
                    </div>
                  </Link>
                </motion.div>
              ))}
              {(!heatmapData?.buildings || heatmapData.buildings.length === 0) && (
                <div className="text-center py-8 bg-white/20 rounded-xl border border-dashed border-slate-300">
                  <p className="text-slate-500 text-sm">No issue data available</p>
                </div>
              )}
            </div>
          </div>

          {/* Category breakdown */}
          <div>
            <h4 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
              <Activity className="w-3 h-3" />
              By Category
            </h4>
            <div className="space-y-2">
              {stats?.categoryStats?.map((cat: any, index: number) => (
                <motion.div 
                  key={cat.category}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + (0.1 * index) }}
                  className="flex items-center justify-between p-2.5 bg-slate-100/50 rounded-lg"
                >
                  <span className="text-slate-600 text-sm capitalize">{cat.category.replace('_', ' ')}</span>
                  <span className="font-bold text-slate-800 text-sm">{cat.count}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
