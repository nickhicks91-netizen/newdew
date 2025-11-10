import type { Point3D, MemoryEntry, Neighbor, CoreStats } from '../types';

export class RhombicTorsionSpiralhedron {
  dims: number;
  phi: number;
  torsionAngle: number;
  channels: number;
  pointsPerChannel: number;
  points: Point3D[];
  memory: MemoryEntry[][];
  adjacency: Map<number, Neighbor[]>;
  phaseState: number[];
  coherence: number;
  torsionPhase: number;
  channelStates: number[];
  decayRate: number;
  thermalNoise: number;
  quantumFluctuation: number;

  constructor(dims = 32, torsionAngle = 60, channels = 4, pointsPerChannel = 40) {
    this.dims = dims;
    this.phi = (1 + Math.sqrt(5)) / 2;
    this.torsionAngle = torsionAngle * Math.PI / 180;
    this.channels = channels;
    this.pointsPerChannel = pointsPerChannel;

    this.points = this.generateRhombicLatticePoints();
    this.memory = new Array(this.points.length).fill(null).map(() => []);
    this.adjacency = this.computeRhombicAdjacency();

    this.phaseState = new Array(dims).fill(0);
    this.coherence = 1.0;
    this.torsionPhase = 0;
    this.channelStates = new Array(channels).fill(0);
    this.decayRate = 0.001;
    this.thermalNoise = 0;
    this.quantumFluctuation = 0;
  }

  generateRhombicLatticePoints(): Point3D[] {
    const points: Point3D[] = [];

    for (let ch = 0; ch < this.channels; ch++) {
      const channelOffset = (2 * Math.PI * ch) / this.channels;

      for (let i = 0; i < this.pointsPerChannel; i++) {
        const t = i / this.pointsPerChannel;
        const turns = 5;

        const theta = t * 2 * Math.PI * turns + channelOffset;
        const torsion = t * this.torsionAngle * turns;

        const rhombicPhase1 = Math.cos(theta * 3);
        const rhombicPhase2 = Math.cos(theta * 3 + Math.PI / 3);
        const rhombicMod = 0.3 * (rhombicPhase1 + rhombicPhase2);

        const R = 1.0;
        const r = 0.3 + rhombicMod;

        const phi = theta + torsion;

        const x = (R + r * Math.cos(phi)) * Math.cos(theta);
        const y = (R + r * Math.cos(phi)) * Math.sin(theta);
        const z = r * Math.sin(phi) + 0.2 * Math.sin(theta * 4);

        const latticeScale = 3;
        const lx = Math.round(x * latticeScale) / latticeScale;
        const ly = Math.round(y * latticeScale) / latticeScale;
        const lz = Math.round(z * latticeScale) / latticeScale;

        points.push({
          id: ch * this.pointsPerChannel + i,
          channel: ch,
          x: lx, y: ly, z: lz,
          rawX: x, rawY: y, rawZ: z,
          theta: theta,
          phi: phi,
          torsion: torsion,
          rhombicPhase: rhombicPhase1 + rhombicPhase2,
          t: t
        });
      }
    }

    return points;
  }

  computeRhombicAdjacency(): Map<number, Neighbor[]> {
    const adjacency = new Map<number, Neighbor[]>();

    for (let i = 0; i < this.points.length; i++) {
      const p1 = this.points[i];
      const neighbors: Neighbor[] = [];

      for (let j = 0; j < this.points.length; j++) {
        if (i === j) continue;

        const p2 = this.points[j];

        const dx = Math.abs(p2.x - p1.x);
        const dy = Math.abs(p2.y - p1.y);
        const dz = Math.abs(p2.z - p1.z);

        const rhombicDist = dx * (1 + 0.5 * Math.cos(0)) +
                           dy * (1 + 0.5 * Math.cos(Math.PI / 3)) +
                           dz * (1 + 0.5 * Math.cos(2 * Math.PI / 3));

        if (rhombicDist > 0.05 && rhombicDist < 0.8) {
          neighbors.push({
            id: j,
            distance: rhombicDist,
            torsionAlignment: Math.cos(p2.torsion - p1.torsion)
          });
        }
      }

      neighbors.sort((a, b) => a.distance - b.distance);
      adjacency.set(i, neighbors.slice(0, 6));
    }

    return adjacency;
  }

