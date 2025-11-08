"""
Penrose P3 Tiling Generator

Generates aperiodic Penrose P3 rhombi tilings for geometric attention nodes.
Uses recursive subdivision of thick/thin rhombi with golden ratio scaling.

The aperiodic structure creates natural hierarchical clustering while
avoiding crystalline periodicity, enabling rich topological routing.
"""

import torch
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


# Golden ratio - fundamental to Penrose tilings
PHI = (1 + np.sqrt(5)) / 2


@dataclass
class Rhombus:
    """Represents a single rhombus in the tiling"""
    vertices: np.ndarray  # [4, 2] - four 2D vertices
    type: str  # 'thick' or 'thin'
    center: np.ndarray  # [2] - center point
    angle: float  # rotation angle


def generate_penrose(
    level: int = 2,
    num_nodes: int = 20,
    scale: float = 1.0,
    seed: Optional[int] = None
) -> torch.Tensor:
    """
    Generate Penrose P3 tiling node positions

    Creates an aperiodic tiling using recursive rhombus subdivision,
    then samples node positions from the resulting vertex set.

    Args:
        level: Subdivision depth (0-4 recommended, higher = more vertices)
        num_nodes: Number of nodes to sample from the tiling
        scale: Overall scale factor for the tiling
        seed: Random seed for reproducible node sampling

    Returns:
        Tensor of shape [num_nodes, 3] with node positions (Z=0)
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate initial "sun" pattern - 10 rhombi around origin
    initial_rhombi = _generate_sun_pattern(scale * (PHI ** level))

    # Recursively subdivide to desired level
    rhombi = initial_rhombi
    for _ in range(level):
        rhombi = _subdivide_rhombi(rhombi)

    # Extract all unique vertices
    all_vertices = []
    for rhomb in rhombi:
        all_vertices.extend(rhomb.vertices.tolist())

    # Remove duplicates (with tolerance for numerical errors)
    unique_vertices = _remove_duplicate_vertices(np.array(all_vertices))

    # Sample num_nodes vertices
    if len(unique_vertices) < num_nodes:
        # If not enough vertices, pad with perturbed copies
        print(f"Warning: Only {len(unique_vertices)} unique vertices "
              f"(requested {num_nodes}). Padding with jittered duplicates.")
        while len(unique_vertices) < num_nodes:
            # Add jittered copies
            jitter = np.random.randn(len(unique_vertices), 2) * 0.01 * scale
            unique_vertices = np.vstack([unique_vertices, unique_vertices + jitter])
        unique_vertices = unique_vertices[:num_nodes]
    else:
        # Random sampling
        indices = np.random.choice(len(unique_vertices), num_nodes, replace=False)
        unique_vertices = unique_vertices[indices]

    # Embed in 3D (Z = 0)
    positions_3d = np.column_stack([
        unique_vertices,
        np.zeros(num_nodes)
    ])

    return torch.tensor(positions_3d, dtype=torch.float32)


def _generate_sun_pattern(radius: float = 1.0) -> List[Rhombus]:
    """
    Generate initial "sun" pattern - 10 rhombi arranged radially

    This is the traditional starting configuration for Penrose P3 tilings.
    """
    rhombi = []

    # Angles for 10 rhombi (36° apart)
    angles = np.linspace(0, 2 * np.pi, 11)[:-1]  # 10 angles

    # Alternate thick and thin rhombi
    for i, angle in enumerate(angles):
        rhomb_type = 'thick' if i % 2 == 0 else 'thin'
        rhomb = _create_rhombus(
            center=np.array([0.0, 0.0]),
            angle=angle,
            size=radius,
            rhomb_type=rhomb_type
        )
        rhombi.append(rhomb)

    return rhombi


def _create_rhombus(
    center: np.ndarray,
    angle: float,
    size: float,
    rhomb_type: str
) -> Rhombus:
    """
    Create a single rhombus

    Args:
        center: Center point [x, y]
        angle: Rotation angle in radians
        size: Edge length
        rhomb_type: 'thick' (72°) or 'thin' (36°)
    """
    if rhomb_type == 'thick':
        # Thick rhombus: 72° and 108° angles
        half_angle = np.pi / 5  # 36° in radians
    else:
        # Thin rhombus: 36° and 144° angles
        half_angle = np.pi / 10  # 18° in radians

    # Create vertices in local coordinates
    local_vertices = np.array([
        [size * np.cos(half_angle), size * np.sin(half_angle)],
        [size, 0],
        [size * np.cos(half_angle), -size * np.sin(half_angle)],
        [0, 0]
    ])

    # Rotation matrix
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rotation = np.array([
        [cos_a, -sin_a],
        [sin_a, cos_a]
    ])

    # Rotate and translate
    vertices = (rotation @ local_vertices.T).T + center

    return Rhombus(
        vertices=vertices,
        type=rhomb_type,
        center=center,
        angle=angle
    )


def _subdivide_rhombi(rhombi: List[Rhombus]) -> List[Rhombus]:
    """
    Subdivide all rhombi according to Penrose inflation rules

    Each rhombus splits into 2-3 smaller rhombi scaled by 1/φ
    """
    new_rhombi = []

    for rhomb in rhombi:
        subdivided = _subdivide_single_rhombus(rhomb)
        new_rhombi.extend(subdivided)

    return new_rhombi


def _subdivide_single_rhombus(rhomb: Rhombus) -> List[Rhombus]:
    """
    Subdivide a single rhombus using Penrose inflation rules

    Thick rhombus → 2 thick + 1 thin
    Thin rhombus → 1 thick + 1 thin
    """
    v = rhomb.vertices
    scale = 1 / PHI

    if rhomb.type == 'thick':
        # Thick rhombus subdivides into 2 thick + 1 thin
        # Calculate division points along edges
        p1 = v[0] + (v[1] - v[0]) / PHI
        p2 = v[2] + (v[3] - v[2]) / PHI

        # Create three new rhombi
        new_rhombi = [
            Rhombus(
                vertices=np.array([v[0], p1, p2, v[3]]),
                type='thin',
                center=(v[0] + p1 + p2 + v[3]) / 4,
                angle=rhomb.angle
            ),
            Rhombus(
                vertices=np.array([p1, v[1], v[2], p2]),
                type='thick',
                center=(p1 + v[1] + v[2] + p2) / 4,
                angle=rhomb.angle + np.pi / 5
            ),
            Rhombus(
                vertices=np.array([v[3], p2, p1, v[0]]),
                type='thick',
                center=(v[3] + p2 + p1 + v[0]) / 4,
                angle=rhomb.angle - np.pi / 5
            )
        ]

    else:  # thin
        # Thin rhombus subdivides into 1 thick + 1 thin
        # Calculate division point
        p = v[1] + (v[2] - v[1]) / PHI

        # Create two new rhombi
        new_rhombi = [
            Rhombus(
                vertices=np.array([v[0], v[1], p, v[3]]),
                type='thin',
                center=(v[0] + v[1] + p + v[3]) / 4,
                angle=rhomb.angle
            ),
            Rhombus(
                vertices=np.array([v[3], p, v[2], v[3]]),
                type='thick',
                center=(v[3] + p + v[2]) / 3,  # Triangle approximation
                angle=rhomb.angle + np.pi / 5
            )
        ]

    return new_rhombi


def _remove_duplicate_vertices(
    vertices: np.ndarray,
    tolerance: float = 1e-6
) -> np.ndarray:
    """
    Remove duplicate vertices within tolerance

    Uses spatial hashing for efficiency with large vertex sets
    """
    unique = []
    seen = set()

    # Round to tolerance for hashing
    grid_size = tolerance * 10
    for v in vertices:
        # Create hash key
        key = (
            int(v[0] / grid_size),
            int(v[1] / grid_size)
        )

        # Check nearby grid cells for duplicates
        is_duplicate = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_key = (key[0] + dx, key[1] + dy)
                if check_key in seen:
                    # Check actual distance
                    for u in unique:
                        if np.linalg.norm(v - u) < tolerance:
                            is_duplicate = True
                            break
                if is_duplicate:
                    break
            if is_duplicate:
                break

        if not is_duplicate:
            unique.append(v)
            seen.add(key)

    return np.array(unique)


def visualize_penrose(
    positions: torch.Tensor,
    save_path: Optional[str] = None
):
    """
    Visualize Penrose tiling node positions

    Args:
        positions: Tensor of shape [N, 3] with node positions
        save_path: Optional path to save figure
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available for visualization")
        return

    pos_np = positions.cpu().numpy()

    plt.figure(figsize=(10, 10))
    plt.scatter(pos_np[:, 0], pos_np[:, 1], s=50, alpha=0.6, c='blue')
    plt.axis('equal')
    plt.grid(True, alpha=0.3)
    plt.title(f'Penrose P3 Tiling - {len(pos_np)} Nodes')
    plt.xlabel('X')
    plt.ylabel('Y')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()

    plt.close()
