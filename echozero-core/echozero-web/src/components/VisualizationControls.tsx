import { motion } from 'framer-motion';
import type { VisualizationMode } from '../types';

export interface VisualizationControlsProps {
  mode: VisualizationMode;
  onModeChange: (mode: VisualizationMode) => void;
  baseline?: number;
}

const modes: { value: VisualizationMode; label: string; icon: string; description: string }[] = [
  {
    value: 'spheres',
    label: '8-Sphere Spiralohedron',
    icon: '🔮',
    description: 'Toroidal resonance with harmonic octaves',
  },
  {
    value: 'attention',
    label: 'Attention Graph',
    icon: '🧠',
    description: 'Node-to-node attention patterns in 3D',
  },
  {
    value: 'phase',
    label: 'Phase Field',
    icon: '🌊',
    description: 'Phase evolution and FFT spectrum',
  },
  {
    value: 'harmonic',
    label: 'Harmonic Coupling',
    icon: '🎵',
    description: 'Inter-sphere resonance matrix',
  },
];

export default function VisualizationControls({
  mode,
  onModeChange,
  baseline = 0.2634,
}: VisualizationControlsProps) {
  return (
    <div className="glass rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Visualization Mode</h3>
        <div className="text-sm text-gray-400">
          Baseline: <span className="text-indigo-400 font-mono">{baseline.toFixed(4)}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {modes.map((m) => (
          <motion.button
            key={m.value}
            onClick={() => onModeChange(m.value)}
            className={`p-4 rounded-lg border-2 transition-all ${
              mode === m.value
                ? 'border-echo-primary bg-echo-primary/20 shadow-lg'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="text-3xl mb-2">{m.icon}</div>
            <div className="text-sm font-semibold text-white mb-1">{m.label}</div>
            <div className="text-xs text-gray-400">{m.description}</div>
          </motion.button>
        ))}
      </div>

      <div className="text-xs text-gray-500 space-y-1">
        <p>🖱️ <strong>Controls:</strong> Drag to rotate • Scroll to zoom • Right-click to pan</p>
        <p>💫 Visualizations update in real-time with model outputs</p>
      </div>
    </div>
  );
}
