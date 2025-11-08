"""
EchoZero: Resonant AI via Torsion-Warped Lattices

A PyTorch-based modular stack for geometric deep learning.
"""

__version__ = '0.1.0'
__author__ = 'Resonant Inventor'

from . import ingestion
from . import warp
from . import decode
from .echo_net import EchoZeroNet, create_echozero_model

__all__ = ['ingestion', 'warp', 'decode', 'EchoZeroNet', 'create_echozero_model']
