// EchoZero API Types

export interface WarpRequest {
  text: string;
}

export interface WarpResponse {
  valence: number;
  arousal: number;
  effective_coherence: number;
  snr_coherence: number;
  plv: number;
  rms_magnitude: number;
  classification: number;
  confidence: number;
  avg_attention_entropy: number;
  avg_max_mean_ratio: number;
  k_idx: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  torch_available: boolean;
  echozero_available: boolean;
  baseline_coherence: number;
}

export interface BaselineResponse {
  baseline_coherence: number;
  baseline_std: number;
  baseline_plv: number;
  baseline_rms: number;
}

export interface AttentionData {
  matrix: number[][];
  entropy: number[];
}

export interface SphereData {
  coupling: number[][];
  activations: number[];
}

export interface PhaseData {
  phases: number[];
  fft: number[];
  frequencies: number[];
}

export type VisualizationMode = 'spheres' | 'attention' | 'phase' | 'harmonic';

export interface AppState {
  inputText: string;
  loading: boolean;
  result: WarpResponse | null;
  baseline: BaselineResponse | null;
  health: HealthResponse | null;
  visualizationMode: VisualizationMode;
  error: string | null;
}
