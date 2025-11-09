import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Trail, MeshTransmissionMaterial, Html } from '@react-three/drei';
import * as THREE from 'three';

interface SphereProps {
  position: [number, number, number];
  color: string;
  index: number;
  activation: number;
  coupling: number[];
}

function ResonantSphere({ position, color, index, activation, coupling }: SphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing based on activation
      const scale = 1 + activation * 0.3 * Math.sin(state.clock.elapsedTime * 2);
      meshRef.current.scale.setScalar(scale);

      // Rotation based on octave (higher octaves spin faster)
      meshRef.current.rotation.y += (index + 1) * 0.002;
      meshRef.current.rotation.x += Math.sin(state.clock.elapsedTime * 0.5) * 0.001;
    }

    if (glowRef.current) {
      const glowScale = 1.3 + activation * 0.5 * Math.sin(state.clock.elapsedTime * 3);
      glowRef.current.scale.setScalar(glowScale);
    }
  });

  return (
    <group position={position}>
      {/* Main sphere */}
      <Trail
        width={2}
        length={6}
        color={color}
        attenuation={(t) => t * t}
      >
        <Sphere ref={meshRef} args={[0.5, 32, 32]}>
          <MeshTransmissionMaterial
            color={color}
            thickness={0.5}
            roughness={0.2}
            transmission={0.9}
            ior={1.5}
            chromaticAberration={0.1}
            backside
          />
        </Sphere>
      </Trail>

      {/* Glow effect */}
      <Sphere ref={glowRef} args={[0.5, 16, 16]} scale={1.3}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2 * activation}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Label */}
      <Html distanceFactor={10} position={[0, 0.8, 0]}>
        <div className="text-white text-xs font-mono bg-black/50 px-2 py-1 rounded">
          S{index + 1} ({(activation * 100).toFixed(0)}%)
        </div>
      </Html>
    </group>
  );
}

function ConnectionLine({ start, end, strength }: { start: [number, number, number]; end: [number, number, number]; strength: number }) {
  const points = useMemo(() => {
    return [new THREE.Vector3(...start), new THREE.Vector3(...end)];
  }, [start, end]);

  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial
        color={new THREE.Color(0.5, 0.5 + strength * 0.5, 1)}
        transparent
        opacity={strength * 0.4}
        linewidth={2}
      />
    </line>
  );
}

export interface EightSpheresProps {
  activations?: number[];
  coupling?: number[][];
}

export default function EightSpheres({
  activations = Array(8).fill(0.5),
  coupling = Array(8).fill(0).map(() => Array(8).fill(0.2))
}: EightSpheresProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Arrange spheres in a toroidal configuration (spiralohedron)
  const spherePositions = useMemo(() => {
    const positions: [number, number, number][] = [];
    const radius = 4;
    const height = 6;

    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const spiralHeight = (i / 8) * height - height / 2;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      positions.push([x, spiralHeight, z]);
    }

    return positions;
  }, []);

  const colors = [
    '#ff6b6b', // Sphere 1 - Red (fundamental)
    '#ffa500', // Sphere 2 - Orange
    '#ffd700', // Sphere 3 - Yellow
    '#90ee90', // Sphere 4 - Light Green
    '#4ecdc4', // Sphere 5 - Cyan
    '#6366f1', // Sphere 6 - Indigo
    '#8b5cf6', // Sphere 7 - Violet
    '#ec4899', // Sphere 8 - Pink (highest octave)
  ];

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Spheres */}
      {spherePositions.map((position, index) => (
        <ResonantSphere
          key={`sphere-${index}`}
          position={position}
          color={colors[index]}
          index={index}
          activation={activations[index]}
          coupling={coupling[index]}
        />
      ))}

      {/* Connections between spheres based on coupling strength */}
      {spherePositions.map((start, i) =>
        spherePositions.slice(i + 1).map((end, j) => {
          const couplingStrength = coupling[i]?.[i + j + 1] || 0;
          if (couplingStrength > 0.3) {
            return (
              <ConnectionLine
                key={`connection-${i}-${i + j + 1}`}
                start={start}
                end={end}
                strength={couplingStrength}
              />
            );
          }
          return null;
        })
      )}

      {/* Central toroidal core */}
      <mesh>
        <torusGeometry args={[4, 0.2, 16, 100]} />
        <meshStandardMaterial
          color="#6366f1"
          transparent
          opacity={0.2}
          emissive="#6366f1"
          emissiveIntensity={0.5}
        />
      </mesh>

      {/* Ambient particles */}
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={1000}
            array={new Float32Array(
              Array.from({ length: 1000 * 3 }, () => (Math.random() - 0.5) * 20)
            )}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.05}
          color="#6366f1"
          transparent
          opacity={0.3}
          sizeAttenuation
        />
      </points>
    </group>
  );
}
