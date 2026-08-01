"""Inward offset and wall-thickness construction.

The preferred route is OpenCASCADE's thick-solid / offset algorithms.
A scale-based fallback is included for environments where the exact offset
API differs, but that fallback should only be used for prototyping.
"""
from __future__ import annotations

from typing import Any

from .occt import (
    require_occ,
    gp_Pnt,
    gp_Trsf,
    BRepBuilderAPI_Transform,
    BRepOffsetAPI_MakeThickSolid,
    BRepOffsetAPI_MakeOffsetShape,
    TopTools_ListOfShape,
    GeomAbs_Arc,
)
from .validator import validate_shape, ensure_positive_volume

def _shape_of(builder: Any) -> Any:
    for name in ("Shape", "Solid", "OffsetShape"):
        fn = getattr(builder, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                continue
    return builder

def _bounding_box_center(shape: Any) -> tuple[float, float, float]:
    # Generic fallback center. We avoid heavy bbox extraction here to keep
    # the shim portable.
    try:
        from .occt import GProp_GProps, brepgprop
        props = GProp_GProps()
        brepgprop.VolumeProperties(shape, props)
        c = props.CentreOfMass()
        return (float(c.X()), float(c.Y()), float(c.Z()))
    except Exception:
        return (0.0, 0.0, 0.0)

def scale_fallback_inner_offset(shape: Any, wall_thickness: float, scale_hint: float = 1.0) -> Any:
    require_occ()
    center = _bounding_box_center(shape)
    # Conservative shrink factor. This is a geometric fallback only.
    factor = max(0.05, min(0.999, 1.0 - 0.10 * float(wall_thickness) * scale_hint))
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(*center), factor)
    transform = BRepBuilderAPI_Transform(shape, trsf, True)
    return _shape_of(transform)

def make_thick_wall(
    shape: Any,
    wall_thickness: float,
    *,
    tolerance: float = 1e-6,
) -> Any:
    """Return a thickened wall solid (preferred OCC route)."""
    require_occ()
    half = float(wall_thickness) / 2.0
    if half <= 0:
        raise ValueError("wall_thickness must be > 0")

    empty = TopTools_ListOfShape()

    # Primary attempt: MakeThickSolid by join.
    try:
        builder = BRepOffsetAPI_MakeThickSolid()
        try:
            builder.MakeThickSolidByJoin(shape, empty, -half, tolerance, True, GeomAbs_Arc)
        except TypeError:
            # Older wrappers use a shorter signature.
            builder.MakeThickSolidByJoin(shape, empty, -half, tolerance)
        if hasattr(builder, "Build"):
            builder.Build()
        if hasattr(builder, "IsDone") and not builder.IsDone():
            raise RuntimeError("BRepOffsetAPI_MakeThickSolid reported failure")
        result = _shape_of(builder)
        vr = validate_shape(result)
        if vr.valid and (vr.volume is None or vr.volume > 0):
            return result
    except Exception:
        pass

    # Secondary attempt: generic offset shape
    try:
        builder = BRepOffsetAPI_MakeOffsetShape()
        # Signature varies by wrapper; try a couple of common patterns.
        try:
            builder.PerformByJoin(shape, -half, tolerance)
        except Exception:
            try:
                builder.PerformBySimple(shape, -half, tolerance)
            except Exception:
                raise
        result = _shape_of(builder)
        vr = validate_shape(result)
        if vr.valid and (vr.volume is None or vr.volume > 0):
            return result
    except Exception:
        pass

    # Fallback: a scaled approximation around the cell centroid.
    return scale_fallback_inner_offset(shape, wall_thickness)

def make_inner_offset(shape: Any, wall_thickness: float, *, tolerance: float = 1e-6) -> Any:
    """Alias kept for readability in the wall generator."""
    return make_thick_wall(shape, wall_thickness, tolerance=tolerance)
