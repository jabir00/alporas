"""Shape validation and healing utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .occt import (
    require_occ,
    BRepCheck_Analyzer,
    ShapeFix_Shape,
    ShapeFix_Solid,
    GProp_GProps,
    brepgprop,
)

@dataclass(slots=True)
class ValidationResult:
    valid: bool
    volume: float | None = None
    message: str = ""

def shape_is_valid(shape: Any) -> bool:
    require_occ()
    try:
        return bool(BRepCheck_Analyzer(shape).IsValid())
    except Exception:
        return False

def shape_volume(shape: Any) -> float:
    require_occ()
    props = GProp_GProps()
    brepgprop.VolumeProperties(shape, props)
    return float(props.Mass())

def validate_shape(shape: Any, min_volume: float = 1e-12) -> ValidationResult:
    if shape is None:
        return ValidationResult(False, None, "shape is None")
    try:
        valid = shape_is_valid(shape)
        volume = shape_volume(shape) if valid else None
        if not valid:
            return ValidationResult(False, volume, "BRepCheck_Analyzer reported invalid shape")
        if volume is not None and volume < min_volume:
            return ValidationResult(False, volume, f"volume < {min_volume:g}")
        return ValidationResult(True, volume, "ok")
    except Exception as exc:
        return ValidationResult(False, None, str(exc))

def heal_shape(shape: Any) -> Any:
    require_occ()
    fixer = ShapeFix_Shape(shape)
    fixer.Perform()
    healed = fixer.Shape()
    try:
        solid_fixer = ShapeFix_Solid(healed)
        solid_fixer.Perform()
        healed = solid_fixer.Solid()
    except Exception:
        pass
    return healed

def ensure_positive_volume(shape: Any, min_volume: float = 1e-12) -> None:
    result = validate_shape(shape, min_volume=min_volume)
    if not result.valid:
        raise ValueError(f"Invalid shape: {result.message} (volume={result.volume})")
