"""
Vortex Encoder - Multi-modal Ingestion Layer

Encodes raw data (text, EEG, spectral) into torsion engrams using:
- FFT-based spectral decomposition
- Trefoil phase embedding (3-fold knot symmetry)
- Compression to latent dimension

Supports:
- Text: Via sentence-transformers
- EEG: Via MNE epochs or raw tensors
- Spectral: Direct tensor input
"""

import torch
import torch.nn as nn
import torch.fft as fft
import numpy as np
from typing import Union, Tuple, List, Optional

# Optional imports with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("Warning: sentence-transformers not installed. Text mode will be limited.")

try:
    import mne
    HAS_MNE = True
except ImportError:
    HAS_MNE = False
    print("Warning: MNE not installed. EEG mode will use tensor-only processing.")


def trefoil_phase(signal: torch.Tensor) -> torch.Tensor:
    """
    Embed signal as trefoil torsion phases.

    The trefoil knot has 3-fold rotational symmetry, creating
    a topologically robust phase embedding that preserves
    signal structure while enabling torsion routing.

    Args:
        signal: Input signal tensor [N] or [batch, N]

    Returns:
        Trefoil-embedded phases [N] or [batch, N]
    """
    # Compute FFT and extract phase
    f = fft.rfft(signal, dim=-1)
    phase = torch.angle(f)

    # Apply trefoil symmetry: sin(3θ) creates 3-fold structure
    # This maps phase space onto a trefoil knot topology
    trefoil_embedded = torch.sin(3 * phase)

    return trefoil_embedded


