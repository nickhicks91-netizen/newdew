import { useState } from 'react';
import { motion } from 'framer-motion';

export interface InputPanelProps {
  onSubmit: (text: string) => void;
  loading: boolean;
}

const sampleTexts = [
  "I feel energized and focused today",
  "I'm anxious about the presentation tomorrow",
  "Everything feels neutral and calm",
  "I'm excited about the new opportunity",
  "This situation makes me feel overwhelmed and stressed",
];

export default function InputPanel({ onSubmit, loading }: InputPanelProps) {
  const [text, setText] = useState(sampleTexts[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onSubmit(text);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6 space-y-4"
    >
      <h2 className="text-2xl font-bold gradient-text mb-4">🌀 EchoZero Warp</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="input-text" className="block text-sm font-medium text-gray-300 mb-2">
            Input Text
          </label>
          <textarea
            id="input-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="input w-full min-h-[120px] resize-none"
            placeholder="Enter text to analyze..."
            disabled={loading}
          />
        </div>

        <div className="flex gap-2 flex-wrap">
          {sampleTexts.map((sample, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setText(sample)}
              className="btn-secondary text-xs"
              disabled={loading}
            >
              Sample {i + 1}
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="btn-primary w-full relative overflow-hidden"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Processing...
            </span>
          ) : (
            '🚀 Warp Through EchoZero'
          )}
        </button>
      </form>

      <div className="text-xs text-gray-400 space-y-1">
        <p>💡 <strong>Tip:</strong> Try emotional, complex, or abstract text for best results</p>
        <p>⚡ Processing uses magnitude-aware coherence metrics</p>
      </div>
    </motion.div>
  );
}