  hashToPoint(pattern: string): number {
    let hash = 0;
    for (let i = 0; i < pattern.length; i++) {
      hash = ((hash << 5) - hash) + pattern.charCodeAt(i);
      hash = hash & hash;
    }

    const channel = Math.abs(hash) % this.channels;
    const offset = Math.abs(hash >> 8) % this.pointsPerChannel;

    return channel * this.pointsPerChannel + offset;
  }

  findNearestPoint(phaseSignature: number[], preferredChannel: number | null = null): number {
    let minDist = Infinity;
    let nearest = 0;

    const searchPoints = preferredChannel !== null
      ? this.points.filter(p => p.channel === preferredChannel)
      : this.points;

    for (const point of searchPoints) {
      let spatialDist = 0;
      for (let d = 0; d < Math.min(3, phaseSignature.length); d++) {
        const coord = d === 0 ? point.x : (d === 1 ? point.y : point.z);
        spatialDist += Math.pow(phaseSignature[d] - coord, 2);
      }
      spatialDist = Math.sqrt(spatialDist);

      let phaseDist = 0;
      for (let d = 3; d < phaseSignature.length; d++) {
        phaseDist += Math.pow(phaseSignature[d], 2);
      }
      phaseDist = Math.sqrt(phaseDist);

      const torsionAlignment = Math.cos(point.torsion - this.torsionPhase);
      const totalDist = (spatialDist + phaseDist) * (1 - 0.2 * torsionAlignment);

      if (totalDist < minDist) {
        minDist = totalDist;
        nearest = point.id;
      }
    }

    return nearest;
  }

  store(pattern: string): { success: boolean; index: number; point: Point3D } {
    const baseIndex = this.hashToPoint(pattern);
    const phaseSignature = this.computePhaseSignature(pattern);

    let targetIndex = this.findNearestPoint(phaseSignature, this.points[baseIndex].channel);

    const existing = this.memory[targetIndex].find(e => e.pattern === pattern);

    if (existing) {
      let walkIndex = targetIndex;
      let walked = 0;
      const maxWalk = 20;

      while (this.memory[walkIndex].length > 4 && walked < maxWalk) {
        const neighbors = this.adjacency.get(walkIndex) || [];

        if (neighbors.length === 0) break;

        let bestNeighbor = neighbors[0].id;
        let minLoad = this.memory[neighbors[0].id].length;

        for (const neighbor of neighbors) {
          const load = this.memory[neighbor.id].length;
          if (load < minLoad) {
            minLoad = load;
            bestNeighbor = neighbor.id;
          }
        }

        walkIndex = bestNeighbor;
        walked++;
      }

      targetIndex = walkIndex;
    }

    this.memory[targetIndex].push({
      pattern,
      phase: phaseSignature,
      timestamp: Date.now(),
      torsion: this.torsionPhase
    });

    const point = this.points[targetIndex];
    this.channelStates[point.channel]++;
    this.torsionPhase += 0.1;

    this.updateCoherence();

    return {
      success: true,
      index: targetIndex,
      point: point
    };
  }

  recall(pattern: string): (MemoryEntry & { score: number; confidence: number }) | null {
    const targetPhase = this.computePhaseSignature(pattern);

    const candidates: (MemoryEntry & { score: number; confidence: number })[] = [];

    for (let ch = 0; ch < this.channels; ch++) {
      const nearestInChannel = this.findNearestPoint(targetPhase, ch);

      for (const entry of this.memory[nearestInChannel]) {
        const resonance = this.phaseResonance(targetPhase, entry.phase);
        const torsionAlign = Math.cos(entry.torsion - this.torsionPhase);
        const score = resonance * (1 + 0.2 * torsionAlign);

        candidates.push({
          ...entry,
          score: score,
          confidence: (score + 1) / 2
        });
      }
    }

    candidates.sort((a, b) => b.score - a.score);
    return candidates.length > 0 ? candidates[0] : null;
  }

  computePhaseSignature(pattern: string): number[] {
    const signature = new Array(this.dims).fill(0);

    for (let i = 0; i < pattern.length; i++) {
      const charCode = pattern.charCodeAt(i);
      const dim = i % this.dims;

      const localTorsion = (i / pattern.length) * this.torsionAngle;
      const rhombicMod = Math.cos(i * Math.PI / 3);
      const decay = Math.exp(-i / (pattern.length * this.phi));

      signature[dim] += charCode * Math.cos(localTorsion) * (1 + 0.3 * rhombicMod) * decay;
    }

    const magnitude = Math.sqrt(signature.reduce((sum, x) => sum + x * x, 0));
    return signature.map(x => x / (magnitude + 1e-10));
  }

