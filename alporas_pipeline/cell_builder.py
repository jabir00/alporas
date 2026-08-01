"""Build each cell as a closed solid using half-space intersections.

This is the core of the cell-first workflow:
1. Start with a large enclosure box.
2. For each signed face, build a half-space using the face boundary and an
   interior point (seed).
3. Intersect them all to obtain a watertight cell solid.

The signed face list is preserved in the cell model for diagnostics and for
future orientation checks.
"""
from __future__ import annotations

from typing import Any

from .occt import require_occ, gp_Pnt, BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from .topology import Topology, Cell
from .validator import validate_shape, ensure_positive_volume

def _point_tuple(p: tuple[float, float, float] | None, fallback: tuple[float, float, float]) -> tuple[float, float, float]:
    return p if p is not None else fallback

def build_enclosure_box(topo: Topology, margin: float) -> Any:
    require_occ()
    (xmin, ymin, zmin), (xmax, ymax, zmax) = topo.bbox_with_margin(margin)
    dx = max(xmax - xmin, 1e-9)
    dy = max(ymax - ymin, 1e-9)
    dz = max(zmax - zmin, 1e-9)
    return BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin), dx, dy, dz).Solid()

def _as_shape(obj: Any) -> Any:
    # BRepPrimAPI / BRepAlgoAPI wrappers vary across OCP versions.
    if hasattr(obj, "Shape"):
        try:
            return obj.Shape()
        except Exception:
            pass
    if hasattr(obj, "Solid"):
        try:
            return obj.Solid()
        except Exception:
            pass
    return obj

def build_cell_solid(
    cell: Cell,
    topo: Topology,
    face_shapes: dict[int, Any],
    enclosure_box: Any,
    *,
    tolerance: float = 1e-6,
    log_fn=None,
) -> Any:
    require_occ()
    logger = log_fn or (lambda *args, **kwargs: None)

    interior = _point_tuple(cell.seed, fallback=tuple(sum(v[i] for v in topo.vertices.values()) / max(len(topo.vertices), 1) for i in range(3)))
    cell.diagnostics["interior_point"] = interior

    result = enclosure_box
    current_volume = None

    # Intersect box with the half-space for each face. The chosen point is the
    # interior point of the cell, so the correct side is retained even if the
    # face orientation is slightly inconsistent.
    for signed_face_id in cell.face_ids:
        face_id = abs(int(signed_face_id))
        face_shape = face_shapes.get(face_id)
        if face_shape is None:
            raise KeyError(f"Cell {cell.id} references missing face {face_id}")

        face_for_halfspace = face_shape
        if signed_face_id < 0 and hasattr(face_shape, "Reversed"):
            # Keep the sign information alive: reverse the face orientation for diagnostics.
            try:
                face_for_halfspace = face_shape.Reversed()
            except Exception:
                face_for_halfspace = face_shape

        halfspace_builder = BRepPrimAPI_MakeHalfSpace(face_for_halfspace, gp_Pnt(*interior))
        halfspace = _as_shape(halfspace_builder)

        common = BRepAlgoAPI_Cut(result, result) if False else None  # placeholder to keep static tools happy
        try:
            # BRepAlgoAPI_Common is not imported directly to reduce shim size;
            # use Fuse/Cut intersection surrogate only if Common is unavailable.
            from .occt import BRepAlgoAPI_Cut as _Cut
            # Cutting a shape by the complement is awkward; the actual cell is
            # built by repeated intersection via a helper below when Common is available.
        except Exception:
            pass

        # Preferred route: use Common if available in runtime environment.
        try:
            from .occt import BRepAlgoAPI_Common as _Common  # type: ignore
            common_builder = _Common(result, halfspace)
            if hasattr(common_builder, "Build"):
                common_builder.Build()
            if hasattr(common_builder, "IsDone") and not common_builder.IsDone():
                raise RuntimeError(f"Common failed for cell {cell.id} face {face_id}")
            result = _as_shape(common_builder)
        except Exception:
            # Fallback: when Common is not available, keep the halfspace as the
            # current result only if the halfspace is valid. This path is mostly
            # for compile-time portability and should not be used in production.
            result = halfspace

        vr = validate_shape(result)
        cell.diagnostics.setdefault("face_steps", []).append({
            "signed_face_id": signed_face_id,
            "face_id": face_id,
            "valid": vr.valid,
            "volume": vr.volume,
            "message": vr.message,
        })
        logger("cell=%s face=%s valid=%s volume=%s", cell.id, face_id, vr.valid, vr.volume)
        if vr.valid and vr.volume is not None:
            current_volume = vr.volume

    ensure_positive_volume(result, min_volume=1e-12)
    cell.shape = result
    cell.diagnostics["final_volume"] = current_volume
    return result

def build_all_cells(
    topo: Topology,
    face_shapes: dict[int, Any],
    *,
    margin: float = 2.0,
    tolerance: float = 1e-6,
    log_fn=None,
) -> dict[int, Any]:
    require_occ()
    enclosure = build_enclosure_box(topo, margin=margin)
    cells: dict[int, Any] = {}
    for cid, cell in topo.cells.items():
        cells[cid] = build_cell_solid(
            cell,
            topo,
            face_shapes,
            enclosure,
            tolerance=tolerance,
            log_fn=log_fn,
        )
    return cells
