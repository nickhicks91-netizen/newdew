# TeaOS PRO - 3D Visualization Improvements

## Current State
The visualization shows vertices that glow based on torsion field intensity, but doesn't clearly show the **encoding process** or **memory operations**.

## Proposed Enhancements

### 1. **Input Injection Animation**
**What it shows:** Where the geometric hash lands

```javascript
// In TEAVisualizer class
startEncoding(hashPoint) {
  // Flash the hashed vertex white
  this.vertexMeshes[hashPoint].material.emissive.setHex(0xffffff);

  // Create expanding ring from this point
  const ringGeometry = new THREE.RingGeometry(0.1, 0.15, 32);
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 1,
    side: THREE.DoubleSide
  });
  const ring = new THREE.Mesh(ringGeometry, ringMaterial);
  ring.position.copy(this.vertexMeshes[hashPoint].position);
  this.scene.add(ring);

  // Animate ring expansion and fade
  this.animatedRings.push({ mesh: ring, scale: 1, opacity: 1 });
}

animate() {
  // Update rings
  this.animatedRings.forEach(ring => {
    ring.scale += 0.05;
    ring.opacity -= 0.02;
    ring.mesh.scale.set(ring.scale, ring.scale, 1);
    ring.mesh.material.opacity = ring.opacity;
  });

  // Remove faded rings
  this.animatedRings = this.animatedRings.filter(r => r.opacity > 0);
}
```

### 2. **Propagation Wave Animation**
**What it shows:** Torsion spreading through the lattice over 15 iterations

```javascript
// Modify encode() to return iteration-by-iteration data
encode(message) {
  const iterations = [];

  for (let iteration = 0; iteration < 15; iteration++) {
    // ... existing propagation code ...
    iterations.push([...this.torsionField]); // Save each state
  }

  return { iterations, finalField, ... };
}

// In visualizer
animateIterations(iterations) {
  let currentIteration = 0;

  const interval = setInterval(() => {
    if (currentIteration >= iterations.length) {
      clearInterval(interval);
      return;
    }

    // Update field to show this iteration
    const field = iterations[currentIteration];
    for (let i = 0; i < field.length; i++) {
      this.updateVertex(i, field[i]);
    }

    currentIteration++;
  }, 100); // 100ms per iteration = 1.5s total
}
```

### 3. **Edge Energy Flow**
**What it shows:** Coupling strength and information flow

```javascript
// Create animated particles along edges
class EdgeParticle {
  constructor(edgeIndex, tea) {
    const [v1, v2] = tea.edges[edgeIndex];
    this.start = new THREE.Vector3(...tea.vertices[v1]);
    this.end = new THREE.Vector3(...tea.vertices[v2]);
    this.progress = 0;
    this.speed = 0.02;

    // Particle sphere
    const geometry = new THREE.SphereGeometry(0.05, 8, 8);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 0.8
    });
    this.mesh = new THREE.Mesh(geometry, material);
  }

  update() {
    this.progress += this.speed;
    if (this.progress > 1) this.progress = 0;

    this.mesh.position.lerpVectors(this.start, this.end, this.progress);
  }
}

// During high coupling, spawn edge particles
spawnEdgeParticles() {
  for (let i = 0; i < this.tea.edges.length; i++) {
    const [v1, v2] = this.tea.edges[i];
    const coupling = Math.abs(
      this.tea.quantumStates[v1] * this.tea.quantumStates[v2]
    );

    // Spawn particles proportional to coupling
    if (coupling > 0.5 && Math.random() < coupling * 0.1) {
      this.edgeParticles.push(new EdgeParticle(i, this.tea));
    }
  }
}
```

### 4. **Memory Storage Visualization**
**What it shows:** Where memories are actually stored

