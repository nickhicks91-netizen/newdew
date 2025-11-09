import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars, Environment } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import type { VisualizationMode, WarpResponse } from '../types';

import EightSpheres from '../visualizations/EightSpheres';
import AttentionGraph from '../visualizations/AttentionGraph';
import PhaseField from '../visualizations/PhaseField';

export interface SceneProps {
  mode: VisualizationMode;
  result: WarpResponse | null;
}

function Loader() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-echo-dark/80">
      <div className="text-center space-y-4">
        <div className="animate-spin text-6xl">🌀</div>
        <div className="text-white font-semibold">Loading Visualization...</div>
      </div>
    </div>
  );
}

export default function Scene({ mode, result }: SceneProps) {
  // Generate mock data from result
  const sphereActivations = result
    ? Array.from({ length: 8 }, () => Math.random() * 0.5 + 0.3)
    : Array(8).fill(0.5);

  const sphereCoupling = result
    ? Array.from({ length: 8 }, () =>
        Array.from({ length: 8 }, () => Math.random() * 0.8 + 0.2)
      )
    : Array(8)
        .fill(0)
        .map(() => Array(8).fill(0.3));

  return (
    <div className="relative w-full h-full bg-gradient-to-b from-echo-dark to-gray-900">
      <Canvas>
        <Suspense fallback={null}>
          {/* Camera */}
          <PerspectiveCamera makeDefault position={[0, 0, 15]} fov={60} />

          {/* Controls */}
          <OrbitControls
            enablePan
            enableZoom
            enableRotate
            minDistance={5}
            maxDistance={30}
            autoRotate
            autoRotateSpeed={0.5}
          />

          {/* Lighting */}
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#6366f1" />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ec4899" />
          <directionalLight position={[0, 5, 5]} intensity={0.5} />

          {/* Environment */}
          <Environment preset="night" />
          <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />

          {/* Visualizations */}
          {mode === 'spheres' && (
            <EightSpheres activations={sphereActivations} coupling={sphereCoupling} />
          )}

          {mode === 'attention' && <AttentionGraph numNodes={20} />}

          {mode === 'phase' && <PhaseField dim={128} />}

          {mode === 'harmonic' && (
            <EightSpheres activations={sphereActivations} coupling={sphereCoupling} />
          )}

          {/* Post-processing effects */}
          <EffectComposer>
            <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} intensity={1.5} />
          </EffectComposer>
        </Suspense>
      </Canvas>

      {/* Loading overlay */}
      <Suspense fallback={<Loader />} />
    </div>
  );
}
