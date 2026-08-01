"""Boolean helper functions."""
from __future__ import annotations

from typing import Any, Iterable

from .occt import require_occ, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from .validator import validate_shape, heal_shape

def _shape_of(builder: Any) -> Any:
    for name in ("Shape", "Solid"):
        fn = getattr(builder, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                continue
    return builder

def cut_shape(base: Any, tool: Any, *, heal: bool = True) -> Any:
    require_occ()
    builder = BRepAlgoAPI_Cut(base, tool)
    if hasattr(builder, "Build"):
        builder.Build()
    if hasattr(builder, "IsDone") and not builder.IsDone():
        raise RuntimeError("Boolean cut failed")
    result = _shape_of(builder)
    if heal:
        try:
            result = heal_shape(result)
        except Exception:
            pass
    return result

def fuse_shapes(shapes: Iterable[Any], *, heal: bool = True) -> Any:
    require_occ()
    shapes = list(shapes)
    if not shapes:
        raise ValueError("No shapes to fuse")
    result = shapes[0]
    for nxt in shapes[1:]:
        builder = BRepAlgoAPI_Fuse(result, nxt)
        if hasattr(builder, "Build"):
            builder.Build()
        if hasattr(builder, "IsDone") and not builder.IsDone():
            raise RuntimeError("Boolean fuse failed")
        result = _shape_of(builder)
        if heal:
            try:
                result = heal_shape(result)
            except Exception:
                pass
    return result
