import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Scene from './components/Scene';
import InputPanel from './components/InputPanel';
import MetricsPanel from './components/MetricsPanel';
import VisualizationControls from './components/VisualizationControls';
import api from './api/client';
import type { AppState, VisualizationMode } from './types';

function App() {
  const [state, setState] = useState<AppState>({
    inputText: '',
    loading: false,
    result: null,
    baseline: null,
    health: null,
    visualizationMode: 'spheres',
    error: null,
  });

  const [showMetrics, setShowMetrics] = useState(false);

  // Load baseline and health on mount
  useEffect(() => {
    const init = async () => {
      try {
        const [health, baseline] = await Promise.all([api.health(), api.baseline()]);
        setState((prev) => ({ ...prev, health, baseline }));
      } catch (error) {
        console.error('Failed to load initial data:', error);
        // Use demo mode if API is not available
      }
    };
    init();
  }, []);

  const handleSubmit = async (text: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null, inputText: text }));

    try {
      // Try real API first, fall back to demo
      const result = await api.warp({ text }).catch(() => api.warpDemo({ text }));
      setState((prev) => ({ ...prev, result, loading: false }));
      setShowMetrics(true);
    } catch (error) {
      console.error('Warp failed:', error);
      setState((prev) => ({
        ...prev,
        loading: false,
        error: 'Failed to process text. Please try again.',
      }));
    }
  };

  const handleModeChange = (mode: VisualizationMode) => {
    setState((prev) => ({ ...prev, visualizationMode: mode }));
  };

  return (
    <div className="w-screen h-screen overflow-hidden bg-echo-dark text-white">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute top-0 left-0 right-0 z-50 glass border-b border-gray-700/50"
      >
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-4xl animate-spin-slow">🌀</div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">EchoZero</h1>
              <p className="text-xs text-gray-400">Resonant AI Visualization v1.0.0</p>
            </div>
          </div>

          {state.health && (
            <div className="flex items-center gap-4">
              <div className="text-sm">
                <span className="text-gray-400">Status:</span>{' '}
                <span className={state.health.model_loaded ? 'text-green-400' : 'text-yellow-400'}>
                  {state.health.model_loaded ? '● Online' : '○ Demo Mode'}
                </span>
              </div>
              {state.baseline && (
                <div className="text-sm">
                  <span className="text-gray-400">Baseline:</span>{' '}
                  <span className="text-indigo-400 font-mono">
                    {state.baseline.baseline_coherence.toFixed(4)}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="h-full pt-20 flex">
        {/* Left Panel - Input & Controls */}
        <motion.aside
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-96 p-6 space-y-6 overflow-y-auto"
        >
          <InputPanel onSubmit={handleSubmit} loading={state.loading} />
          <VisualizationControls
            mode={state.visualizationMode}
            onModeChange={handleModeChange}
            baseline={state.baseline?.baseline_coherence}
          />
        </motion.aside>

        {/* Center - 3D Visualization */}
        <div className="flex-1 relative">
          <Scene mode={state.visualizationMode} result={state.result} />

          {/* Error Toast */}
          <AnimatePresence>
            {state.error && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                className="absolute bottom-6 left-1/2 transform -translate-x-1/2 glass border-2 border-red-500 rounded-lg p-4 max-w-md"
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <div className="font-semibold text-red-400">Error</div>
                    <div className="text-sm text-gray-300">{state.error}</div>
                  </div>
                  <button
                    onClick={() => setState((prev) => ({ ...prev, error: null }))}
                    className="ml-auto text-gray-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Metrics Toggle */}
          <button
            onClick={() => setShowMetrics(!showMetrics)}
            className="absolute top-6 right-6 btn-secondary"
          >
            {showMetrics ? '← Hide Metrics' : 'Show Metrics →'}
          </button>
        </div>

        {/* Right Panel - Metrics */}
        <AnimatePresence>
          {showMetrics && (
            <motion.aside
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              className="w-[500px] p-6 overflow-y-auto bg-echo-dark/90 backdrop-blur border-l border-gray-700/50"
            >
              <MetricsPanel result={state.result} baseline={state.baseline?.baseline_coherence} />
            </motion.aside>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Info */}
      <div className="absolute bottom-4 left-4 text-xs text-gray-500">
        <p>🔮 8-Sphere Spiralohedron | 🧠 TEA-Penrose Attention | 🌊 Phase-Locked Resonance</p>
      </div>
    </div>
  );
}

export default App;
