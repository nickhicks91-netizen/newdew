import { motion } from 'framer-motion';
import type { WarpResponse } from '../types';

interface MetricCardProps {
  label: string;
  value: string;
  status?: 'good' | 'marginal' | 'poor' | 'neutral';
  emoji?: string;
  description?: string;
}

function MetricCard({ label, value, status = 'neutral', emoji, description }: MetricCardProps) {
  const statusColors = {
    good: 'border-green-500 bg-green-500/10',
    marginal: 'border-yellow-500 bg-yellow-500/10',
    poor: 'border-red-500 bg-red-500/10',
    neutral: 'border-indigo-500 bg-indigo-500/10',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass rounded-lg p-4 border-2 ${statusColors[status]} transition-all hover:scale-105`}
      title={description}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400 font-medium">{label}</span>
        {emoji && <span className="text-2xl">{emoji}</span>}
      </div>
      <div className="text-2xl font-bold gradient-text">{value}</div>
    </motion.div>
  );
}

export interface MetricsPanelProps {
  result: WarpResponse | null;
  baseline?: number;
}

export default function MetricsPanel({ result, baseline = 0.2634 }: MetricsPanelProps) {
  if (!result) {
    return (
      <div className="glass rounded-xl p-6">
        <p className="text-gray-400 text-center">No metrics yet. Enter text and click "Warp" to analyze.</p>
      </div>
    );
  }

  const getSNRStatus = (snr: number): 'good' | 'marginal' | 'poor' => {
    if (snr > 3.0) return 'good';
    if (snr > 0) return 'marginal';
    return 'poor';
  };

  const getSNREmoji = (snr: number): string => {
    if (snr > 3.0) return '🟢';
    if (snr > 0) return '🟡';
    return '🔴';
  };

  const getAttentionHealthStatus = (entropy: number, maxMean: number): 'good' | 'marginal' | 'poor' => {
    if (entropy < 1.0 && maxMean >= 2 && maxMean <= 5) return 'good';
    if (entropy < 2.0 && maxMean < 10) return 'marginal';
    return 'poor';
  };

  return (
    <div className="space-y-6">
      {/* Qualia Section */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-white">🎨 Decoded Qualia</h3>
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="Valence"
            value={result.valence.toFixed(3)}
            status={result.valence > 0.3 ? 'good' : result.valence < -0.3 ? 'poor' : 'neutral'}
            description="Emotional polarity: -1 (negative) to +1 (positive)"
          />
          <MetricCard
            label="Arousal"
            value={result.arousal.toFixed(3)}
            status={result.arousal > 0.6 ? 'good' : 'neutral'}
            emoji={result.arousal > 0.7 ? '⚡' : result.arousal > 0.4 ? '💫' : '😌'}
            description="Energy level: 0 (calm) to 1 (excited)"
          />
        </div>
      </div>

      {/* Coherence Metrics */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-white">📊 Magnitude-Aware Coherence</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Effective Coherence"
            value={result.effective_coherence.toFixed(4)}
            status={result.effective_coherence > 0.5 ? 'good' : result.effective_coherence > 0.3 ? 'marginal' : 'poor'}
            description="PLV × RMS (prevents low-amplitude noise)"
          />
          <MetricCard
            label={`SNR ${getSNREmoji(result.snr_coherence)}`}
            value={`${result.snr_coherence.toFixed(2)} dB`}
            status={getSNRStatus(result.snr_coherence)}
            description="Signal quality vs baseline"
          />
          <MetricCard
            label="PLV"
            value={result.plv.toFixed(4)}
            status="neutral"
            description="Phase-locking value"
          />
          <MetricCard
            label="RMS Magnitude"
            value={result.rms_magnitude.toFixed(4)}
            status={result.rms_magnitude > 0.6 ? 'good' : 'neutral'}
            emoji={result.rms_magnitude > 0.7 ? '💪' : undefined}
            description="Signal amplitude strength"
          />
        </div>
      </div>

      {/* System Outputs */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-white">⚡ System Outputs</h3>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            label="Classification"
            value={result.classification.toString()}
            status="neutral"
            description="Predicted class"
          />
          <MetricCard
            label="Confidence"
            value={result.confidence.toFixed(3)}
            status={result.confidence > 0.8 ? 'good' : result.confidence > 0.5 ? 'marginal' : 'poor'}
            description="Prediction confidence"
          />
          <MetricCard
            label="Spectral Bin (k)"
            value={result.k_idx.toFixed(1)}
            status="neutral"
            description="ECC auto-selected frequency band"
          />
        </div>
      </div>

      {/* Attention Health */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-white">🧠 Attention Health</h3>
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="Entropy"
            value={`${result.avg_attention_entropy.toFixed(3)} ${
              result.avg_attention_entropy < 1.0 ? '✓' : '⚠'
            }`}
            status={result.avg_attention_entropy < 1.0 ? 'good' : result.avg_attention_entropy < 2.0 ? 'marginal' : 'poor'}
            description="Lower = sharper focus (healthy < 1.0)"
          />
          <MetricCard
            label="Max/Mean Ratio"
            value={`${result.avg_max_mean_ratio.toFixed(2)} ${
              result.avg_max_mean_ratio >= 2 && result.avg_max_mean_ratio <= 5 ? '✓' : '⚠'
            }`}
            status={
              result.avg_max_mean_ratio >= 2 && result.avg_max_mean_ratio <= 5
                ? 'good'
                : result.avg_max_mean_ratio < 10
                ? 'marginal'
                : 'poor'
            }
            description="Collapse detector (healthy: 2-5, collapse: >10)"
          />
        </div>
      </div>

      {/* Quality Summary */}
      <div className="glass rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Overall Signal Quality</span>
          <div className="flex gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              getSNRStatus(result.snr_coherence) === 'good' ? 'snr-good' :
              getSNRStatus(result.snr_coherence) === 'marginal' ? 'snr-marginal' : 'snr-poor'
            }`}>
              {getSNRStatus(result.snr_coherence) === 'good' ? 'Good Signal' :
               getSNRStatus(result.snr_coherence) === 'marginal' ? 'Marginal' : 'Below Baseline'}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              getAttentionHealthStatus(result.avg_attention_entropy, result.avg_max_mean_ratio) === 'good'
                ? 'bg-green-500/20 text-green-400' :
              getAttentionHealthStatus(result.avg_attention_entropy, result.avg_max_mean_ratio) === 'marginal'
                ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {getAttentionHealthStatus(result.avg_attention_entropy, result.avg_max_mean_ratio) === 'good' ? 'Healthy Attention' :
               getAttentionHealthStatus(result.avg_attention_entropy, result.avg_max_mean_ratio) === 'marginal' ? 'Attention Warning' : 'Attention Collapse'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
