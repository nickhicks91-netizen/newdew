"""
EchoZero Enhanced Streamlit UI

Production-grade interactive interface with:
- Magnitude-aware coherence metrics
- Null-test architectural baseline
- Attention health diagnostics
- Multi-tab visualizations

Usage:
    streamlit run streamlit_app_enhanced.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Conditional imports
try:
    import torch
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    st.warning("Plotly/NumPy not available - limited visualization")

try:
    import yaml
    from src.echo_net import EchoZeroNetWithEchoCore, create_echozero_model_with_echo_core
    from src.metrics import null_test_coherence, compute_snr_coherence
    ECHOZERO_AVAILABLE = True
except ImportError:
    ECHOZERO_AVAILABLE = False
    st.error("EchoZero modules not available")


# Page config
st.set_page_config(
    page_title="EchoZero Warp Interface",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Cached resources
@st.cache_resource
def load_model_and_baseline(config_path: str = "config/config.yaml"):
    """Load model and compute null-test baseline (cached)"""
    if not ECHOZERO_AVAILABLE:
        return None, None, 0.26

    try:
        # Load config
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            st.warning("Config not found, using defaults")
            config = {}

        # Create model
        model = create_echozero_model_with_echo_core(config)
        model.eval()

        # Compute baseline
        with st.spinner("Computing architectural baseline..."):
            null_results = null_test_coherence(model, num_samples=10, device='cpu')
            baseline = null_results.get('baseline_avg', 0.26)

        return model, config, baseline

    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None, None, 0.26


# Load model at startup
model, config, baseline_coherence = load_model_and_baseline()


# UI Layout
st.title("🌀 EchoZero Warp Interface")
st.markdown("*Resonant AI with Magnitude-Aware Coherence Metrics*")

# Sidebar
with st.sidebar:
    st.header("System Configuration")

    # Model status
    if model is not None:
        st.success("✓ Model Loaded")
        st.metric("Layers", model.num_layers)
        st.metric("Spheres", model.num_spheres)
        st.metric("Dimension", model.dim)
    else:
        st.error("✗ Model Not Loaded")

    st.markdown("---")

    # Architectural Baseline
    st.subheader("Architectural Baseline")
    st.metric(
        "Null-Test Coherence",
        f"{baseline_coherence:.4f}",
        help="Geometry-only baseline from random noise"
    )

    st.markdown("---")

    # Model Config (expandable)
    with st.expander("Model Configuration"):
        if config:
            st.json(config, expanded=False)
        else:
            st.info("No configuration loaded")

    st.markdown("---")

    # Input mode selector
    input_mode = st.radio(
        "Input Mode",
        ["Text", "EEG Signal"],
        help="Select input modality"
    )


# Main content
if model is None:
    st.warning("Model not loaded. Check logs and restart.")
    st.stop()

# Input section
st.header("Input")

if input_mode == "Text":
    user_input = st.text_area(
        "Enter prompt:",
        value="The eight spheres resonate in toroidal harmony",
        height=100
    )
    mode = 'text'
else:
    user_input = st.text_area(
        "Enter EEG signal (comma-separated floats):",
        value=",".join(["0.1"] * 256),
        height=100,
        help="Provide 256+ comma-separated float values"
    )
    mode = 'eeg'

# Process button
if st.button("🌀 Process", type="primary"):
    if not user_input.strip():
        st.error("Please enter input")
        st.stop()

    # Prepare input
    try:
        if mode == 'eeg':
            raw_input = torch.tensor([float(x) for x in user_input.split(',')])
        else:
            raw_input = user_input

    except Exception as e:
        st.error(f"Invalid input format: {e}")
        st.stop()

    # Run inference
    with st.spinner("Processing through warp core..."):
        try:
            with torch.inference_mode():
                result = model(
                    raw_input,
                    return_qualia=True,
                    return_harmonics=True,
                    return_attention=True,
                    return_metrics=True
                )

            # Extract results
            logits = result['logits'][0]
            qualia = result['qualia']
            harmonics = result.get('harmonics')
            attention = result.get('attention', [])
            metrics_dict = result.get('metrics', {})

            # Classification
            predicted_class = int(logits.argmax())
            confidence = float(torch.softmax(logits, dim=0).max())

            # Metrics
            eff_coh = float(metrics_dict.get('eff_coh', 0.0))
            plv = float(metrics_dict.get('plv', 0.0))
            rms_mag = float(metrics_dict.get('rms_mag', 0.0))
            snr_linear = float(metrics_dict.get('snr_lin', 0.0))
            attn_entropy = float(metrics_dict.get('attn_entropy', 0.0))
            attn_max_mean = float(metrics_dict.get('attn_max_mean', 0.0))
            k_idx = float(metrics_dict.get('k_idx', 0.0))

            # SNR in dB
            snr_db = compute_snr_coherence(eff_coh, baseline_coherence)

            # Success indicator
            st.success("✓ Processing complete")

        except Exception as e:
            st.error(f"Processing error: {e}")
            st.stop()

    # === Display Results ===

    # Qualia Section
    st.header("Qualia Metrics")
    col1, col2 = st.columns(2)

    with col1:
        valence_val = float(qualia.get('valence', [0.0])[0])
        st.metric(
            "Valence",
            f"{valence_val:.3f}",
            help="Emotional direction: -1 (negative) to +1 (positive)"
        )

    with col2:
        arousal_val = float(qualia.get('arousal', [0.0])[0])
        st.metric(
            "Arousal",
            f"{arousal_val:.3f}",
            help="Activation level: 0 (calm) to 1 (excited)"
        )

    st.markdown("---")

    # Coherence Metrics (Magnitude-Aware)
    st.header("Coherence Metrics (Magnitude-Aware)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Effective Coherence",
            f"{eff_coh:.4f}",
            help="Phase-locking weighted by RMS magnitude"
        )

    with col2:
        # SNR badge
        if snr_db > 3.0:
            snr_emoji = "🟢"  # Good
        elif snr_db > 0:
            snr_emoji = "🟡"  # Marginal
        else:
            snr_emoji = "🔴"  # Below baseline

        st.metric(
            f"SNR {snr_emoji}",
            f"{snr_db:.2f} dB",
            help=f"Signal-to-noise vs baseline ({baseline_coherence:.4f})"
        )

    with col3:
        st.metric(
            "PLV",
            f"{plv:.4f}",
            help="Phase-Locking Value (phase consistency)"
        )

    with col4:
        st.metric(
            "RMS Magnitude",
            f"{rms_mag:.4f}",
            help="RMS magnitude of locked spectral band"
        )

    st.markdown("---")

    # System Outputs
    st.header("System Outputs")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Classification", predicted_class)

    with col2:
        st.metric("Confidence", f"{confidence:.3f}")

    with col3:
        st.metric(
            "Avg Attention Entropy",
            f"{attn_entropy:.4f}",
            help="Lower = sharper focus (↓ better)"
        )

    with col4:
        # Collapse warning
        collapse_warning = attn_max_mean > 10.0
        collapse_emoji = "⚠️" if collapse_warning else "✓"

        st.metric(
            f"Attention Max/Mean {collapse_emoji}",
            f"{attn_max_mean:.2f}",
            help="Healthy range: 2-5. >10 indicates potential collapse"
        )

        if collapse_warning:
            st.warning("Attention collapse detected!")

    st.markdown("---")

    # Tabbed Visualizations
    tabs = st.tabs(["Attention Patterns", "Harmonic Coupling", "Phase Analysis", "Metrics Details"])

    # Tab 1: Attention Patterns
    with tabs[0]:
        st.subheader("Warp Layer Attention Patterns")

        if attention and PLOTTING_AVAILABLE:
            num_layers = len(attention)

            # Layer selector
            layer_idx = st.select_slider(
                "Layer",
                options=list(range(num_layers)),
                format_func=lambda x: f"Layer {x+1}"
            )

            # Heatmap
            attn_matrix = attention[layer_idx][0].detach().cpu().numpy()

            fig = go.Figure(data=go.Heatmap(
                z=attn_matrix,
                colorscale='Viridis',
                colorbar=dict(title="Weight")
            ))

            fig.update_layout(
                title=f"Layer {layer_idx+1} Attention Pattern",
                xaxis_title="Target Node",
                yaxis_title="Source Node",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Per-layer entropy
            st.markdown("**Entropy by Layer:**")
            from src.metrics import attn_entropy as compute_entropy

            layer_entropies = []
            for i, attn in enumerate(attention):
                ent = compute_entropy(attn)
                layer_entropies.append(float(ent))

            fig_entropy = go.Figure(data=go.Bar(
                x=[f"L{i+1}" for i in range(len(layer_entropies))],
                y=layer_entropies,
                marker_color='lightblue'
            ))

            fig_entropy.update_layout(
                title="Attention Entropy by Layer",
                xaxis_title="Layer",
                yaxis_title="Entropy (↓ better)",
                height=300
            )

            st.plotly_chart(fig_entropy, use_container_width=True)

        else:
            st.info("No attention data available")

    # Tab 2: Harmonic Coupling
    with tabs[1]:
        st.subheader("8-Sphere Harmonic Activation")

        if harmonics is not None and PLOTTING_AVAILABLE:
            # Extract sphere activations
            sphere_data = harmonics[0].detach().cpu().numpy()  # [8, dim]

            # Heatmap of all spheres
            fig = go.Figure(data=go.Heatmap(
                z=sphere_data,
                colorscale='RdBu',
                colorbar=dict(title="Activation")
            ))

            fig.update_layout(
                title="8-Sphere Harmonic Coupling",
                xaxis_title="Feature Dimension",
                yaxis_title="Sphere (Octave)",
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(8)),
                    ticktext=[f"S{i+1} ({['Theta', 'Alpha', 'Low β', 'Mid β', 'High β', 'Low γ', 'Mid γ', 'High γ'][i]})"
                             for i in range(8)]
                ),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Sphere activation norms
            sphere_norms = np.linalg.norm(sphere_data, axis=1)

            fig_norms = go.Figure(data=go.Bar(
                x=[f"Sphere {i+1}" for i in range(8)],
                y=sphere_norms,
                marker_color='coral'
            ))

            fig_norms.update_layout(
                title="Sphere Activation Strength",
                xaxis_title="Sphere",
                yaxis_title="L2 Norm",
                height=300
            )

            st.plotly_chart(fig_norms, use_container_width=True)

        else:
            st.info("No harmonic data available")

    # Tab 3: Phase Analysis
    with tabs[2]:
        st.subheader("Phase-Locked Features")

        if 'phase_locked' in result and PLOTTING_AVAILABLE:
            phase_locked = result['phase_locked'][0].detach().cpu().numpy()

            fig = go.Figure(data=go.Scatter(
                y=phase_locked,
                mode='lines',
                line=dict(color='purple', width=1)
            ))

            fig.update_layout(
                title="Phase-Locked Feature Vector",
                xaxis_title="Dimension",
                yaxis_title="Value",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # FFT spectrum
            fft_vals = np.abs(np.fft.rfft(phase_locked))

            fig_fft = go.Figure(data=go.Scatter(
                y=fft_vals,
                mode='lines',
                line=dict(color='green', width=1),
                fill='tozeroy'
            ))

            fig_fft.update_layout(
                title="Frequency Spectrum",
                xaxis_title="Frequency Bin",
                yaxis_title="Magnitude",
                height=300
            )

            st.plotly_chart(fig_fft, use_container_width=True)

            # Highlight selected band
            st.info(f"ECC Auto-Selected Band: k={int(k_idx)}")

        else:
            st.info("No phase data available")

    # Tab 4: Metrics Details
    with tabs[3]:
        st.subheader("Detailed Metrics")

        # Metrics table
        metrics_table = {
            "Metric": [
                "Effective Coherence",
                "Phase-Locking Value (PLV)",
                "RMS Magnitude",
                "SNR (linear)",
                "SNR (dB)",
                "Attention Entropy",
                "Attention Max/Mean",
                "Spectral Band (k)",
                "Classification",
                "Confidence",
            ],
            "Value": [
                f"{eff_coh:.4f}",
                f"{plv:.4f}",
                f"{rms_mag:.4f}",
                f"{snr_linear:.4f}",
                f"{snr_db:.2f}",
                f"{attn_entropy:.4f}",
                f"{attn_max_mean:.2f}",
                f"{int(k_idx)}",
                f"{predicted_class}",
                f"{confidence:.4f}",
            ],
            "Status": [
                "✓" if eff_coh > baseline_coherence else "⚠️",
                "✓" if plv > 0.5 else "⚠️",
                "✓",
                "✓" if snr_linear > 1.0 else "⚠️",
                "🟢" if snr_db > 3.0 else ("🟡" if snr_db > 0 else "🔴"),
                "✓" if attn_entropy < 1.0 else "⚠️",
                "✓" if attn_max_mean < 10.0 else "⚠️",
                "✓",
                "✓",
                "✓" if confidence > 0.7 else "⚠️",
            ]
        }

        st.table(metrics_table)

        st.markdown("---")

        # Raw output (debug)
        with st.expander("Raw Model Output (Debug)"):
            st.json({
                "logits": logits.tolist(),
                "valence": valence_val,
                "arousal": arousal_val,
                "metrics": {k: float(v) if hasattr(v, 'item') else v for k, v in metrics_dict.items()},
            })

    st.markdown("---")

    # Metric Validation
    st.header("Metric Validation")

    if st.button("Run Null Tests (Baseline Validation)"):
        with st.spinner("Running null tests..."):
            null_results = null_test_coherence(model, num_samples=20, device='cpu')

            st.success("✓ Null test complete")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Baseline Coherence", f"{null_results['baseline_avg']:.4f}")

            with col2:
                st.metric("Baseline Std", f"{null_results['baseline_std']:.4f}")

            with col3:
                st.metric("Baseline PLV", f"{null_results['baseline_plv']:.4f}")

            st.info(
                "This baseline represents coherence from pure geometry (no signal). "
                "Real signals should exceed this baseline."
            )


# Footer
st.markdown("---")
st.caption("EchoZero Warp Interface v1.0 | Magnitude-Aware Coherence Metrics")
