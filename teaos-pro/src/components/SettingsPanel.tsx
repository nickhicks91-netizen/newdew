import { useState, useEffect } from 'react';
import { Settings, Zap, ZapOff, RefreshCw } from 'lucide-react';
import type { OllamaConfig } from '../types';

interface SettingsPanelProps {
  config: OllamaConfig;
  onConfigChange: (config: OllamaConfig) => void;
  onCheckHealth: () => Promise<boolean>;
}

export function SettingsPanel({ config, onConfigChange, onCheckHealth }: SettingsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [checking, setChecking] = useState(false);

  const [localConfig, setLocalConfig] = useState<OllamaConfig>(config);

  useEffect(() => {
    setLocalConfig(config);
  }, [config]);

  const handleCheckHealth = async () => {
    setChecking(true);
    const healthy = await onCheckHealth();
    setIsHealthy(healthy);
    setChecking(false);
  };

  const handleApply = () => {
    onConfigChange(localConfig);
    setIsOpen(false);
  };

  useEffect(() => {
    if (localConfig.enabled) {
      handleCheckHealth();
    }
  }, [localConfig.enabled]);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary flex items-center gap-2"
      >
        <Settings className="w-4 h-4" />
        Settings
      </button>

      {isOpen && (
        <div className="absolute top-12 right-0 w-80 glass-strong rounded-xl p-4 z-50">
          <h3 className="text-lg font-bold text-purple-400 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Ollama Configuration
          </h3>

          <div className="space-y-4">
            {/* Enable Toggle */}
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-300">Enable Ollama</label>
              <button
                onClick={() => setLocalConfig({ ...localConfig, enabled: !localConfig.enabled })}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  localConfig.enabled ? 'bg-purple-600' : 'bg-gray-600'
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    localConfig.enabled ? 'transform translate-x-6' : ''
                  }`}
                />
              </button>
            </div>

            {/* Endpoint */}
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Endpoint</label>
              <input
                type="text"
                value={localConfig.endpoint}
                onChange={(e) => setLocalConfig({ ...localConfig, endpoint: e.target.value })}
                className="w-full bg-black/30 border border-purple-500/30 rounded px-3 py-2 text-sm"
                placeholder="http://localhost:11434"
              />
            </div>

            {/* Model */}
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Model</label>
              <input
                type="text"
                value={localConfig.model}
                onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
                className="w-full bg-black/30 border border-purple-500/30 rounded px-3 py-2 text-sm"
                placeholder="llama2"
              />
            </div>

            {/* Temperature */}
            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Temperature: {localConfig.temperature.toFixed(2)}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={localConfig.temperature}
                onChange={(e) => setLocalConfig({ ...localConfig, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>

            {/* Health Check */}
            {localConfig.enabled && (
              <div className="pt-2 border-t border-purple-500/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">Connection Status</span>
                  <button
                    onClick={handleCheckHealth}
                    disabled={checking}
                    className="text-purple-400 hover:text-purple-300 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${checking ? 'animate-spin' : ''}`} />
                  </button>
                </div>
                {isHealthy !== null && (
                  <div className={`flex items-center gap-2 text-xs ${
                    isHealthy ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {isHealthy ? <Zap className="w-4 h-4" /> : <ZapOff className="w-4 h-4" />}
                    {isHealthy ? 'Connected' : 'Disconnected'}
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <button
                onClick={handleApply}
                className="flex-1 btn-primary py-2"
              >
                Apply
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="flex-1 btn-secondary py-2"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
