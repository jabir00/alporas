"""Create wall solids from closed cell solids."""
from __future__ import annotations

from typing import Any

from .offset_builder import make_inner_offset
from .boolean_utils import cut_shape
from .validator import validate_shape, ensure_positive_volume

def build_wall_from_cell(
    cell_shape: Any,
    wall_thickness: float,
    *,
    tolerance: float = 1e-6,
    prefer_boolean_cut: bool = True,
) -> Any:
    """Build a wall solid from a closed cell solid.

    The primary workflow is:
        cell solid -> inner offset -> boolean cut -> wall

    If the offset result already represents a valid wall solid in the local
    OCC build, the boolean cut remains the safest post-processing step.
    """
    inner = make_inner_offset(cell_shape, wall_thickness, tolerance=tolerance)
    vr = validate_shape(inner)
    if not vr.valid:
        raise ValueError(f"Inner offset is invalid: {vr.message}")

    if prefer_boolean_cut:
        wall = cut_shape(cell_shape, inner, heal=True)
        ensure_positive_volume(wall, min_volume=1e-12)
        return wall

    return inner
