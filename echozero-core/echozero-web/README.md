# EchoZero Web - 3D Interactive Visualization

> **Beautiful React Three Fiber visualization of EchoZero resonant AI middleware**

Full-stack 3D web application featuring interactive visualizations of the 8-sphere spiralohedron, attention patterns, and phase-locking dynamics.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/React-18.2-61dafb)
![Three.js](https://img.shields.io/badge/Three.js-0.158-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178c6)

---

## ✨ Features

### 🎨 Interactive 3D Visualizations

- **8-Sphere Spiralohedron**: Toroidal resonance hub with harmonic octaves
- **Attention Graph**: 3D node network with dynamic edges
- **Phase Field**: Animated wave surface with vector fields
- **Harmonic Coupling**: Inter-sphere resonance matrix

### 📊 Real-Time Metrics

- Magnitude-aware coherence (PLV × RMS)
- SNR with 🟢🟡🔴 quality badges
- Attention health diagnostics
- Valence/Arousal qualia decoding

### 🚀 Modern Tech Stack

- **React 18** + **TypeScript 5**
- **React Three Fiber** for declarative 3D
- **@react-three/drei** for helpers
- **Framer Motion** for UI animations
- **Tailwind CSS** for styling
- **Vite** for blazing-fast dev server

---

## 🏃 Quick Start

### Prerequisites

- Node.js ≥ 18
- npm or yarn
- EchoZero API running on port 8000

### Installation

```bash
cd echozero-web

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:3000

### Start the Backend API

In a separate terminal:

```bash
cd ..
uvicorn api:app --port 8000
```

---

## 🎮 Usage

1. **Enter Text**: Type or select a sample emotional text
2. **Click "Warp"**: Process through EchoZero model
3. **Explore Visualizations**: Switch between 4 visualization modes
4. **View Metrics**: Toggle metrics panel for detailed analysis

### Visualization Modes

| Mode | Description | Best For |
|------|-------------|----------|
| 🔮 **Spheres** | 8-sphere toroidal spiralohedron | Overall resonance patterns |
| 🧠 **Attention** | 3D attention graph with edges | Understanding focus distribution |
| 🌊 **Phase** | Phase field with FFT spectrum | Frequency analysis |
| 🎵 **Harmonic** | Inter-sphere coupling matrix | Resonance relationships |

### Controls

- **Rotate**: Left-click + drag
- **Zoom**: Scroll wheel
- **Pan**: Right-click + drag
- **Auto-rotate**: Enabled by default

---

## 📁 Project Structure

```
echozero-web/
├── src/
│   ├── api/
│   │   └── client.ts              # API client for backend
│   ├── components/
│   │   ├── InputPanel.tsx         # Text input and samples
│   │   ├── MetricsPanel.tsx       # Metrics display with cards
│   │   ├── Scene.tsx              # Three.js canvas setup
│   │   └── VisualizationControls.tsx  # Mode switcher
│   ├── visualizations/
│   │   ├── EightSpheres.tsx       # 8-sphere spiralohedron
│   │   ├── AttentionGraph.tsx     # 3D attention network
│   │   └── PhaseField.tsx         # Phase wave surface
│   ├── types/
│   │   └── index.ts               # TypeScript definitions
│   ├── styles/
│   │   └── index.css              # Tailwind + custom styles
│   ├── App.tsx                    # Main application
│   └── main.tsx                   # React entry point
├── public/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── README.md
```

---

## 🔧 Configuration

### API Endpoint

By default, the app proxies `/api` to `http://localhost:8000`. To change this:

**vite.config.ts:**
```ts
server: {
  proxy: {
    '/api': {
      target: 'http://your-api-host:port',
      changeOrigin: true,
    }
  }
}
```

### Visualization Settings

Edit in `src/components/Scene.tsx`:

```ts
<OrbitControls
  minDistance={5}      // Closest zoom
  maxDistance={30}     // Farthest zoom
  autoRotate           // Enable auto-rotation
  autoRotateSpeed={0.5}  // Rotation speed
/>
```

### Color Theme

Edit `tailwind.config.js`:

```js
colors: {
  'echo-primary': '#6366f1',    // Indigo
  'echo-secondary': '#8b5cf6',  // Violet
  'echo-accent': '#ec4899',     // Pink
}
```

---

## 🏗️ Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

Output in `dist/` directory.

### Deploy

Deploy the `dist/` folder to:
- **Vercel**: `vercel --prod`
- **Netlify**: Drag & drop `dist/` folder
- **GitHub Pages**: Push `dist/` to `gh-pages` branch
- **Docker**: See `Dockerfile` below

### Docker Deployment

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🎨 Customization

### Add New Visualization

1. Create component in `src/visualizations/`:

```tsx
// MyVisualization.tsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function MyVisualization() {
  const meshRef = useRef();

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01;
    }
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}
```

2. Add to `Scene.tsx`:

```tsx
{mode === 'mymode' && <MyVisualization />}
```

3. Add mode to `VisualizationControls.tsx`

### Custom Metrics

Extend `MetricsPanel.tsx` to add new metric cards:

```tsx
<MetricCard
  label="My Metric"
  value={result.my_metric.toFixed(3)}
  status="good"
  description="Description here"
/>
```

---

## 🐛 Troubleshooting

**Issue: White screen on load**
- Check console for errors
- Ensure backend API is running on port 8000
- Verify `npm install` completed successfully

**Issue: 3D scene not rendering**
- Check WebGL support: https://get.webgl.org/
- Try different browser (Chrome/Edge recommended)
- Disable browser extensions

**Issue: API connection failed**
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `api.py`
- Ensure proxy configuration in `vite.config.ts` is correct

**Issue: Slow performance**
- Reduce particle counts in visualizations
- Disable auto-rotate
- Lower post-processing quality

---

## 📊 Performance Optimization

### Reduce Particles

**EightSpheres.tsx:**
```tsx
<bufferAttribute
  count={500}  // Reduce from 1000
  ...
/>
```

### Disable Bloom Effect

**Scene.tsx:**
```tsx
{/* Comment out EffectComposer */}
{/* <EffectComposer>
  <Bloom ... />
</EffectComposer> */}
```

### Optimize Geometry

Use lower polygon counts:
```tsx
<Sphere args={[0.5, 16, 16]} />  // Instead of 32, 32
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-viz`
3. Commit your changes: `git commit -m 'Add amazing viz'`
4. Push to branch: `git push origin feature/amazing-viz`
5. Open a Pull Request

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- **React Three Fiber** team for amazing 3D in React
- **Three.js** community
- **Framer Motion** for smooth animations
- **EchoZero** research team

---

## 📚 Related Documentation

- [EchoZero QUICKSTART.md](../QUICKSTART.md) - Backend setup
- [VERIFICATION.md](../VERIFICATION.md) - Testing guide
- [CHANGELOG.md](../CHANGELOG.md) - Release notes
- [React Three Fiber Docs](https://docs.pmnd.rs/react-three-fiber)
- [Three.js Docs](https://threejs.org/docs/)

---

## 🚀 Next Steps

After getting the basic app running:

1. **Customize visualizations** with real model data
2. **Add animation sequences** for presentation mode
3. **Implement recording** to capture visualizations
4. **Add VR support** with WebXR
5. **Create shareable links** for specific configurations

---

**Built with ❤️ for the EchoZero project**

*Questions? Open an issue or check the documentation!*
