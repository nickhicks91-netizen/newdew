import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface PhaseFieldProps {
  phaseData?: number[];
  dim?: number;
}

export default function PhaseField({ phaseData, dim = 128 }: PhaseFieldProps) {
  const groupRef = useRef<THREE.Group>(null);
  const waveRef = useRef<THREE.Mesh>(null);

  // Generate phase data if not provided
  const phases = useMemo(() => {
    if (phaseData) return phaseData;

    // Generate sample phase data (sine waves with harmonics)
    const data: number[] = [];
    for (let i = 0; i < dim; i++) {
      const t = (i / dim) * Math.PI * 4;
      const phase =
        Math.sin(t * 1) * 0.5 +
        Math.sin(t * 3) * 0.3 +
        Math.sin(t * 5) * 0.2 +
        Math.random() * 0.1;
      data.push(phase);
    }
    return data;
  }, [phaseData, dim]);

  // Create 3D wave surface from phase data
  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(10, 10, dim - 1, dim - 1);
    const positions = geo.attributes.position.array as Float32Array;

    // Apply phase data to z-coordinates
    for (let i = 0; i < positions.length; i += 3) {
      const index = Math.floor(i / 3);
      const phase = phases[index % phases.length] || 0;
      positions[i + 2] = phase * 2; // Z displacement
    }

    geo.attributes.position.needsUpdate = true;
    geo.computeVertexNormals();

    return geo;
  }, [phases, dim]);

  // Create color gradient based on phase
  const colorAttribute = useMemo(() => {
    const colors = new Float32Array(dim * dim * 3);

    for (let i = 0; i < dim * dim; i++) {
      const phase = phases[i % phases.length] || 0;
      const normalizedPhase = (phase + 1) / 2; // Normalize to 0-1

      // Color gradient from indigo to pink
      const color = new THREE.Color().setHSL(
        0.7 - normalizedPhase * 0.4, // Hue: 0.7 (blue) to 0.3 (pink)
        0.8,
        0.5 + normalizedPhase * 0.3
      );

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    return new THREE.Float32BufferAttribute(colors, 3);
  }, [phases, dim]);

  // Create phase vector arrows
  const arrows = useMemo(() => {
    const arrowData: { position: [number, number, number]; direction: [number, number, number]; strength: number }[] = [];
    const gridSize = 16;
    const spacing = 10 / gridSize;

    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        const index = Math.floor((x / gridSize) * phases.length);
        const phase = phases[index] || 0;

        const px = x * spacing - 5;
        const py = y * spacing - 5;
        const pz = phase * 2;

        // Direction based on phase gradient
        const nextPhase = phases[Math.min(index + 1, phases.length - 1)] || 0;
        const gradient = nextPhase - phase;

        arrowData.push({
          position: [px, py, pz],
          direction: [Math.cos(phase), Math.sin(phase), gradient],
          strength: Math.abs(phase),
        });
      }
    }

    return arrowData;
  }, [phases]);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.z += 0.001;
    }

    if (waveRef.current && geometry) {
      const positions = geometry.attributes.position.array as Float32Array;
      const time = state.clock.elapsedTime;

      // Animate wave
      for (let i = 0; i < positions.length; i += 3) {
        const index = Math.floor(i / 3);
        const phase = phases[index % phases.length] || 0;
        const wave = Math.sin(time * 2 + phase * 3) * 0.3;
        positions[i + 2] = phase * 2 + wave;
      }

      geometry.attributes.position.needsUpdate = true;
      geometry.computeVertexNormals();
    }
  });

  return (
    <group ref={groupRef}>
      {/* Main wave surface */}
      <mesh ref={waveRef} geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
        <meshStandardMaterial
          vertexColors
          side={THREE.DoubleSide}
          wireframe={false}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Wireframe overlay */}
      <mesh geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
        <meshBasicMaterial
          color="#6366f1"
          wireframe
          transparent
          opacity={0.2}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Phase vectors */}
      {arrows.map((arrow, i) => (
        <group key={i} position={arrow.position}>
          <arrowHelper
            args={[
              new THREE.Vector3(...arrow.direction).normalize(),
              new THREE.Vector3(0, 0, 0),
              0.5,
              new THREE.Color().setHSL(arrow.strength, 0.8, 0.6),
              0.2,
              0.1,
            ]}
          />
        </group>
      ))}

      {/* FFT spectrum visualization */}
      <group position={[0, 0, -6]}>
        {phases.slice(0, 64).map((phase, i) => {
          const magnitude = Math.abs(phase);
          const x = (i / 64) * 10 - 5;
          const height = magnitude * 3;

          return (
            <mesh key={`fft-${i}`} position={[x, height / 2, 0]}>
              <boxGeometry args={[0.1, height, 0.1]} />
              <meshStandardMaterial
                color={new THREE.Color().setHSL((1 - magnitude) * 0.7, 0.8, 0.6)}
                emissive={new THREE.Color().setHSL((1 - magnitude) * 0.7, 0.8, 0.4)}
                emissiveIntensity={magnitude}
              />
            </mesh>
          );
        })}
      </group>

      {/* Ambient particles showing phase flow */}
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={500}
            array={new Float32Array(
              Array.from({ length: 500 * 3 }, (_, i) => {
                const index = Math.floor(i / 3);
                const phase = phases[index % phases.length] || 0;
                if (i % 3 === 0) return (Math.random() - 0.5) * 12; // x
                if (i % 3 === 1) return (Math.random() - 0.5) * 12; // y
                return phase * 2; // z
              })
            )}
            itemSize={3}
          />
          <bufferAttribute attach="attributes-color" count={500} array={colorAttribute.array} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial size={0.08} vertexColors transparent opacity={0.6} sizeAttenuation />
      </points>
    </group>
  );
}
