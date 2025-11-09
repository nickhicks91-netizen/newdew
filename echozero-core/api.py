"""
EchoZero Enhanced FastAPI Server

Production-grade REST API with magnitude-aware coherence metrics,
null-test baseline, and attention health diagnostics.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    GET  /health - Health check + model status
    POST /warp   - Full inference with magnitude-aware metrics
    GET  /baseline - Get architectural baseline from null-test
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditional imports
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - running in demo mode")

try:
    from src.echo_net import EchoZeroNetWithEchoCore, create_echozero_model_with_echo_core
    from src.metrics import null_test_coherence, compute_all_metrics
    ECHOZERO_AVAILABLE = True
except ImportError:
    ECHOZERO_AVAILABLE = False
    logger.warning("EchoZero modules not available")


# FastAPI app
app = FastAPI(
    title="EchoZero Warp API",
    description="Resonant AI with Magnitude-Aware Coherence Metrics",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class WarpRequest(BaseModel):
    """Request model for /warp endpoint"""
    prompt: str
    mode: str = 'text'  # 'text' or 'eeg'


class WarpResponse(BaseModel):
    """Response model with full metrics"""
    # Qualia
    valence: float
    arousal: float

    # Magnitude-aware coherence metrics
    effective_coherence: float
    snr_coherence: float  # dB
    plv: float            # Phase-locking value
    rms_magnitude: float  # RMS of locked band

    # Classification
    classification: int   # Predicted class
    confidence: float     # Max logit probability

    # Attention health
    avg_attention_entropy: float  # Lower = sharper focus
    avg_max_mean_ratio: float     # 2-5 = healthy, >10 = collapse

    # Optional debug info
    k_idx: Optional[float] = None  # Spectral bin used by ECC


# Global state
_model: Optional[Any] = None
_config: Optional[Dict] = None
_baseline_coherence: float = 0.26  # Default baseline


def load_model_and_baseline(config_path: str = "config/config.yaml") -> None:
    """Load model and compute null-test baseline at startup"""
    global _model, _config, _baseline_coherence

    if not ECHOZERO_AVAILABLE or not TORCH_AVAILABLE:
        logger.warning("Running in demo mode - model not loaded")
        return

    try:
        # Load config
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config not found: {config_path}, using defaults")
            _config = {}
        else:
            with open(config_path, 'r') as f:
                _config = yaml.safe_load(f)

        # Create model
        _model = create_echozero_model_with_echo_core(_config)
        _model.eval()

        logger.info(
            f"Model loaded: {_model.num_layers} layers, "
            f"{_model.num_spheres} spheres, dim={_model.dim}"
        )

        # Compute null-test baseline
        logger.info("Computing architectural baseline (null-test)...")
        null_results = null_test_coherence(_model, num_samples=10, device='cpu')
        _baseline_coherence = null_results.get('baseline_avg', 0.26)

        logger.info(f"Baseline coherence: {_baseline_coherence:.4f}")

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model = None


# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model and baseline on startup"""
    load_model_and_baseline()


# Endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        {
            "status": "healthy",
            "model_loaded": bool,
            "torch_available": bool,
            "echozero_available": bool,
            "baseline_coherence": float
        }
    """
    return {
        "status": "healthy",
        "model_loaded": _model is not None,
        "torch_available": TORCH_AVAILABLE,
        "echozero_available": ECHOZERO_AVAILABLE,
        "baseline_coherence": _baseline_coherence
    }


@app.post("/warp", response_model=WarpResponse)
async def warp_endpoint(request: WarpRequest) -> WarpResponse:
    """
    Full EchoZero inference with magnitude-aware metrics.

    Args:
        request: WarpRequest with prompt and mode

    Returns:
        WarpResponse with qualia, coherence metrics, classification,
        and attention health diagnostics
    """
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded - check /health endpoint"
        )

    if not TORCH_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PyTorch not available"
        )

    try:
        # Prepare input based on mode
        if request.mode == 'text':
            raw_input = request.prompt
        elif request.mode == 'eeg':
            # Parse EEG data from prompt (assume comma-separated floats)
            try:
                raw_input = torch.tensor([float(x) for x in request.prompt.split(',')])
            except:
                raise HTTPException(
                    status_code=400,
                    detail="EEG mode requires comma-separated float values"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {request.mode}. Use 'text' or 'eeg'"
            )

        # Forward pass with full diagnostics
        with torch.inference_mode():
            result = _model(
                raw_input,
                return_qualia=True,
                return_harmonics=True,
                return_attention=True,
                return_metrics=True
            )

        # Extract results
        logits = result['logits'][0]  # [num_classes]
        qualia = result['qualia']
        metrics_dict = result.get('metrics', {})

        # Classification
        predicted_class = int(logits.argmax())
        confidence = float(torch.softmax(logits, dim=0).max())

        # Build response
        response = WarpResponse(
            # Qualia
            valence=float(qualia.get('valence', [0.0])[0]),
            arousal=float(qualia.get('arousal', [0.0])[0]),

            # Coherence metrics
            effective_coherence=float(metrics_dict.get('eff_coh', 0.0)),
            snr_coherence=compute_snr_db(
                float(metrics_dict.get('eff_coh', 0.0)),
                _baseline_coherence
            ),
            plv=float(metrics_dict.get('plv', 0.0)),
            rms_magnitude=float(metrics_dict.get('rms_mag', 0.0)),

            # Classification
            classification=predicted_class,
            confidence=confidence,

            # Attention health
            avg_attention_entropy=float(metrics_dict.get('attn_entropy', 0.0)),
            avg_max_mean_ratio=float(metrics_dict.get('attn_max_mean', 0.0)),

            # Debug
            k_idx=float(metrics_dict.get('k_idx', 0.0))
        )

        return response

    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/baseline")
async def get_baseline() -> Dict[str, float]:
    """
    Get the architectural baseline coherence from null-test.

    Returns:
        {"baseline_coherence": float, "note": str}
    """
    return {
        "baseline_coherence": _baseline_coherence,
        "note": "Geometry-only coherence from random noise (10 samples)"
    }


# Helper functions
def compute_snr_db(coherence: float, baseline: float, eps: float = 1e-8) -> float:
    """Compute SNR in dB"""
    import math
    snr_linear = coherence / (baseline + eps)
    snr_db = 10 * math.log10(snr_linear + eps)
    return snr_db


# Demo mode responses (when model not loaded)
@app.post("/warp/demo", response_model=WarpResponse)
async def warp_demo() -> WarpResponse:
    """
    Demo endpoint that returns mock data (for testing without model).
    """
    return WarpResponse(
        valence=0.42,
        arousal=0.67,
        effective_coherence=0.58,
        snr_coherence=3.2,
        plv=0.72,
        rms_magnitude=1.15,
        classification=1,
        confidence=0.83,
        avg_attention_entropy=0.45,
        avg_max_mean_ratio=3.2,
        k_idx=2.0
    )


if __name__ == "__main__":
    import uvicorn

    # Load model
    load_model_and_baseline()

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
