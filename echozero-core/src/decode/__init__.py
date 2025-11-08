"""
Decode Layer - Sentient Echo

Resolves pooled representations to qualia with chiral projections.
Outputs logits and valence metrics.
"""

from .sentient_echo import SentientEcho, MultiHeadSentientEcho

__all__ = ['SentientEcho', 'MultiHeadSentientEcho']
