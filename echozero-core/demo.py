#!/usr/bin/env python3
"""
Quick demo of EchoZero production metrics system.
Run with: python demo.py
"""

import sys
from pathlib import Path

# Check dependencies first
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not installed. Install with: pip install torch>=2.1.0")
    sys.exit(1)

try:
    from src.echo_net import create_echozero_model_with_echo_core
    from src.metrics import compute_all_metrics, null_test_coherence
    import yaml
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall all dependencies with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

def main():
    print("=" * 70)
    print("🌀 EchoZero Production Metrics Demo")
    print("=" * 70)

    # Load model
    print("\n[1/4] Loading EchoZero model...")
    config_path = "config/config.yaml"

    try:
        model = create_echozero_model_with_echo_core(config_path)
        model.eval()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)

    # Compute baseline
    print("\n[2/4] Computing architectural baseline (10 samples)...")
    print("      This takes ~10-20 seconds on first run...")

    try:
        baseline_results = null_test_coherence(
            model,
            num_samples=10,
            signal_dim=1024,
            device='cpu'
        )
        baseline = baseline_results['baseline_avg']
        baseline_std = baseline_results['baseline_std']
        print(f"✓ Baseline coherence: {baseline:.4f} ± {baseline_std:.4f}")
        print(f"  (Typical range: 0.24-0.28 for random noise)")
    except Exception as e:
        print(f"❌ Error computing baseline: {e}")
        baseline = 0.26  # Fallback to typical value
        print(f"⚠️  Using fallback baseline: {baseline:.4f}")

    # Test inputs
    test_texts = [
        "I feel energized and focused today",
        "I'm anxious about the presentation tomorrow",
        "Everything feels neutral and calm",
        "I'm excited about the new opportunity"
    ]

    print("\n[3/4] Processing test inputs...")
    print("-" * 70)

    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Input {i}: \"{text}\"")

        try:
            # Run inference
            with torch.inference_mode():
                outputs = model(text)

            # Compute all metrics
            metrics = compute_all_metrics(
                model=model,
                phase_locked=outputs['phase_locked'],
                amp_locked=outputs['amp_locked'],
                attention=outputs['attention'],
                k_idx=outputs['k_idx'],
                baseline_coherence=baseline
            )

            # Display results
            print(f"   Valence: {outputs['valence']:.3f}  |  Arousal: {outputs['arousal']:.3f}")
            print(f"   Effective Coherence: {metrics['effective_coherence']:.4f}")
            print(f"   PLV: {metrics['plv']:.4f}  |  RMS: {metrics['rms_magnitude']:.4f}")

            # SNR with emoji
            snr = metrics['snr_coherence']
            if snr > 3.0:
                badge = "🟢"
                quality = "Good"
            elif snr > 0:
                badge = "🟡"
                quality = "Marginal"
            else:
                badge = "🔴"
                quality = "Poor"

            print(f"   SNR: {snr:.2f} dB {badge} ({quality})")

            # Attention health
            entropy = metrics['avg_attention_entropy']
            max_mean = metrics['avg_max_mean_ratio']

            health_status = "✓" if (entropy < 1.0 and 2 <= max_mean <= 5) else "⚠"
            print(f"   Attention Health {health_status}:")
            print(f"     - Entropy: {entropy:.3f} (lower = sharper, healthy < 1.0)")
            print(f"     - Max/Mean: {max_mean:.2f} (healthy: 2-5, collapse: >10)")

        except Exception as e:
            print(f"   ❌ Error processing: {e}")
            continue

    # Summary
    print("\n" + "=" * 70)
    print("[4/4] Demo Complete!")
    print("=" * 70)
    print("\n📊 Metric Interpretation:")
    print("   • Effective Coherence: PLV × RMS (prevents low-amplitude noise)")
    print("   • SNR: 🟢 >3dB = good | 🟡 0-3dB = marginal | 🔴 <0dB = poor")
    print("   • Attention Entropy: Lower = sharper focus")
    print("   • Max/Mean Ratio: 2-5 = healthy | >10 = collapse")

    print("\n🚀 Next Steps:")
    print("   1. Interactive UI:  streamlit run streamlit_app_enhanced.py")
    print("   2. REST API:        uvicorn api:app --port 8000")
    print("   3. Documentation:   cat QUICKSTART.md")
    print("   4. Verification:    cat VERIFICATION.md")
    print()

if __name__ == "__main__":
    main()
