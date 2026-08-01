"""Parser for Neper .tess files.

This parser focuses on preserving signed topology:
- vertex ids and coordinates
- edge ids and endpoint ids
- face vertex loops + signed edge loops
- cell signed face lists + optional seed coordinates
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .topology import Topology, Vertex, Edge, Face, Cell

SECTION_HEADERS = {"vertex", "edge", "face", "cell", "polyhedron", "seed"}

def _tokenize_numeric(line: str) -> list[float | int]:
    out: list[float | int] = []
    for token in line.replace(",", " ").split():
        try:
            if any(ch in token for ch in ".eE"):
                out.append(float(token))
            else:
                out.append(int(token))
        except ValueError:
            continue
    return out

class NeperTessParser:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def parse(self) -> Topology:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        topo = Topology(source_path=self.path)
        current_section: str | None = None

        for raw in self.path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line:
                continue

            if line.startswith("**"):
                head = line[2:].strip().split()
                current_section = head[0].lower() if head else None
                continue

            if current_section not in SECTION_HEADERS:
                continue

            nums = _tokenize_numeric(line)
            if not nums:
                continue

            if current_section == "vertex":
                self._parse_vertex(nums, topo)
            elif current_section == "edge":
                self._parse_edge(nums, topo)
            elif current_section == "face":
                self._parse_face(nums, topo)
            elif current_section in {"cell", "polyhedron"}:
                self._parse_cell(nums, topo)
            elif current_section == "seed":
                self._parse_seed(nums, topo)

        return topo

    def _parse_vertex(self, nums: list[float | int], topo: Topology) -> None:
        if len(nums) < 4:
            return
        vid = int(nums[0])
        x, y, z = float(nums[1]), float(nums[2]), float(nums[3])
        state = int(nums[4]) if len(nums) >= 5 else None
        topo.vertices[vid] = Vertex(vid, x, y, z, state)

    def _parse_edge(self, nums: list[float | int], topo: Topology) -> None:
        if len(nums) < 3:
            return
        eid = int(nums[0])
        v1, v2 = int(nums[1]), int(nums[2])
        state = int(nums[3]) if len(nums) >= 4 else None
        topo.edges[eid] = Edge(eid, v1, v2, state)

    def _parse_face(self, nums: list[float | int], topo: Topology) -> None:
        # Common Neper-ish layout:
        # fid, nverts, [vertex ids...], nedges, [signed edge ids...], optional extras
        if len(nums) < 3:
            return
        fid = int(nums[0])
        cursor = 1
        nverts = int(nums[cursor]); cursor += 1
        vertex_ids = [int(v) for v in nums[cursor:cursor + max(nverts, 0)]]
        cursor += max(nverts, 0)

        edge_ids: list[int] = []
        if cursor < len(nums):
            try:
                nedges = int(nums[cursor]); cursor += 1
                edge_ids = [int(v) for v in nums[cursor:cursor + max(nedges, 0)]]
                cursor += max(nedges, 0)
            except Exception:
                edge_ids = []

        state = int(nums[cursor]) if cursor < len(nums) and float(nums[cursor]).is_integer() else None
        topo.faces[fid] = Face(fid, vertex_ids=vertex_ids, edge_ids=edge_ids, state=state)

    def _parse_cell(self, nums: list[float | int], topo: Topology) -> None:
        # Common layout:
        # cid, nfaces, [signed face ids...], optional seed x y z
        if len(nums) < 3:
            return
        cid = int(nums[0])
        cursor = 1
        nfaces = int(nums[cursor]); cursor += 1
        face_ids = [int(v) for v in nums[cursor:cursor + max(nfaces, 0)]]
        cursor += max(nfaces, 0)

        seed = None
        if len(nums) >= cursor + 3:
            seed = (float(nums[cursor]), float(nums[cursor + 1]), float(nums[cursor + 2]))

        topo.cells[cid] = Cell(cid, face_ids=face_ids, seed=seed)

    def _parse_seed(self, nums: list[float | int], topo: Topology) -> None:
        # Some tess files carry a seed section that can be used as interior points.
        if len(nums) >= 4:
            cid = int(nums[0])
            topo.cells.setdefault(cid, Cell(cid)).seed = (float(nums[1]), float(nums[2]), float(nums[3]))

def parse_tess(path: str | Path) -> Topology:
    return NeperTessParser(path).parse()
