# Alporas Foam Pipeline

A modular **cell-first, offset-second** pipeline for generating Alporas-like foam geometry from a Neper tessellation and exporting CAD geometry suitable for validation in FreeCAD and meshing for Abaqus.

## What it does

1. Parses a Neper `.tess` file.
2. Preserves signed topology for faces and edges.
3. Builds each cell as a closed solid by intersecting half-spaces.
4. Generates a wall body by inward offsetting the cell.
5. Optionally cuts the cell with its offset to form the wall volume.
6. Fuses all wall bodies into a single foam body.
7. Heals and exports the final shape to STEP.

## Project layout

```
alporas_pipeline/
  __init__.py
  occt.py
  topology.py
  config.py
  logger.py
  parser.py
  geometry_builder.py
  cell_builder.py
  offset_builder.py
  wall_generator.py
  boolean_utils.py
  validator.py
  exporter.py
run_pipeline.py
main.py
README.md
requirements.txt
```

## Install

Recommended environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For geometry execution, install either:

- `cadquery-ocp`, or
- FreeCAD Python bindings

## Run

```bash
python run_pipeline.py       --input your_model.tess       --output alporas_foam.step       --thickness 0.20       --margin 2.0       --debug-dir debug_out       --export-stl
```

## Notes

- The pipeline is designed to keep topology orientation information alive.
- The cell construction stage uses half-space intersections instead of repeated clipping of partially-built wall panels.
- `BRepOffsetAPI_MakeThickSolid` is used when available; a fallback offset strategy is included for portability.
- The generated STEP file can be opened in FreeCAD for visual inspection and further conversion to Abaqus workflows.

## Practical advice

- Start with one or a few cells and check the debug STEP files.
- If a cell fails, inspect the corresponding `cell_XXXXX_solid.step` and `cell_XXXXX_wall.step` outputs.
- Keep wall thickness smaller than the smallest cell dimension.
- Use the same unit system everywhere.

## Troubleshooting

- If the script says OpenCASCADE is unavailable, install `cadquery-ocp` or use a FreeCAD Python environment.
- If a cell collapses to zero volume, your wall thickness is too large for that local geometry or the input tessellation contains a degeneracy.
- If FreeCAD imports a null body, inspect the intermediate STEP files and reduce the offset thickness or increase tolerance slightly.

## Outputs

- `*.step` final CAD body
- `*.stl` optional mesh export
- `debug_out/summary.json`
- `debug_out/cell_XXXXX_solid.step`
- `debug_out/cell_XXXXX_wall.step`
