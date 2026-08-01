"""Build OCC face geometry from parsed topology.

This module preserves signed topology data in the model objects, but the
planar face construction itself uses ordered vertex loops.
"""
from __future__ import annotations

from typing import Any

from .occt import require_occ, gp_Pnt, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from .topology import Topology, Face, Vertex
from .validator import validate_shape

def ordered_vertices_for_face(face: Face, topo: Topology) -> list[int]:
    if face.vertex_ids:
        return list(face.vertex_ids)
    # Fallback: reconstruct from signed edges by chaining endpoints.
    if not face.edge_ids:
        raise ValueError(f"Face {face.id} has neither vertex_ids nor edge_ids")
    edges = [topo.edges[abs(eid)] for eid in face.edge_ids]
    chain = [edges[0].v1, edges[0].v2]
    used = {0}
    while len(used) < len(edges):
        tail = chain[-1]
        extended = False
        for idx, edge in enumerate(edges):
            if idx in used:
                continue
            if edge.v1 == tail:
                chain.append(edge.v2)
                used.add(idx)
                extended = True
                break
            if edge.v2 == tail:
                chain.append(edge.v1)
                used.add(idx)
                extended = True
                break
        if not extended:
            break
    if len(chain) >= 3 and chain[0] == chain[-1]:
        chain.pop()
    return chain

def build_face_shape(face: Face, topo: Topology) -> Any:
    require_occ()
    vertex_ids = ordered_vertices_for_face(face, topo)
    if len(vertex_ids) < 3:
        raise ValueError(f"Face {face.id} does not contain enough vertices")

    poly = BRepBuilderAPI_MakePolygon()
    for vid in vertex_ids:
        v = topo.vertices[vid]
        poly.Add(gp_Pnt(float(v.x), float(v.y), float(v.z)))
    poly.Close()

    wire = poly.Wire()
    face_shape = BRepBuilderAPI_MakeFace(wire).Face()

    # Basic validity check
    result = validate_shape(face_shape)
    if not result.valid:
        raise ValueError(f"Invalid face {face.id}: {result.message}")
    face.shape = face_shape
    face.diagnostics["vertex_loop"] = vertex_ids
    face.diagnostics["volume"] = result.volume
    return face_shape

def build_all_faces(topo: Topology) -> dict[int, Any]:
    require_occ()
    shapes: dict[int, Any] = {}
    for fid, face in topo.faces.items():
        shapes[fid] = build_face_shape(face, topo)
    return shapes

def build_bounding_box_shape(topo: Topology, margin: float = 1.0) -> Any:
    require_occ()
    (xmin, ymin, zmin), (xmax, ymax, zmax) = topo.bbox_with_margin(margin)
    dx = max(xmax - xmin, 1e-9)
    dy = max(ymax - ymin, 1e-9)
    dz = max(zmax - zmin, 1e-9)
    return BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin), dx, dy, dz).Solid()