  phaseResonance(phase1: number[], phase2: number[]): number {
    let dotProduct = 0;
    for (let i = 0; i < phase1.length; i++) {
      dotProduct += phase1[i] * phase2[i];
    }

    const torsionBonus = Math.cos(this.torsionPhase) * 0.15;
    const rhombicResonance = Math.cos(this.torsionPhase * 3) * 0.1;

    return dotProduct * (1 + torsionBonus + rhombicResonance);
  }

  updateCoherence(): void {
    let totalResonance = 0;
    let torsionCoherence = 0;
    let rhombicCoherence = 0;
    let count = 0;

    for (let i = 0; i < this.points.length; i++) {
      const point = this.points[i];

      for (const entry of this.memory[i]) {
        const resonance = this.phaseResonance(this.phaseState, entry.phase);
        totalResonance += resonance;

        const torsionAlign = Math.cos(point.torsion - this.torsionPhase);
        torsionCoherence += torsionAlign;

        const neighbors = this.adjacency.get(i) || [];
        let neighborCoherence = 0;
        for (const neighbor of neighbors) {
          if (this.memory[neighbor.id].length > 0) {
            neighborCoherence += neighbor.torsionAlignment;
          }
        }
        rhombicCoherence += neighborCoherence / (neighbors.length + 1);

        count++;
      }
    }

    if (count > 0) {
      this.coherence = (1 + totalResonance / count) / 2;

      const torsionBonus = (torsionCoherence / count) * 0.25;
      const rhombicBonus = (rhombicCoherence / count) * 0.1;
      const channelBonus = this.getChannelBalance() * 0.15;

      this.coherence = Math.min(1, this.coherence + torsionBonus + rhombicBonus + channelBonus);
    } else {
      this.coherence = 1.0;
    }

    this.coherence *= (1 - this.decayRate);
    this.coherence *= (1 - this.thermalNoise * 0.06);
    this.coherence *= (1 - this.quantumFluctuation * 0.03);
    this.coherence = Math.max(0, Math.min(1, this.coherence));
  }

  getChannelBalance(): number {
    const avg = this.channelStates.reduce((a, b) => a + b, 0) / this.channels;
    const variance = this.channelStates.reduce((sum, load) => {
      return sum + Math.pow(load - avg, 2);
    }, 0) / this.channels;
    return Math.exp(-variance / (avg + 1));
  }

  getTopologicalProtection(): number {
    let protection = 0;
    let count = 0;

    for (let i = 0; i < this.points.length; i++) {
      for (const entry of this.memory[i]) {
        const torsionAlign = Math.cos(entry.torsion - this.torsionPhase);
        protection += (torsionAlign + 1) / 2;
        count++;
      }
    }

    return count > 0 ? protection / count : 1.0;
  }

  getRhombicStability(): number {
    let stability = 0;
    let count = 0;

    for (let i = 0; i < this.points.length; i++) {
      if (this.memory[i].length === 0) continue;

      const neighbors = this.adjacency.get(i) || [];
      let neighborLoad = 0;

      for (const neighbor of neighbors) {
        neighborLoad += this.memory[neighbor.id].length;
      }

      const avgNeighborLoad = neighborLoad / (neighbors.length + 1);
      const balance = 1 / (1 + Math.abs(this.memory[i].length - avgNeighborLoad));

      stability += balance;
      count++;
    }

    return count > 0 ? stability / count : 1.0;
  }

  getSpiralDepth(): number {
    const maxIndex = Math.max(...this.memory.map((m, i) => m.length > 0 ? i : 0));
    return maxIndex / this.points.length;
  }

  getStats(): CoreStats {
    const totalPatterns = this.memory.reduce((sum, point) => sum + point.length, 0);

    return {
      coherence: this.coherence,
      totalPatterns,
      channelBalance: this.getChannelBalance(),
      torsionPhase: this.torsionPhase,
      topologicalProtection: this.getTopologicalProtection(),
      rhombicStability: this.getRhombicStability(),
      spiralDepth: this.getSpiralDepth(),
      pointsUsed: this.memory.filter(m => m.length > 0).length,
      totalPoints: this.points.length
    };
  }
}
