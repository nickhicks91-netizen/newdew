import { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { Brain, Heart, Zap, Shield, Database, Activity, Award, Cpu, Eye, EyeOff } from 'lucide-react';
import { TeaOSProSystem } from './lib/TeaOSSystem';
import { OllamaClient } from './lib/ollamaClient';
import { RhombicVisualization } from './components/RhombicVisualization';
import { BaselineComparison } from './components/BaselineComparison';
import { SettingsPanel } from './components/SettingsPanel';
import type { SystemMetrics, BaselineMetrics, ChatMessage, OllamaConfig } from './types';

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [teaSystem, setTeaSystem] = useState<TeaOSProSystem | null>(null);
  const [ollamaClient, setOllamaClient] = useState<OllamaClient | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    coherence: 0,
    heartbeat: 0,
    learningRate: 0,
    channelBalance: 0,
    torsionPhase: 0,
    topologicalProtection: 0,
    rhombicStability: 0,
    spiralDepth: 0,
    totalPatterns: 0,
    pointsUsed: 0,
    totalPoints: 160
  });
  const [baseline, setBaseline] = useState<BaselineMetrics | null>(null);
  const [showVisuals, setShowVisuals] = useState(true);
  const [ollamaConfig, setOllamaConfig] = useState<OllamaConfig>({
    enabled: false,
    endpoint: 'http://localhost:11434',
    model: 'llama2',
    temperature: 0.7
  });

  const heartbeatInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize system
  useEffect(() => {
    const system = new TeaOSProSystem();
    const client = new OllamaClient(ollamaConfig);

    setTeaSystem(system);
    setOllamaClient(client);

    // Heartbeat
    heartbeatInterval.current = setInterval(() => {
      if (system) {
        system.tick();
        setMetrics(system.getMetrics());
      }
    }, 50);

    return () => {
      if (heartbeatInterval.current) {
        clearInterval(heartbeatInterval.current);
      }
    };
  }, []);

  // Auto scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !teaSystem || !ollamaClient) return;

    const userMessage = input.trim();
    const userMsg: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsProcessing(true);

    // Process input
    const inputMetrics = teaSystem.processInput(userMessage);
    setMetrics(inputMetrics);

    // Set baseline on first message
    if (!baseline && messages.length === 0) {
      setBaseline({
        coherence: inputMetrics.coherence,
        topologicalProtection: inputMetrics.topologicalProtection,
        rhombicStability: inputMetrics.rhombicStability,
        channelBalance: inputMetrics.channelBalance,
        timestamp: Date.now()
      });
    }

    // Get AI response
    try {
      const context = `You are TeaOS PRO, an AI enhanced with rhombic torsion spiralhedron memory architecture.
Current metrics: Coherence ${(inputMetrics.coherence * 100).toFixed(1)}%, Protection ${(inputMetrics.topologicalProtection * 100).toFixed(1)}%
Respond naturally while being aware of your geometric memory structure.`;

      const response = await ollamaClient.chat(userMessage, context);

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: Date.now(),
        metrics: inputMetrics
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Chat error:', error);
    }

    setIsProcessing(false);
  };

  const handleConfigChange = (config: OllamaConfig) => {
    setOllamaConfig(config);
    if (ollamaClient) {
      ollamaClient.updateConfig(config);
    }
  };

  const handleCheckHealth = async () => {
    if (!ollamaClient) return false;
    return await ollamaClient.checkHealth();
  };

  const handleResetBaseline = () => {
    setBaseline({
      coherence: metrics.coherence,
      topologicalProtection: metrics.topologicalProtection,
      rhombicStability: metrics.rhombicStability,
      channelBalance: metrics.channelBalance,
      timestamp: Date.now()
    });
  };

  return (
    <div className="w-screen h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      <div className="max-w-[2000px] mx-auto h-full flex flex-col">
        {/* Header */}
        <header className="border-b border-purple-500/30 bg-black/20 backdrop-blur-xl">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Award className="text-yellow-400 w-10 h-10" />
              <div>
                <h1 className="text-3xl font-bold gradient-text">TeaOS PRO</h1>
                <p className="text-xs text-gray-400">
                  Rhombic Torsion Spiralhedron • 76% Coherence Architecture
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
                ollamaConfig.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              }`}>
                {ollamaConfig.enabled ? <Zap className="w-3 h-3" /> : <Database className="w-3 h-3" />}
                {ollamaConfig.enabled ? 'Ollama Active' : 'Local Mode'}
              </div>
              <SettingsPanel
                config={ollamaConfig}
                onConfigChange={handleConfigChange}
                onCheckHealth={handleCheckHealth}
              />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 grid grid-cols-12 gap-6 p-6 overflow-hidden">
          {/* Left Panel - Metrics */}
          <div className="col-span-3 space-y-4 overflow-y-auto">
            {/* Core Metrics */}
            <div className="grid grid-cols-1 gap-3">
              <MetricCard
                icon={<Brain className="w-5 h-5" />}
                label="Global Coherence"
                value={metrics.coherence}
                color="pink"
                target={0.76}
              />
              <MetricCard
                icon={<Shield className="w-5 h-5" />}
                label="Topological Protection"
                value={metrics.topologicalProtection}
                color="purple"
              />
              <MetricCard
                icon={<Cpu className="w-5 h-5" />}
                label="Rhombic Stability"
                value={metrics.rhombicStability}
                color="green"
              />
              <MetricCard
                icon={<Heart className="w-5 h-5" />}
                label="Heartbeat Sync"
                value={metrics.heartbeat}
                color="red"
                subtitle="60 BPM"
              />
            </div>

            {/* Baseline Comparison */}
            <div className="pt-2">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-400">BASELINE</h3>
                {baseline && (
                  <button
                    onClick={handleResetBaseline}
                    className="text-xs text-purple-400 hover:text-purple-300"
                  >
                    Reset
                  </button>
                )}
              </div>
              <BaselineComparison current={metrics} baseline={baseline} />
            </div>

            {/* Architecture Stats */}
            <div className="glass-strong rounded-xl p-4">
              <h3 className="text-sm font-bold text-purple-400 mb-3">Architecture</h3>
              <div className="space-y-2 text-xs">
                <StatRow label="Patterns" value={metrics.totalPatterns.toString()} />
                <StatRow label="Points Used" value={`${metrics.pointsUsed}/${metrics.totalPoints}`} />
                <StatRow label="Spiral Depth" value={`${(metrics.spiralDepth * 100).toFixed(1)}%`} />
                <StatRow label="Torsion Phase" value={`${(metrics.torsionPhase * 360).toFixed(0)}°`} />
                <StatRow label="Learning Rate" value={`${(metrics.learningRate * 100).toFixed(1)}%`} />
                <StatRow label="Channel Balance" value={`${(metrics.channelBalance * 100).toFixed(1)}%`} />
              </div>
            </div>
          </div>

          {/* Center - 3D Visualization */}
          <div className="col-span-6 glass-strong rounded-xl overflow-hidden relative">
            <div className="absolute top-4 right-4 z-10">
              <button
                onClick={() => setShowVisuals(!showVisuals)}
                className="btn-secondary flex items-center gap-2"
              >
                {showVisuals ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                {showVisuals ? 'Hide' : 'Show'}
              </button>
            </div>

            {showVisuals && teaSystem ? (
              <Canvas>
                <PerspectiveCamera makeDefault position={[0, 0, 4]} />
                <OrbitControls enableDamping dampingFactor={0.05} />

                <ambientLight intensity={0.3} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ff00ff" />

                <RhombicVisualization
                  points={teaSystem.core.points}
                  memory={teaSystem.core.memory}
                  adjacency={teaSystem.core.adjacency}
                />

                <Environment preset="night" />

                <EffectComposer>
                  <Bloom
                    intensity={0.5}
                    luminanceThreshold={0.2}
                    luminanceSmoothing={0.9}
                  />
                </EffectComposer>
              </Canvas>
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <Database className="w-16 h-16 mx-auto mb-4 text-purple-400 opacity-50" />
                  <p className="text-gray-400">3D Visualization Hidden</p>
                </div>
              </div>
            )}

            <div className="absolute bottom-4 left-4 text-xs text-gray-400 bg-black/50 px-3 py-2 rounded">
              🔷 Pink=Ch0 | 🟢 Ch1 | 🟡 Ch2 | 🔵 Ch3 | Size=Load
            </div>
          </div>

          {/* Right Panel - Chat */}
          <div className="col-span-3 flex flex-col glass-strong rounded-xl overflow-hidden">
            <div className="p-4 border-b border-purple-500/30">
              <h3 className="font-bold text-purple-400 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Conversation
              </h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Start a conversation</p>
                  <p className="text-xs mt-1">Your input will be stored geometrically</p>
                </div>
              )}

              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 text-sm ${
                      msg.role === 'user'
                        ? 'bg-purple-600/50 text-white'
                        : 'bg-gray-800/50 border border-purple-500/30'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    {msg.metrics && (
                      <div className="mt-2 pt-2 border-t border-white/10 text-xs text-gray-400">
                        Coherence: {(msg.metrics.coherence * 100).toFixed(1)}%
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-800/50 border border-purple-500/30 rounded-lg p-3">
                    <Activity className="w-5 h-5 animate-spin text-purple-400" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-purple-500/30">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isProcessing && handleSend()}
                  placeholder="Type your message..."
                  className="flex-1 bg-black/30 border border-purple-500/30 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500"
                  disabled={isProcessing}
                />
                <button
                  onClick={handleSend}
                  disabled={isProcessing || !input.trim()}
                  className="btn-primary px-4"
                >
                  <Zap className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  color,
  target,
  subtitle
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
  target?: number;
  subtitle?: string;
}) {
  const colorClasses = {
    pink: 'from-pink-900/50 to-pink-700/30 border-pink-500 text-pink-400',
    purple: 'from-purple-900/50 to-purple-700/30 border-purple-500 text-purple-400',
    green: 'from-green-900/50 to-green-700/30 border-green-500 text-green-400',
    red: 'from-red-900/50 to-red-700/30 border-red-500 text-red-400'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} border-2 rounded-lg p-3`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-gray-300">{label}</span>
      </div>
      <div className="text-2xl font-bold">{(value * 100).toFixed(1)}%</div>
      {target && (
        <div className="text-xs mt-1 opacity-70">Target: {(target * 100).toFixed(0)}%+</div>
      )}
      {subtitle && <div className="text-xs mt-1 opacity-70">{subtitle}</div>}
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-400">{label}</span>
      <span className="text-purple-300 font-mono">{value}</span>
    </div>
  );
}

export default App;