```javascript
// Create persistent "memory orbs" at vertices with stored patterns
class MemoryOrb {
  constructor(vertexIndex, tea) {
    const vertex = tea.vertices[vertexIndex];
    const memoryCount = tea.memory[vertexIndex].length;

    // Create orb
    const geometry = new THREE.SphereGeometry(0.08, 16, 16);
    const material = new THREE.MeshStandardMaterial({
      color: 0xffaa00,
      emissive: 0xff6600,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: Math.min(memoryCount * 0.2, 0.8)
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.position.set(vertex[0], vertex[1], vertex[2]);

    // Offset vertically by count (stack memories)
    this.mesh.position.y += memoryCount * 0.1;

    this.age = 0;
  }

  update() {
    // Gentle float animation
    this.age += 0.02;
    this.mesh.position.y += Math.sin(this.age) * 0.001;
  }
}

// Update after each storage
updateMemoryOrbs() {
  // Clear old orbs
  this.memoryOrbs.forEach(orb => this.scene.remove(orb.mesh));
  this.memoryOrbs = [];

  // Create new orbs for all stored memories
  for (let i = 0; i < this.tea.memory.length; i++) {
    if (this.tea.memory[i].length > 0) {
      const orb = new MemoryOrb(i, this.tea);
      this.scene.add(orb.mesh);
      this.memoryOrbs.push(orb);
    }
  }
}
```

### 5. **Channel Grouping & Halos**
**What it shows:** The 4 parallel processing channels

```javascript
// Create subtle halos around each channel's vertices
createChannelHalos() {
  const channelColors = [0xff00ff, 0x00ff41, 0xffaa00, 0x00aaff];

  for (let ch = 0; ch < 4; ch++) {
    const channelVertices = this.tea.points.filter(p => p.channel === ch);

    // Calculate channel center
    const center = new THREE.Vector3();
    channelVertices.forEach(v => {
      center.add(new THREE.Vector3(v.rawX, v.rawY, v.rawZ));
    });
    center.divideScalar(channelVertices.length);

    // Create subtle sphere around channel
    const geometry = new THREE.SphereGeometry(1.5, 32, 32);
    const material = new THREE.MeshBasicMaterial({
      color: channelColors[ch],
      transparent: true,
      opacity: 0.05,
      side: THREE.BackSide
    });

    const halo = new THREE.Mesh(geometry, material);
    halo.position.copy(center);
    this.scene.add(halo);
    this.channelHalos.push(halo);
  }
}

// Update halo intensity based on channel load
updateChannelHalos() {
  for (let ch = 0; ch < 4; ch++) {
    const load = this.tea.channelStates[ch];
    const maxLoad = Math.max(...this.tea.channelStates);
    const intensity = load / (maxLoad + 1);

    this.channelHalos[ch].material.opacity = 0.05 + intensity * 0.15;
  }
}
```

### 6. **Quantum Coupling Bolts**
**What it shows:** Strong phase correlations between nodes

```javascript
// Show temporary lightning between strongly coupled nodes
showQuantumCoupling() {
  // Check all edges for strong coupling
  for (const [v1, v2] of this.tea.edges) {
    const state1 = this.tea.quantumStates[v1];
    const state2 = this.tea.quantumStates[v2];
    const coupling = Math.abs(state1 * state2);

    if (coupling > 0.7) { // Strong coupling threshold
      this.createLightningBolt(v1, v2, coupling);
    }
  }
}

createLightningBolt(v1, v2, intensity) {
  const start = new THREE.Vector3(...this.tea.vertices[v1]);
  const end = new THREE.Vector3(...this.tea.vertices[v2]);

  // Create jagged line
  const points = [];
  const segments = 5;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const pos = new THREE.Vector3().lerpVectors(start, end, t);

    // Add random offset (except endpoints)
    if (i > 0 && i < segments) {
      pos.x += (Math.random() - 0.5) * 0.2;
      pos.y += (Math.random() - 0.5) * 0.2;
      pos.z += (Math.random() - 0.5) * 0.2;
    }

    points.push(pos);
  }

  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({
    color: intensity > 0.85 ? 0x00ff00 : 0xffff00,
    transparent: true,
    opacity: intensity,
    linewidth: 3
  });

  const bolt = new THREE.Line(geometry, material);
  this.scene.add(bolt);

  // Remove after 0.5 seconds
  setTimeout(() => {
    this.scene.remove(bolt);
  }, 500);
}
```

### 7. **Coherence Field Shader**
**What it shows:** Global system coherence as ambient effect

