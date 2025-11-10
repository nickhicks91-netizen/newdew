import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import type { Point3D } from '../types';

interface RhombicVisualizationProps {
  points: Point3D[];
  memory: any[][];
  adjacency: Map<number, any[]>;
  autoRotate?: boolean;
}

export function RhombicVisualization({
  points,
  memory,
  adjacency,
  autoRotate = true
}: RhombicVisualizationProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.2;
    }
  });

  const channelColors = ['#ff00ff', '#00ff41', '#ffaa00', '#00aaff'];

  const connections = useMemo(() => {
    const lines: { start: THREE.Vector3; end: THREE.Vector3; opacity: number }[] = [];

    for (let i = 0; i < points.length; i++) {
      const p1 = points[i];
      const neighbors = adjacency.get(i) || [];

      for (const neighbor of neighbors.slice(0, 3)) {
        const p2 = points[neighbor.id];

        lines.push({
          start: new THREE.Vector3(p1.rawX, p1.rawY, p1.rawZ),
          end: new THREE.Vector3(p2.rawX, p2.rawY, p2.rawZ),
          opacity: 0.15
        });
      }
    }

    return lines;
  }, [points, adjacency]);

  return (
    <group ref={groupRef}>
      {/* Connections */}
      {connections.map((line, i) => (
        <Line
          key={`line-${i}`}
          points={[line.start, line.end]}
          color="#ff00ff"
          lineWidth={0.5}
          transparent
          opacity={line.opacity}
        />
      ))}

      {/* Memory points */}
      {points.map((point, i) => {
        const load = memory[i]?.length || 0;
        if (load === 0) return null;

        const color = channelColors[point.channel];
        const size = 0.03 + load * 0.015;
        const intensity = Math.min(load / 5, 1);

        return (
          <Sphere
            key={`point-${i}`}
            position={[point.rawX, point.rawY, point.rawZ]}
            args={[size, 16, 16]}
          >
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={intensity * 0.5}
              transparent
              opacity={0.7 + intensity * 0.3}
            />
          </Sphere>
        );
      })}

      {/* Ambient particles for depth */}
      <Points count={200} />
    </group>
  );
}

function Points({ count }: { count: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI * 2;
      const r = 1.5 + Math.random() * 0.5;

      positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = r * Math.cos(phi);

      const color = new THREE.Color();
      color.setHSL(Math.random() * 0.3 + 0.7, 0.7, 0.5);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    return { positions, colors };
  }, [count]);

  useFrame((state) => {
    if (pointsRef.current) {
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;

      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        const x = positions[i3];
        const z = positions[i3 + 2];

        const angle = state.clock.elapsedTime * 0.1;

        positions[i3] = x * Math.cos(angle * 0.1) - z * Math.sin(angle * 0.1);
        positions[i3 + 2] = x * Math.sin(angle * 0.1) + z * Math.cos(angle * 0.1);
      }

      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={particles.colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        vertexColors
        transparent
        opacity={0.4}
        sizeAttenuation
      />
    </points>
  );
}
