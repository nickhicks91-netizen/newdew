"""
Warp Core - TEAPenroseLayer

Geometric attention with Ricci-torsion on Penrose tilings.
Implements coherence funneling through warped lattice structures.
"""

from .penrose_gen import generate_penrose, visualize_penrose
from .ricci_affinity import ricci_affinity, ricci_warp, compute_ricci_flow
from .torsion_router import (
    torsion_loss,
    trefoil_phase,
    coherence_score,
    phase_synchronization
)
from .tea_penrose import TEAPenroseLayer

__all__ = [
    # Penrose generation
    'generate_penrose',
    'visualize_penrose',
    # Ricci affinity
    'ricci_affinity',
    'ricci_warp',
    'compute_ricci_flow',
    # Torsion routing
    'torsion_loss',
    'trefoil_phase',
    'coherence_score',
    'phase_synchronization',
    # Main layer
    'TEAPenroseLayer',
]
