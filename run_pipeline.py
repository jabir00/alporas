"""Command line entry point for the Alporas foam pipeline."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from alporas_pipeline.logger import setup_logging
from alporas_pipeline.config import PipelineConfig
from alporas_pipeline.parser import parse_tess
from alporas_pipeline.geometry_builder import build_all_faces
from alporas_pipeline.cell_builder import build_all_cells
from alporas_pipeline.wall_generator import build_wall_from_cell
from alporas_pipeline.boolean_utils import fuse_shapes
from alporas_pipeline.validator import validate_shape, heal_shape
from alporas_pipeline.exporter import export_step, export_stl
from alporas_pipeline.occt import occ_available, require_occ

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cell-first, offset-second Alporas foam generator"
    )
    p.add_argument("--input", required=True, help="Input Neper .tess file")
    p.add_argument("--output", required=True, help="Output STEP file")
    p.add_argument("--thickness", type=float, default=0.20, help="Wall thickness")
    p.add_argument("--tolerance", type=float, default=1e-6, help="Geometry tolerance")
    p.add_argument("--margin", type=float, default=2.0, help="Bounding-box margin")
    p.add_argument("--no-fuse", action="store_true", help="Do not fuse walls into a single body")
    p.add_argument("--export-stl", action="store_true", help="Also export STL")
    p.add_argument("--debug-dir", default=None, help="Save intermediate files here")
    p.add_argument("--log-file", default=None, help="Write log output to file")
    p.add_argument("--log-level", default="INFO", help="DEBUG, INFO, WARNING, ...")
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger = setup_logging(level=level, log_file=args.log_file)
    logger.info("OCC available: %s", occ_available())

    cfg = PipelineConfig(
        input_path=Path(args.input),
        output_path=Path(args.output),
        wall_thickness=float(args.thickness),
        tolerance=float(args.tolerance),
        margin=float(args.margin),
        fuse_output=not args.no_fuse,
        export_intermediates=bool(args.debug_dir),
        debug_dir=Path(args.debug_dir) if args.debug_dir else None,
        log_level=args.log_level.upper(),
    )

    if cfg.debug_dir:
        cfg.debug_dir.mkdir(parents=True, exist_ok=True)

    require_occ()

    topo = parse_tess(cfg.input_path)
    logger.info("Parsed tessellation: %d vertices, %d edges, %d faces, %d cells",
                len(topo.vertices), len(topo.edges), len(topo.faces), len(topo.cells))

    face_shapes = build_all_faces(topo)

    cells = build_all_cells(
        topo,
        face_shapes,
        margin=cfg.margin,
        tolerance=cfg.tolerance,
        log_fn=logger.debug,
    )
    logger.info("Built %d cell solids", len(cells))

    wall_shapes = []
    for cid, cell_shape in cells.items():
        wall_shape = build_wall_from_cell(
            cell_shape,
            cfg.wall_thickness,
            tolerance=cfg.tolerance,
            prefer_boolean_cut=True,
        )
        cell = topo.cells[cid]
        cell.wall_shape = wall_shape
        wall_shapes.append(wall_shape)

        vr = validate_shape(wall_shape)
        logger.info("Cell %s wall valid=%s volume=%s", cid, vr.valid, vr.volume)

        if cfg.debug_dir and cfg.export_intermediates:
            export_step(cell_shape, cfg.debug_dir / f"cell_{cid:05d}_solid.step")
            export_step(wall_shape, cfg.debug_dir / f"cell_{cid:05d}_wall.step")

    if not wall_shapes:
        raise RuntimeError("No wall shapes were generated")

    final_shape = fuse_shapes(wall_shapes) if cfg.fuse_output and len(wall_shapes) > 1 else wall_shapes[0]
    final_shape = heal_shape(final_shape)

    vr = validate_shape(final_shape)
    logger.info("Final foam valid=%s volume=%s", vr.valid, vr.volume)
    if not vr.valid:
        raise RuntimeError(f"Final foam failed validation: {vr.message}")

    out_path = export_step(final_shape, cfg.output_path)
    logger.info("Wrote STEP: %s", out_path)

    if args.export_stl:
        stl_path = cfg.output_path.with_suffix(".stl")
        export_stl(final_shape, stl_path, deflection=max(cfg.wall_thickness / 10.0, 0.05))
        logger.info("Wrote STL: %s", stl_path)

    if cfg.debug_dir:
        summary = {
            "config": cfg.as_dict(),
            "vertices": len(topo.vertices),
            "edges": len(topo.edges),
            "faces": len(topo.faces),
            "cells": len(topo.cells),
            "output": str(out_path),
        }
        (cfg.debug_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
