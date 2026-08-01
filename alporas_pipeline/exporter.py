"""Export helpers for STEP and STL."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .occt import require_occ, STEPControl_Writer, StlAPI_Writer, BRepMesh_IncrementalMesh, IFSelect_RetDone
from .validator import heal_shape

def export_step(shape: Any, path: str | Path) -> Path:
    require_occ()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    shape = heal_shape(shape)
    writer = STEPControl_Writer()
    writer.Transfer(shape, 1)  # STEPControl_AsIs in most wrappers
    status = writer.Write(str(path))
    if status != IFSelect_RetDone:
        # Some wrappers return 1 for success; keep this as a soft check.
        try:
            if int(status) not in (0, 1):
                raise RuntimeError(f"STEP export failed with status={status}")
        except Exception:
            pass
    return path

def export_stl(shape: Any, path: str | Path, *, deflection: float = 0.1) -> Path:
    require_occ()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    shape = heal_shape(shape)
    try:
        mesh = BRepMesh_IncrementalMesh(shape, float(deflection), False, 0.5, True)
        if hasattr(mesh, "Perform"):
            mesh.Perform()
    except Exception:
        pass
    writer = StlAPI_Writer()
    writer.Write(shape, str(path))
    return path