```javascript
// Create particle field that responds to coherence
class CoherenceField {
  constructor(scene) {
    const particleCount = 500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities = [];

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

      velocities.push(new THREE.Vector3(
        (Math.random() - 0.5) * 0.02,
        (Math.random() - 0.5) * 0.02,
        (Math.random() - 0.5) * 0.02
      ));
    }

    geometry.setAttribute('position',
      new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      size: 0.05,
      color: 0x00ffff,
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geometry, material);
    this.velocities = velocities;
    scene.add(this.particles);
  }

  update(coherence) {
    const positions = this.particles.geometry.attributes.position.array;

    // High coherence = organized flow
    // Low coherence = chaotic turbulence
    const turbulence = 1 - coherence / 100;

    for (let i = 0; i < this.velocities.length; i++) {
      const i3 = i * 3;

      // Add turbulence
      this.velocities[i].x += (Math.random() - 0.5) * 0.001 * turbulence;
      this.velocities[i].y += (Math.random() - 0.5) * 0.001 * turbulence;
      this.velocities[i].z += (Math.random() - 0.5) * 0.001 * turbulence;

      // Update position
      positions[i3] += this.velocities[i].x;
      positions[i3 + 1] += this.velocities[i].y;
      positions[i3 + 2] += this.velocities[i].z;

      // Wrap around
      if (Math.abs(positions[i3]) > 10) positions[i3] *= -0.9;
      if (Math.abs(positions[i3 + 1]) > 10) positions[i3 + 1] *= -0.9;
      if (Math.abs(positions[i3 + 2]) > 10) positions[i3 + 2] *= -0.9;
    }

    this.particles.geometry.attributes.position.needsUpdate = true;

    // Update opacity based on coherence
    this.particles.material.opacity = 0.2 + (coherence / 100) * 0.4;
  }
}
```

### 8. **Memory Recall Path Highlighting**
**What it shows:** Retrieval paths during recall operations

```javascript
// When recalling, highlight the search path
visualizeRecall(query) {
  const baseIndex = this.tea.hashToPoint(query);
  const targetPhase = this.tea.computePhaseSignature(query);

  // Highlight base hash point
  this.flashVertex(baseIndex, 0xffff00, 1000);

  // Show search across channels
  for (let ch = 0; ch < 4; ch++) {
    const nearestInChannel = this.tea.findNearestPoint(targetPhase, ch);

    // Draw search ray
    this.drawSearchRay(baseIndex, nearestInChannel);

    // Highlight found vertex
    setTimeout(() => {
      this.flashVertex(nearestInChannel, 0x00ff00, 500);
    }, ch * 200);
  }
}

drawSearchRay(from, to) {
  const start = new THREE.Vector3(...this.tea.vertices[from]);
  const end = new THREE.Vector3(...this.tea.vertices[to]);

  const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
  const material = new THREE.LineDashedMaterial({
    color: 0xffff00,
    dashSize: 0.1,
    gapSize: 0.05,
    transparent: true,
    opacity: 0.6
  });

  const ray = new THREE.Line(geometry, material);
  ray.computeLineDistances();
  this.scene.add(ray);

  // Fade out and remove
  setTimeout(() => {
    this.scene.remove(ray);
  }, 1000);
}
```

## Priority Implementation Order

1. **Input Injection** - Quick win, shows where encoding starts
2. **Memory Orbs** - Makes storage visible and persistent
3. **Channel Halos** - Clarifies parallel processing
4. **Propagation Animation** - Core process visualization
5. **Edge Flow** - Shows coupling dynamics
6. **Quantum Bolts** - Highlights strong correlations
7. **Coherence Field** - Ambient system state
8. **Recall Paths** - Makes retrieval visible

## Performance Considerations

- Limit edge particles to top 20% most active edges
- Use object pooling for frequently created/destroyed elements
- Update memory orbs only on storage, not every frame
- Batch geometry updates where possible
- Use instanced meshes for particles
- Target 60 FPS minimum

## User Controls

Add visualization controls:
- **Detail Level**: Low/Medium/High (affects particle counts)
- **Show Memory**: Toggle memory orbs on/off
- **Show Coupling**: Toggle quantum bolts
- **Show Channels**: Toggle channel halos
- **Animation Speed**: Slow down for study, speed up for demos
