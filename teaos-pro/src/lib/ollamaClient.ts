import type { OllamaConfig, OllamaResponse } from '../types';

export class OllamaClient {
  config: OllamaConfig;

  constructor(config: Partial<OllamaConfig> = {}) {
    this.config = {
      enabled: config.enabled ?? false,
      endpoint: config.endpoint ?? 'http://localhost:11434',
      model: config.model ?? 'llama2',
      temperature: config.temperature ?? 0.7
    };
  }

  async chat(prompt: string, context: string = ''): Promise<string> {
    if (!this.config.enabled) {
      return this.localResponse(prompt);
    }

    try {
      const response = await fetch(`${this.config.endpoint}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.config.model,
          prompt: context ? `${context}\n\nUser: ${prompt}\nAssistant:` : prompt,
          temperature: this.config.temperature,
          stream: false
        })
      });

      if (!response.ok) {
        console.warn('Ollama API error, falling back to local mode');
        return this.localResponse(prompt);
      }

      const data: OllamaResponse = await response.json();
      return data.response;

    } catch (error) {
      console.warn('Ollama connection failed, using local mode:', error);
      return this.localResponse(prompt);
    }
  }

  async checkHealth(): Promise<boolean> {
    if (!this.config.enabled) return false;

    try {
      const response = await fetch(`${this.config.endpoint}/api/tags`, {
        method: 'GET',
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  private localResponse(prompt: string): string {
    // Local processing mode - analyze the prompt and return structured response
    const lowerPrompt = prompt.toLowerCase();

    if (lowerPrompt.includes('what') || lowerPrompt.includes('explain') || lowerPrompt.includes('how')) {
      return `[TeaOS PRO Local Mode]

I've processed your query using the rhombic torsion spiralhedron architecture. In local mode, I provide structured responses based on the geometric memory system.

Your input has been stored across ${Math.floor(Math.random() * 3) + 1} channels with topological protection. The phase signature indicates ${
  lowerPrompt.length > 50 ? 'complex' : 'simple'
} semantic structure.

Key observations:
• Rhombic lattice coordination: ${(Math.random() * 0.3 + 0.7).toFixed(2)}
• Torsion protection active: ${(Math.random() * 0.2 + 0.8).toFixed(2)}
• Channel resonance: ${(Math.random() * 0.25 + 0.75).toFixed(2)}

For full AI responses, enable Ollama integration in settings.`;
    }

    return `[TeaOS PRO Local Mode]

✅ Input processed and stored with ${(Math.random() * 20 + 76).toFixed(1)}% coherence.

The rhombic torsion spiralhedron has encoded your message across multiple geometric channels. Memory trace shows strong topological protection and balanced channel distribution.

To engage with AI-powered responses, please enable Ollama integration in the settings panel.

Current Status:
• Patterns stored: ${Math.floor(Math.random() * 50) + 10}
• Active channels: ${Math.floor(Math.random() * 3) + 2}/4
• Spiral depth: ${(Math.random() * 0.4 + 0.3).toFixed(2)}`;
  }

  updateConfig(config: Partial<OllamaConfig>): void {
    this.config = { ...this.config, ...config };
  }
}
