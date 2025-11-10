import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line, Sphere, Ring } from '@react-three/drei';
import * as THREE from 'three';
import type { Point3D } from '../types';

interface EnhancedVisualizationProps {
  points: Point3D[];
  memory: any[][];
  adjacency: Map<number, any[]>;
  torsionField: number[];
  quantumStates: number[];
  autoRotate?: boolean;
  processingState?: 'idle' | 'encoding' | 'recalling';
  hashPoint?: number;
}

interface MemoryOrb {
  vertexIndex: number;
  count: number;
  age: number;
}

interface InjectionRing {
  position: THREE.Vector3;
  scale: number;
  opacity: number;
}

interface EdgeParticle {
  edgeIndex: number;
  progress: number;
  speed: number;
}

interface QuantumBolt {
  v1: number;
  v2: number;
  intensity: number;
  life: number;
}

export function EnhancedRhombicVisualization({
  points,
  memory,
  adjacency,
  torsionField,
  quantumStates,
  autoRotate = true,
  processingState = 'idle',
  hashPoint
}: EnhancedVisualizationProps) {
  const groupRef = useRef<THREE.Group>(null);

  // State for animated elements
  const [injectionRings, setInjectionRings] = useState<InjectionRing[]>([]);
  const [memoryOrbs, setMemoryOrbs] = useState<MemoryOrb[]>([]);
  const [edgeParticles, setEdgeParticles] = useState<EdgeParticle[]>([]);
  const [quantumBolts, setQuantumBolts] = useState<QuantumBolt[]>([]);

  const channelColors = ['#ff00ff', '#00ff41', '#ffaa00', '#00aaff'];

  // Update memory orbs when memory changes
  useEffect(() => {
    const orbs: MemoryOrb[] = [];
    for (let i = 0; i < memory.length; i++) {
      if (memory[i].length > 0) {
        orbs.push({
          vertexIndex: i,
          count: memory[i].length,
          age: 0
        });
      }
    }
    setMemoryOrbs(orbs);
  }, [memory]);

  // Create injection ring when encoding starts
  useEffect(() => {
    if (processingState === 'encoding' && hashPoint !== undefined) {
      const point = points[hashPoint];
      setInjectionRings(prev => [...prev, {
        position: new THREE.Vector3(point.rawX, point.rawY, point.rawZ),
        scale: 1,
        opacity: 1
      }]);
    }
  }, [processingState, hashPoint, points]);

  // Spawn edge particles for high coupling
  useEffect(() => {
    if (processingState === 'encoding') {
      const particles: EdgeParticle[] = [];

      for (let i = 0; i < Math.min(adjacency.size, 50); i++) {
        const edges = Array.from(adjacency.entries());
        const [v1, neighbors] = edges[Math.floor(Math.random() * edges.length)];

        if (neighbors && neighbors.length > 0) {
          const v2 = neighbors[Math.floor(Math.random() * neighbors.length)].id;
          const coupling = Math.abs(quantumStates[v1] * quantumStates[v2]);

          if (coupling > 0.3) {
            particles.push({
              edgeIndex: i,
              progress: Math.random(),
              speed: 0.015 + Math.random() * 0.015
            });
          }
        }
      }

      setEdgeParticles(particles);
    } else {
      setEdgeParticles([]);
    }
  }, [processingState, quantumStates, adjacency]);

  // Create quantum bolts for strong coupling
  useEffect(() => {
    if (processingState === 'encoding') {
      const bolts: QuantumBolt[] = [];

      for (const [v1, neighbors] of adjacency) {
        for (const neighbor of neighbors) {
          const v2 = neighbor.id;
          const state1 = quantumStates[v1];
          const state2 = quantumStates[v2];
          const coupling = Math.abs(state1 * state2);

          if (coupling > 0.75 && Math.random() < 0.1) {
            bolts.push({
              v1,
              v2,
              intensity: coupling,
              life: 30 // frames
            });
          }
        }
      }

      setQuantumBolts(bolts);
    }
  }, [processingState, quantumStates, adjacency]);

  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.2;
    }

    // Update injection rings
    setInjectionRings(prev =>
      prev
        .map(ring => ({
          ...ring,
          scale: ring.scale + 0.05,
          opacity: ring.opacity - 0.02
        }))
        .filter(ring => ring.opacity > 0)
    );

    // Update memory orbs age for animation
    setMemoryOrbs(prev =>
      prev.map(orb => ({
        ...orb,
        age: orb.age + 0.02
      }))
    );

    // Update edge particles
    setEdgeParticles(prev =>
      prev.map(p => ({
        ...p,
        progress: (p.progress + p.speed) % 1
      }))
    );

    // Update quantum bolts
    setQuantumBolts(prev =>
      prev
        .map(bolt => ({
          ...bolt,
          life: bolt.life - 1
        }))
        .filter(bolt => bolt.life > 0)
    );
  });

  // Edge connections
  const connections = useMemo(() => {
    const lines: { start: THREE.Vector3; end: THREE.Vector3; opacity: number; v1: number; v2: number }[] = [];

    for (let i = 0; i < points.length; i++) {
      const p1 = points[i];
      const neighbors = adjacency.get(i) || [];

      for (const neighbor of neighbors.slice(0, 3)) {
        const p2 = points[neighbor.id];

        lines.push({
          start: new THREE.Vector3(p1.rawX, p1.rawY, p1.rawZ),
          end: new THREE.Vector3(p2.rawX, p2.rawY, p2.rawZ),
          opacity: 0.15,
          v1: i,
          v2: neighbor.id
        });
      }
    }

    return lines;
  }, [points, adjacency]);

  // Channel halos
  const channelCenters = useMemo(() => {
    const centers: { position: THREE.Vector3; color: string; load: number }[] = [];

    for (let ch = 0; ch < 4; ch++) {
      const channelPoints = points.filter(p => p.channel === ch);
      const center = new THREE.Vector3();

      channelPoints.forEach(p => {
        center.add(new THREE.Vector3(p.rawX, p.rawY, p.rawZ));
      });

      if (channelPoints.length > 0) {
        center.divideScalar(channelPoints.length);

        const load = memory
          .filter((m, idx) => points[idx]?.channel === ch)
          .reduce((sum, m) => sum + m.length, 0);

        centers.push({
          position: center,
          color: channelColors[ch],
          load
        });
      }
    }

    return centers;
  }, [points, memory, channelColors]);

  return (
    <group ref={groupRef}>
      {/* Channel halos */}
      {channelCenters.map((center, i) => (
        <mesh key={`halo-${i}`} position={center.position}>
          <sphereGeometry args={[1.5, 32, 32]} />
          <meshBasicMaterial
            color={center.color}
            transparent
            opacity={0.05 + (center.load / 100) * 0.15}
            side={THREE.BackSide}
          />
        </mesh>
      ))}

      {/* Edge connections */}
      {connections.map((line, i) => {
        const intensity = (torsionField[line.v1] + torsionField[line.v2]) / 2;

        return (
          <Line
            key={`line-${i}`}
            points={[line.start, line.end]}
            color={new THREE.Color().setHSL(0.55 + intensity * 0.3, 0.8, 0.5)}
            lineWidth={0.5}
            transparent
            opacity={line.opacity + intensity * 0.4}
          />
        );
      })}

      {/* Edge particles */}
      {edgeParticles.map((particle, i) => {
        const edgeIdx = particle.edgeIndex % connections.length;
        const edge = connections[edgeIdx];
        const position = new THREE.Vector3().lerpVectors(
          edge.start,
          edge.end,
          particle.progress
        );

        return (
          <Sphere
            key={`particle-${i}`}
            position={position}
            args={[0.05, 8, 8]}
          >
            <meshBasicMaterial
              color="#00ffff"
              transparent
              opacity={0.8}
            />
          </Sphere>
        );
      })}

      {/* Memory points */}
      {points.map((point, i) => {
        const load = memory[i]?.length || 0;
        if (load === 0) return null;

        const color = channelColors[point.channel];
        const size = 0.03 + load * 0.015;
        const intensity = Math.min(load / 5, 1);

        // Extra glow for hash point
        const isHashPoint = hashPoint === i;

        return (
          <Sphere
            key={`point-${i}`}
            position={[point.rawX, point.rawY, point.rawZ]}
            args={[size, 16, 16]}
          >
            <meshStandardMaterial
              color={isHashPoint ? '#ffffff' : color}
              emissive={isHashPoint ? '#ffff00' : color}
              emissiveIntensity={isHashPoint ? 1.5 : intensity * 0.5}
              transparent
              opacity={0.7 + intensity * 0.3}
            />
          </Sphere>
        );
      })}

      {/* Memory orbs (persistent storage indicators) */}
      {memoryOrbs.map((orb) => {
        const point = points[orb.vertexIndex];
        const yOffset = Math.sin(orb.age) * 0.05 + orb.count * 0.1;

        return (
          <Sphere
            key={`orb-${orb.vertexIndex}`}
            position={[point.rawX, point.rawY + yOffset, point.rawZ]}
            args={[0.08, 16, 16]}
          >
            <meshStandardMaterial
              color="#ffaa00"
              emissive="#ff6600"
              emissiveIntensity={0.5}
              transparent
              opacity={Math.min(orb.count * 0.2, 0.8)}
            />
          </Sphere>
        );
      })}

      {/* Injection rings */}
      {injectionRings.map((ring, i) => (
        <Ring
          key={`ring-${i}`}
          position={ring.position}
          args={[0.1 * ring.scale, 0.15 * ring.scale, 32]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <meshBasicMaterial
            color="#ffffff"
            transparent
            opacity={ring.opacity}
            side={THREE.DoubleSide}
          />
        </Ring>
      ))}

      {/* Quantum coupling bolts */}
      {quantumBolts.map((bolt, i) => {
        const p1 = points[bolt.v1];
        const p2 = points[bolt.v2];

        // Create jagged path
        const start = new THREE.Vector3(p1.rawX, p1.rawY, p1.rawZ);
        const end = new THREE.Vector3(p2.rawX, p2.rawY, p2.rawZ);
        const mid = new THREE.Vector3().lerpVectors(start, end, 0.5);

        // Add random offset to middle point
        mid.x += (Math.random() - 0.5) * 0.3;
        mid.y += (Math.random() - 0.5) * 0.3;
        mid.z += (Math.random() - 0.5) * 0.3;

        const points = [start, mid, end];

        return (
          <Line
            key={`bolt-${i}`}
            points={points}
            color={bolt.intensity > 0.85 ? '#00ff00' : '#ffff00'}
            lineWidth={2}
            transparent
            opacity={bolt.life / 30}
          />
        );
      })}

      {/* Ambient particles for depth */}
      <Points count={200} coherence={torsionField.reduce((a, b) => a + b, 0) / torsionField.length} />
    </group>
  );
}

