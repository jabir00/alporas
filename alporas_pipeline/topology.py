"""Topology data models used by the pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class Vertex:
    id: int
    x: float
    y: float
    z: float
    state: int | None = None

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

@dataclass(slots=True)
class Edge:
    id: int
    v1: int
    v2: int
    state: int | None = None

@dataclass(slots=True)
class Face:
    id: int
    vertex_ids: list[int] = field(default_factory=list)
    edge_ids: list[int] = field(default_factory=list)
    state: int | None = None
    plane: tuple[float, float, float, float] | None = None
    shape: Any = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class Cell:
    id: int
    face_ids: list[int] = field(default_factory=list)   # signed face ids preserve orientation
    seed: tuple[float, float, float] | None = None
    shape: Any = None
    wall_shape: Any = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

@dataclass
class Topology:
    source_path: Path | None = None
    vertices: dict[int, Vertex] = field(default_factory=dict)
    edges: dict[int, Edge] = field(default_factory=dict)
    faces: dict[int, Face] = field(default_factory=dict)
    cells: dict[int, Cell] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def all_points(self) -> list[tuple[float, float, float]]:
        return [v.as_tuple() for v in self.vertices.values()]

    def bounds(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        pts = self.all_points()
        if not pts:
            return (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
        xs, ys, zs = zip(*pts)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def bbox_with_margin(self, margin: float = 1.0) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        (xmin, ymin, zmin), (xmax, ymax, zmax) = self.bounds()
        return (xmin - margin, ymin - margin, zmin - margin), (xmax + margin, ymax + margin, zmax + margin)

    def face_ids_for_cell(self, cell_id: int) -> list[int]:
        return self.cells[cell_id].face_ids
