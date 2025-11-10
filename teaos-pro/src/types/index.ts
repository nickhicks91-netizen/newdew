export interface Point3D {
  id: number;
  channel: number;
  x: number;
  y: number;
  z: number;
  rawX: number;
  rawY: number;
  rawZ: number;
  theta: number;
  phi: number;
  torsion: number;
  rhombicPhase: number;
  t: number;
}

export interface MemoryEntry {
  pattern: string;
  phase: number[];
  timestamp: number;
  torsion: number;
}

export interface Neighbor {
  id: number;
  distance: number;
  torsionAlignment: number;
}

export interface CoreStats {
  coherence: number;
  totalPatterns: number;
  channelBalance: number;
  torsionPhase: number;
  topologicalProtection: number;
  rhombicStability: number;
  spiralDepth: number;
  pointsUsed: number;
  totalPoints: number;
}

export interface SystemMetrics extends CoreStats {
  heartbeat: number;
  learningRate: number;
}

export interface BaselineMetrics {
  coherence: number;
  topologicalProtection: number;
  rhombicStability: number;
  channelBalance: number;
  timestamp: number;
}

export interface ComparisonMetrics {
  coherenceDelta: number;
  protectionDelta: number;
  stabilityDelta: number;
  balanceDelta: number;
  overallImprovement: number;
}

export interface OllamaConfig {
  enabled: boolean;
  endpoint: string;
  model: string;
  temperature: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metrics?: SystemMetrics;
}

export interface OllamaResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
}
