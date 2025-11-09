import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

interface NodeProps {
  position: [number, number, number];
  index: number;
  attention: number;
}

function AttentionNode({ position, index, attention }: NodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      // Pulse based on attention strength
      const scale = 0.3 + attention * 0.5 * (1 + Math.sin(state.clock.elapsedTime * 3) * 0.2);
      meshRef.current.scale.setScalar(scale);
    }
  });

  const color = useMemo(() => {
    // Color from blue (low attention) to yellow (high attention)
    const hue = (1 - attention) * 240; // 240 = blue, 60 = yellow
    return new THREE.Color().setHSL(hue / 360, 0.8, 0.6);
  }, [attention]);

  return (
    <group position={position}>
      <Sphere ref={meshRef} args={[0.3, 16, 16]}>
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={attention}
          metalness={0.5}
          roughness={0.2}
        />
      </Sphere>

      {/* Glow */}
      <Sphere args={[0.35, 16, 16]}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={attention * 0.3}
          side={THREE.BackSide}
        />
      </Sphere>

      <Html distanceFactor={8} position={[0, 0.5, 0]}>
        <div className="text-white text-xs font-mono bg-black/70 px-1.5 py-0.5 rounded">
          {index}
        </div>
      </Html>
    </group>
  );
}

function AttentionEdge({
  start,
  end,
  strength,
}: {
  start: [number, number, number];
  end: [number, number, number];
  strength: number;
}) {
  const points = useMemo(() => [start, end], [start, end]);

  if (strength < 0.1) return null;

  return (
    <Line
      points={points}
      color={new THREE.Color().setHSL(0.55, 0.8, 0.5 + strength * 0.3)}
      lineWidth={strength * 3}
      transparent
      opacity={strength * 0.6}
    />
  );
}

export interface AttentionGraphProps {
  attentionMatrix?: number[][];
  numNodes?: number;
}

export default function AttentionGraph({
  attentionMatrix,
  numNodes = 20,
}: AttentionGraphProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Generate random attention matrix if not provided
  const matrix = useMemo(() => {
    if (attentionMatrix) return attentionMatrix;

    const m: number[][] = [];
    for (let i = 0; i < numNodes; i++) {
      m[i] = [];
      for (let j = 0; j < numNodes; j++) {
        if (i === j) {
          m[i][j] = 0;
        } else {
          // Sparse attention with some strong connections
          const strength = Math.random() < 0.3 ? Math.random() * 0.8 + 0.2 : Math.random() * 0.2;
          m[i][j] = strength;
        }
      }
    }
    return m;
  }, [attentionMatrix, numNodes]);

  // Arrange nodes in 3D space using force-directed layout
  const nodePositions = useMemo(() => {
    const positions: [number, number, number][] = [];
    const radius = 5;

    for (let i = 0; i < numNodes; i++) {
      // Spherical distribution
      const phi = Math.acos(2 * (i / (numNodes - 1)) - 1);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i; // Golden angle

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      positions.push([x, y, z]);
    }

    return positions;
  }, [numNodes]);

  // Calculate average attention per node
  const nodeAttention = useMemo(() => {
    return matrix.map((row) => {
      const sum = row.reduce((acc, val) => acc + val, 0);
      return sum / row.length;
    });
  }, [matrix]);

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Draw edges first (so they appear behind nodes) */}
      {nodePositions.map((start, i) =>
        nodePositions.map((end, j) => {
          if (i >= j) return null; // Only draw once per pair
          const strength = (matrix[i][j] + matrix[j][i]) / 2;
          return (
            <AttentionEdge
              key={`edge-${i}-${j}`}
              start={start}
              end={end}
              strength={strength}
            />
          );
        })
      )}

      {/* Draw nodes */}
      {nodePositions.map((position, index) => (
        <AttentionNode
          key={`node-${index}`}
          position={position}
          index={index}
          attention={nodeAttention[index]}
        />
      ))}

      {/* Background sphere */}
      <mesh>
        <sphereGeometry args={[7, 32, 32]} />
        <meshBasicMaterial
          color="#1e293b"
          transparent
          opacity={0.05}
          side={THREE.BackSide}
          wireframe
        />
      </mesh>
    </group>
  );
}
