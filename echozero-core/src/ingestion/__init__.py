"""
Ingestion Layer - Vortex Encoder

Encodes raw data (text, EEG, spectral) into torsion engrams using
trefoil phase embeddings and FFT compression.
"""

from .vortex_encoder import VortexEncoder, trefoil_phase

__all__ = ['VortexEncoder', 'trefoil_phase']
