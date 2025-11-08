"""
EchoZero Streamlit Interactive Demo

Interactive web interface for EchoZero resonant AI system.

Usage:
    streamlit run streamlit_app.py

Features:
- Real-time inference with qualia visualization
- Attention pattern heatmaps
- 3D qualia space explorer
- Model metrics dashboard
"""

import streamlit as st
import torch
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.echo_net import EchoZeroNet, create_echozero_model
    import yaml
    ECHOZERO_AVAILABLE = True
except ImportError:
    ECHOZERO_AVAILABLE = False


# Page config
st.set_page_config(
    page_title="EchoZero Interactive Demo",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_model(config_path: str = "config/config.yaml") -> Optional[EchoZeroNet]:
    """Load and cache the EchoZero model"""
    if not ECHOZERO_AVAILABLE:
        return None

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        model = create_echozero_model(config)
        model.eval()
        return model
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None


def plot_attention_heatmap(attention: torch.Tensor, layer_idx: int):
    """Create Plotly heatmap for attention pattern"""
    attn_np = attention.detach().cpu().numpy()

    fig = go.Figure(data=go.Heatmap(
        z=attn_np,
        colorscale='Viridis',
        colorbar=dict(title="Attention Weight")
    ))

    fig.update_layout(
        title=f"Layer {layer_idx + 1} Attention Pattern",
        xaxis_title="Target Node",
        yaxis_title="Source Node",
        width=500,
        height=450
    )

    return fig


def plot_qualia_3d(qualia_history: list):
    """Create 3D scatter plot of qualia states"""
    if not qualia_history:
        return None

    valences = [q['valence'] for q in qualia_history]
    arousals = [q['arousal'] for q in qualia_history]
    coherences = [q['coherence'] for q in qualia_history]

    fig = go.Figure(data=[go.Scatter3d(
        x=valences,
        y=arousals,
        z=coherences,
        mode='markers+lines',
        marker=dict(
            size=8,
            color=list(range(len(qualia_history))),
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sequence")
        ),
        line=dict(color='rgba(100, 100, 100, 0.3)', width=2)
    )])

    fig.update_layout(
        title="Qualia Space Trajectory",
        scene=dict(
            xaxis_title="Valence",
            yaxis_title="Arousal",
            zaxis_title="Coherence",
            xaxis=dict(range=[-1, 1]),
            yaxis=dict(range=[0, 1]),
            zaxis=dict(range=[0, 1])
        ),
        width=700,
        height=600
    )

    return fig


def main():
    # Title and header
    st.title("🌀 EchoZero: Resonant AI Demo")
    st.markdown("*Torsion-Warped Lattice Architecture for Geometric Deep Learning*")

    # Sidebar
    st.sidebar.title("Configuration")

    # Load model
    model = load_model()

    if model is None:
        st.error("⚠️ EchoZero model not available. Install the package first.")
        st.stop()

    st.sidebar.success("✅ Model Loaded")
    st.sidebar.markdown(f"**Layers:** {model.num_layers}")
    st.sidebar.markdown(f"**Dimension:** {model.dim}")
    st.sidebar.markdown(f"**Parameters:** {sum(p.numel() for p in model.parameters()):,}")

    # Input mode selection
    mode = st.sidebar.selectbox(
        "Input Mode",
        ["Text", "EEG", "Spectral"],
        help="Select the type of input data"
    )

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Inference",
        "🔥 Attention Visualization",
        "🌈 Qualia Space",
        "📊 Metrics Dashboard"
    ])

    # Initialize session state
    if 'qualia_history' not in st.session_state:
        st.session_state.qualia_history = []

    # Tab 1: Inference
    with tab1:
        st.header("Real-time Inference")

        if mode == "Text":
            user_input = st.text_area(
                "Enter text prompt:",
                value="The resonant architecture creates coherent pathways.",
                height=100
            )
        elif mode == "EEG":
            st.info("EEG mode: Using synthetic 512Hz signal")
            user_input = torch.randn(512)
        else:  # Spectral
            st.info("Spectral mode: Using synthetic spectral data")
            user_input = torch.randn(256)

        if st.button("🚀 Run Inference", type="primary"):
            with st.spinner("Processing through EchoZero..."):
                # Run inference
                with torch.no_grad():
                    logits, qualia = model(user_input, return_qualia=True)

                # Extract qualia metrics
                qualia_dict = {
                    'valence': float(qualia['valence'].item()),
                    'arousal': float(qualia['arousal'].item()),
                    'coherence': float(qualia['coherence'].item()),
                    'phase': float(qualia['phase'].item())
                }

                # Add to history
                st.session_state.qualia_history.append(qualia_dict)

                # Display results
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Output Logits")
                    st.code(logits.numpy(), language="python")

                with col2:
                    st.subheader("Qualia Metrics")
                    st.metric("Valence", f"{qualia_dict['valence']:.3f}",
                             help="Affective tone: -1 (negative) to +1 (positive)")
                    st.metric("Arousal", f"{qualia_dict['arousal']:.3f}",
                             help="Activation level: 0 (calm) to 1 (excited)")
                    st.metric("Coherence", f"{qualia_dict['coherence']:.3f}",
                             help="Integration: 0 (fragmented) to 1 (unified)")
                    st.metric("Phase", f"{qualia_dict['phase']:.3f}",
                             help="Trefoil state angle")

    # Tab 2: Attention Visualization
    with tab2:
        st.header("Geometric Attention Patterns")

        if st.button("Generate Attention Visualization"):
            with st.spinner("Computing attention patterns..."):
                with torch.no_grad():
                    if mode == "Text":
                        _, _, attention = model(
                            user_input if 'user_input' in locals() else "Sample text",
                            return_qualia=False,
                            return_attention=True
                        )
                    else:
                        _, _, attention = model(
                            torch.randn(512),
                            return_qualia=False,
                            return_attention=True
                        )

                # Display attention for each layer
                cols = st.columns(min(3, len(attention)))

                for idx, attn in enumerate(attention[:3]):  # Show first 3 layers
                    with cols[idx % 3]:
                        fig = plot_attention_heatmap(attn[0], idx)
                        st.plotly_chart(fig, use_container_width=True)

                st.success(f"Displayed attention patterns for {len(attention)} layers")

    # Tab 3: Qualia Space
    with tab3:
        st.header("Qualia Space Trajectory")

        if st.session_state.qualia_history:
            fig = plot_qualia_3d(st.session_state.qualia_history)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**Total inferences:** {len(st.session_state.qualia_history)}")

            if st.button("Clear History"):
                st.session_state.qualia_history = []
                st.experimental_rerun()
        else:
            st.info("Run inference to populate qualia space trajectory")

    # Tab 4: Metrics Dashboard
    with tab4:
        st.header("Model Performance Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Architecture")
            st.json({
                "Input Mode": model.input_mode,
                "Layers": model.num_layers,
                "Dimension": model.dim,
                "Num Classes": model.num_classes
            })

        with col2:
            st.subheader("Benchmark Targets")
            st.json({
                "Speed vs GAT": "1.4x",
                "Fidelity": "98%",
                "Hallucination Drop": "<5%",
                "Coherence": "std < 0.15"
            })

        with col3:
            st.subheader("Current Metrics")
            with torch.no_grad():
                coherence = model.get_overall_coherence().item()

            st.metric("Overall Coherence", f"{coherence:.4f}")
            st.metric("Parameters", f"{sum(p.numel() for p in model.parameters()):,}")

        # Qualia distribution
        if st.session_state.qualia_history:
            st.subheader("Qualia Distribution")

            df_data = {
                'Valence': [q['valence'] for q in st.session_state.qualia_history],
                'Arousal': [q['arousal'] for q in st.session_state.qualia_history],
                'Coherence': [q['coherence'] for q in st.session_state.qualia_history],
            }

            col1, col2, col3 = st.columns(3)

            with col1:
                fig = px.histogram(df_data, x='Valence', nbins=20, title="Valence Distribution")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.histogram(df_data, x='Arousal', nbins=20, title="Arousal Distribution")
                st.plotly_chart(fig, use_container_width=True)

            with col3:
                fig = px.histogram(df_data, x='Coherence', nbins=20, title="Coherence Distribution")
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