class VortexEncoder(nn.Module):
    """
    Vortex Recorder - Multi-modal data encoder

    Transforms raw inputs into compressed torsion engrams via:
    1. Modal pre-processing (text→embeddings, EEG→channels, spectral→raw)
    2. FFT spectral decomposition
    3. Trefoil phase embedding
    4. Linear projection to target dimension

    Args:
        dim: Target embedding dimension (default: 128)
        mode: Input modality - 'text', 'eeg', or 'spectral' (default: 'eeg')
        text_model: Sentence-transformer model name (default: 'all-MiniLM-L6-v2')
        normalize: Whether to L2-normalize output engrams (default: True)
    """

    def __init__(
        self,
        dim: int = 128,
        mode: str = 'eeg',
        text_model: str = 'all-MiniLM-L6-v2',
        normalize: bool = True
    ):
        super().__init__()
        self.dim = dim
        self.mode = mode
        self.normalize = normalize

        # Initialize text encoder if in text mode
        if mode == 'text':
            if not HAS_SENTENCE_TRANSFORMERS:
                raise ImportError(
                    "sentence-transformers required for text mode. "
                    "Install with: pip install sentence-transformers"
                )
            self.text_encoder = SentenceTransformer(text_model)
            # Get embedding dimension from model
            test_emb = self.text_encoder.encode("test", convert_to_tensor=True)
            self.text_dim = test_emb.shape[0]
        else:
            self.text_encoder = None
            self.text_dim = None

        # Projection layer: maps concatenated [amplitude, phase] to target dim
        # Input is 2*dim (amplitude + phase), output is dim
        self.proj = nn.Linear(dim * 2, dim)

        # Learnable phase scaling for adaptive torsion strength
        self.phase_scale = nn.Parameter(torch.tensor(1.0))

    def _encode_text(self, text: Union[str, List[str]]) -> torch.Tensor:
        """Encode text using sentence-transformers"""
        if isinstance(text, str):
            text = [text]

        # Get embeddings
        embeddings = self.text_encoder.encode(
            text,
            convert_to_tensor=True,
            show_progress_bar=False
        )

        return embeddings

    def _encode_eeg(self, raw: Union[torch.Tensor, 'mne.Epochs']) -> torch.Tensor:
        """Encode EEG data from MNE Epochs or raw tensor"""
        if HAS_MNE and isinstance(raw, mne.BaseEpochs):
            # Extract data from MNE Epochs: [epochs, channels, times]
            data = raw.get_data()
            # Average across epochs and flatten channels
            signal = torch.tensor(data.mean(axis=0).flatten(), dtype=torch.float32)
        elif HAS_MNE and isinstance(raw, mne.io.BaseRaw):
            # Extract from Raw object
            data = raw.get_data()
            signal = torch.tensor(data.flatten(), dtype=torch.float32)
        else:
            # Assume it's already a tensor
            if not isinstance(raw, torch.Tensor):
                signal = torch.tensor(raw, dtype=torch.float32)
            else:
                signal = raw

        return signal

    def _encode_spectral(self, raw: torch.Tensor) -> torch.Tensor:
        """Pass-through for spectral data (already in tensor form)"""
        if not isinstance(raw, torch.Tensor):
            return torch.tensor(raw, dtype=torch.float32)
        return raw

    def forward(
        self,
        raw: Union[str, List[str], torch.Tensor, 'mne.Epochs']
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode raw input to torsion engram

        Args:
            raw: Input data in modal format:
                - text: str or List[str]
                - eeg: torch.Tensor [samples] or mne.Epochs
                - spectral: torch.Tensor [samples]

        Returns:
            Tuple of:
                - engram: Compressed torsion engram [dim] or [batch, dim]
                - phases: Trefoil phases [dim] or [batch, dim]
        """
        # Step 1: Modal pre-processing
        if self.mode == 'text':
            signal = self._encode_text(raw)
            # Text embeddings are already high-dim, use directly
            batch_mode = True
        elif self.mode == 'eeg':
            signal = self._encode_eeg(raw)
            batch_mode = False
        else:  # spectral
            signal = self._encode_spectral(raw)
            batch_mode = False

        # Handle batching
        if batch_mode:
            return self._forward_batch(signal)
        else:
            return self._forward_single(signal)

    def _forward_single(self, signal: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process single signal"""
        # Step 2: FFT spectral decomposition
        f = fft.rfft(signal)

        # Extract amplitude and phase
        amp = torch.abs(f)

        # Step 3: Trefoil phase embedding
        phase = trefoil_phase(signal)

        # Step 4: Compress to target dimension
        # Truncate or pad to dim
        if amp.shape[0] >= self.dim:
            amp_compressed = amp[:self.dim]
            phase_compressed = phase[:self.dim]
        else:
            # Pad with zeros
            pad_size = self.dim - amp.shape[0]
            amp_compressed = torch.cat([amp, torch.zeros(pad_size)])
            phase_compressed = torch.cat([phase, torch.zeros(pad_size)])

        # Scale phases by learnable parameter
        phase_compressed = phase_compressed * self.phase_scale

        # Step 5: Project concatenated features
        combined = torch.cat([amp_compressed, phase_compressed])  # [2*dim]
        engram = self.proj(combined.unsqueeze(0)).squeeze(0)  # [dim]

        # Optional normalization
        if self.normalize:
            engram = torch.nn.functional.normalize(engram, p=2, dim=0)

        return engram, phase_compressed

    def _forward_batch(self, signal: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process batch of signals"""
        batch_size = signal.shape[0]
        engrams = []
        phases_list = []

        for i in range(batch_size):
            engram, phases = self._forward_single(signal[i])
            engrams.append(engram)
            phases_list.append(phases)

        engrams_batch = torch.stack(engrams)
        phases_batch = torch.stack(phases_list)

        return engrams_batch, phases_batch

    def get_fidelity(self, signal: torch.Tensor, engram: torch.Tensor) -> float:
        """
        Compute reconstruction fidelity as cosine similarity

        Args:
            signal: Original signal
            engram: Encoded engram

        Returns:
            Fidelity score in [0, 1]
        """
        # Compress signal to same dim for comparison
        if signal.shape[0] > self.dim:
            signal_compressed = signal[:self.dim]
        else:
            signal_compressed = torch.cat([
                signal,
                torch.zeros(self.dim - signal.shape[0])
            ])

        # Normalize both
        signal_norm = torch.nn.functional.normalize(signal_compressed, p=2, dim=0)
        engram_norm = torch.nn.functional.normalize(engram, p=2, dim=0)

        # Cosine similarity
        fidelity = torch.dot(signal_norm, engram_norm).item()

        return max(0.0, fidelity)  # Clamp to [0, 1]
