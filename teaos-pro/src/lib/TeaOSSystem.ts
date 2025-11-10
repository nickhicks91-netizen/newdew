import { RhombicTorsionSpiralhedron } from './RhombicCore';
import type { SystemMetrics } from '../types';

export class HeartbeatCoherence {
  bpm: number;
  phase: number;
  frequency: number;

  constructor(bpm = 60) {
    this.bpm = bpm;
    this.phase = 0;
    this.frequency = bpm / 60;
  }

  tick(dt = 0.05): number {
    this.phase = (this.phase + 2 * Math.PI * this.frequency * dt) % (2 * Math.PI);
    return Math.sin(this.phase);
  }

  modulate(coherence: number): number {
    const heartbeat = (Math.sin(this.phase) + 1) / 2;
    return coherence * (0.8 + 0.4 * heartbeat);
  }
}

export class HebbianLearning {
  weights: Map<string, { count: number; strength: number }>;
  baseRate: number;

  constructor() {
    this.weights = new Map();
    this.baseRate = 0.1;
  }

  update(pattern: string, coherence: number): number {
    const learningRate = this.baseRate * (1 - coherence);

    if (!this.weights.has(pattern)) {
      this.weights.set(pattern, { count: 0, strength: 0 });
    }

    const entry = this.weights.get(pattern)!;
    entry.count++;
    entry.strength += learningRate;

    for (const [key, value] of this.weights.entries()) {
      if (key !== pattern) {
        value.strength *= 0.99;
      }
    }

    return learningRate;
  }

  getStrength(pattern: string): number {
    return this.weights.get(pattern)?.strength || 0;
  }
}

export class TeaOSProSystem {
  core: RhombicTorsionSpiralhedron;
  heartbeat: HeartbeatCoherence;
  learning: HebbianLearning;
  globalCoherence: number;

  constructor() {
    this.core = new RhombicTorsionSpiralhedron(32, 60, 4, 40);
    this.heartbeat = new HeartbeatCoherence(60);
    this.learning = new HebbianLearning();
    this.globalCoherence = 1.0;
  }

  processInput(text: string): SystemMetrics {
    const words = text.toLowerCase().split(/\s+/);
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());

    words.forEach(word => word.length > 2 && this.core.store(word));
    sentences.forEach(sent => this.core.store(sent.trim()));
    this.core.store(text);

    const coreStats = this.core.getStats();
    this.learning.update(text, coreStats.coherence);

    this.globalCoherence = this.heartbeat.modulate(coreStats.coherence);

    return this.getMetrics();
  }

  recall(query: string) {
    return this.core.recall(query);
  }

  getMetrics(): SystemMetrics {
    const coreStats = this.core.getStats();

    return {
      coherence: this.globalCoherence,
      heartbeat: (Math.sin(this.heartbeat.phase) + 1) / 2,
      learningRate: this.learning.baseRate * (1 - this.globalCoherence),
      channelBalance: coreStats.channelBalance,
      torsionPhase: (coreStats.torsionPhase % (2 * Math.PI)) / (2 * Math.PI),
      topologicalProtection: coreStats.topologicalProtection,
      rhombicStability: coreStats.rhombicStability,
      spiralDepth: coreStats.spiralDepth,
      totalPatterns: coreStats.totalPatterns,
      pointsUsed: coreStats.pointsUsed,
      totalPoints: coreStats.totalPoints
    };
  }

  tick(): void {
    this.heartbeat.tick(0.05);
    const coreStats = this.core.getStats();
    this.globalCoherence = this.heartbeat.modulate(coreStats.coherence);
  }
}
