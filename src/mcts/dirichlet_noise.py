"""
Applies Dirichlet exploration noise to root priors.
"""

from __future__ import annotations

from typing import Dict

import numpy as np


def apply_dirichlet_noise(
    priors: Dict[str, float],
    alpha: float = 0.3,
    epsilon: float = 0.25,
    seed: int | None = None,
) -> Dict[str, float]:
    """
    Blend Dirichlet noise into a prior distribution.

    new_prior = (1 - epsilon) * prior + epsilon * dirichlet_sample

    Args:
        priors: Mapping move UCI -> prior probability
        alpha: Dirichlet alpha parameter
        epsilon: Noise blending factor
        seed: Optional random seed

    Returns:
        New normalized prior mapping
    """
    if not priors:
        return {}

    rng = np.random.default_rng(seed)
    moves = list(priors.keys())
    base = np.array([priors[m] for m in moves], dtype=np.float64)

    noise = rng.dirichlet([alpha] * len(moves))
    blended = (1.0 - epsilon) * base + epsilon * noise

    total = blended.sum()
    if total <= 0:
        blended = np.full_like(blended, 1.0 / len(blended))
    else:
        blended = blended / total

    return {move: float(prob) for move, prob in zip(moves, blended)}
