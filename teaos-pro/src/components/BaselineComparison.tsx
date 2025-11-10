import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { SystemMetrics, BaselineMetrics, ComparisonMetrics } from '../types';

interface BaselineComparisonProps {
  current: SystemMetrics;
  baseline: BaselineMetrics | null;
}

export function BaselineComparison({ current, baseline }: BaselineComparisonProps) {
  if (!baseline) {
    return (
      <div className="glass-strong rounded-xl p-4">
        <h3 className="text-lg font-bold text-purple-400 mb-3">Baseline Comparison</h3>
        <p className="text-sm text-gray-400">
          No baseline set. Current metrics will be used as baseline after first interaction.
        </p>
      </div>
    );
  }

  const comparison: ComparisonMetrics = {
    coherenceDelta: current.coherence - baseline.coherence,
    protectionDelta: current.topologicalProtection - baseline.topologicalProtection,
    stabilityDelta: current.rhombicStability - baseline.rhombicStability,
    balanceDelta: current.channelBalance - baseline.channelBalance,
    overallImprovement: 0
  };

  comparison.overallImprovement = (
    comparison.coherenceDelta +
    comparison.protectionDelta +
    comparison.stabilityDelta +
    comparison.balanceDelta
  ) / 4;

  const MetricDelta = ({ value, label }: { value: number; label: string }) => {
    const getIcon = () => {
      if (Math.abs(value) < 0.01) return <Minus className="w-4 h-4" />;
      return value > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />;
    };

    const getColor = () => {
      if (Math.abs(value) < 0.01) return 'text-gray-400';
      return value > 0 ? 'text-green-400' : 'text-red-400';
    };

    return (
      <div className="flex items-center justify-between p-2 bg-black/20 rounded">
        <span className="text-sm text-gray-300">{label}</span>
        <div className={`flex items-center gap-1 ${getColor()}`}>
          {getIcon()}
          <span className="text-sm font-mono">
            {value > 0 ? '+' : ''}{(value * 100).toFixed(2)}%
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="glass-strong rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-purple-400">Baseline Comparison</h3>
        <div className={`text-xs px-2 py-1 rounded ${
          comparison.overallImprovement > 0.05 ? 'bg-green-500/20 text-green-400' :
          comparison.overallImprovement < -0.05 ? 'bg-red-500/20 text-red-400' :
          'bg-gray-500/20 text-gray-400'
        }`}>
          Overall: {comparison.overallImprovement > 0 ? '+' : ''}
          {(comparison.overallImprovement * 100).toFixed(1)}%
        </div>
      </div>

      <div className="space-y-2">
        <MetricDelta value={comparison.coherenceDelta} label="Coherence" />
        <MetricDelta value={comparison.protectionDelta} label="Protection" />
        <MetricDelta value={comparison.stabilityDelta} label="Stability" />
        <MetricDelta value={comparison.balanceDelta} label="Balance" />
      </div>

      <div className="mt-4 p-2 bg-purple-500/10 border border-purple-500/30 rounded text-xs">
        <div className="text-purple-300 font-semibold mb-1">Baseline Set</div>
        <div className="text-gray-400">
          {new Date(baseline.timestamp).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