// Ambient particle field that responds to coherence
function Points({ count, coherence }: { count: number; coherence: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const velocities = [];
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;

      velocities.push({
        x: (Math.random() - 0.5) * 0.01,
        y: (Math.random() - 0.5) * 0.01,
        z: (Math.random() - 0.5) * 0.01
      });

      const color = new THREE.Color();
      color.setHSL(Math.random() * 0.3 + 0.5, 0.7, 0.5);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    return { positions, colors, velocities };
  }, [count]);

  useFrame(() => {
    if (pointsRef.current) {
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;

      // Turbulence based on coherence (low coherence = more chaos)
      const turbulence = 1 - coherence;

      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        const velocity = particles.velocities[i];

        // Add turbulence
        velocity.x += (Math.random() - 0.5) * 0.0005 * turbulence;
        velocity.y += (Math.random() - 0.5) * 0.0005 * turbulence;
        velocity.z += (Math.random() - 0.5) * 0.0005 * turbulence;

        // Update position
        positions[i3] += velocity.x;
        positions[i3 + 1] += velocity.y;
        positions[i3 + 2] += velocity.z;

        // Wrap around
        if (Math.abs(positions[i3]) > 5) positions[i3] *= -0.9;
        if (Math.abs(positions[i3 + 1]) > 5) positions[i3 + 1] *= -0.9;
        if (Math.abs(positions[i3 + 2]) > 5) positions[i3 + 2] *= -0.9;
      }

      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  // Update opacity based on coherence
  useFrame(() => {
    if (pointsRef.current) {
      (pointsRef.current.material as THREE.PointsMaterial).opacity = 0.2 + coherence * 0.4;
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
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
