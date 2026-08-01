"""Optional OpenCASCADE / OCP import shim.

The package is importable even when OCP is missing. Runtime functions that
need CAD operations call :func:`require_occ`.
"""
from __future__ import annotations

from typing import Any

HAVE_OCC = False
OCC_ERROR: Exception | None = None

gp_Pnt = gp_Vec = gp_Dir = gp_Pln = None
BRepBuilderAPI_MakePolygon = BRepBuilderAPI_MakeFace = None
BRepBuilderAPI_Sewing = BRepBuilderAPI_MakeSolid = None
BRepPrimAPI_MakeBox = BRepPrimAPI_MakeHalfSpace = None
BRepOffsetAPI_MakeThickSolid = BRepOffsetAPI_MakeOffsetShape = None
BRepAlgoAPI_Cut = BRepAlgoAPI_Fuse = None
BRepCheck_Analyzer = None
ShapeFix_Shape = ShapeFix_Solid = None
BRepMesh_IncrementalMesh = None
STEPControl_Writer = None
StlAPI_Writer = None
IFSelect_RetDone = None
GProp_GProps = None
brepgprop = None
TopTools_ListOfShape = None
GeomAbs_Arc = None
TopLoc_Location = None
BRepBuilderAPI_Transform = None
gp_Trsf = None

def _try_import() -> None:
    global HAVE_OCC, OCC_ERROR
    global gp_Pnt, gp_Vec, gp_Dir, gp_Pln
    global BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    global BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    global BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace
    global BRepOffsetAPI_MakeThickSolid, BRepOffsetAPI_MakeOffsetShape
    global BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    global BRepCheck_Analyzer, ShapeFix_Shape, ShapeFix_Solid
    global BRepMesh_IncrementalMesh, STEPControl_Writer, StlAPI_Writer
    global IFSelect_RetDone, GProp_GProps, brepgprop
    global TopTools_ListOfShape, GeomAbs_Arc, TopLoc_Location
    global BRepBuilderAPI_Transform, gp_Trsf

    try:
        try:
            from OCP.gp import gp_Pnt as _gp_Pnt, gp_Vec as _gp_Vec, gp_Dir as _gp_Dir, gp_Pln as _gp_Pln
            from OCP.BRepBuilderAPI import (
                BRepBuilderAPI_MakePolygon as _BRepBuilderAPI_MakePolygon,
                BRepBuilderAPI_MakeFace as _BRepBuilderAPI_MakeFace,
                BRepBuilderAPI_Sewing as _BRepBuilderAPI_Sewing,
                BRepBuilderAPI_MakeSolid as _BRepBuilderAPI_MakeSolid,
                BRepBuilderAPI_Transform as _BRepBuilderAPI_Transform,
            )
            from OCP.BRepPrimAPI import (
                BRepPrimAPI_MakeBox as _BRepPrimAPI_MakeBox,
                BRepPrimAPI_MakeHalfSpace as _BRepPrimAPI_MakeHalfSpace,
            )
            from OCP.BRepOffsetAPI import (
                BRepOffsetAPI_MakeThickSolid as _BRepOffsetAPI_MakeThickSolid,
                BRepOffsetAPI_MakeOffsetShape as _BRepOffsetAPI_MakeOffsetShape,
            )
            from OCP.BRepAlgoAPI import (
                BRepAlgoAPI_Cut as _BRepAlgoAPI_Cut,
                BRepAlgoAPI_Fuse as _BRepAlgoAPI_Fuse,
            )
            from OCP.BRepCheck import BRepCheck_Analyzer as _BRepCheck_Analyzer
            from OCP.ShapeFix import ShapeFix_Shape as _ShapeFix_Shape, ShapeFix_Solid as _ShapeFix_Solid
            from OCP.BRepMesh import BRepMesh_IncrementalMesh as _BRepMesh_IncrementalMesh
            from OCP.STEPControl import STEPControl_Writer as _STEPControl_Writer
            from OCP.StlAPI import StlAPI_Writer as _StlAPI_Writer
            from OCP.IFSelect import IFSelect_RetDone as _IFSelect_RetDone
            from OCP.GProp import GProp_GProps as _GProp_GProps
            from OCP.BRepGProp import brepgprop as _brepgprop
            from OCP.TopTools import TopTools_ListOfShape as _TopTools_ListOfShape
            from OCP.GeomAbs import GeomAbs_Arc as _GeomAbs_Arc
            from OCP.TopLoc import TopLoc_Location as _TopLoc_Location
            from OCP.gp import gp_Trsf as _gp_Trsf
        except Exception:
            from OCC.Core.gp import gp_Pnt as _gp_Pnt, gp_Vec as _gp_Vec, gp_Dir as _gp_Dir, gp_Pln as _gp_Pln
            from OCC.Core.BRepBuilderAPI import (
                BRepBuilderAPI_MakePolygon as _BRepBuilderAPI_MakePolygon,
                BRepBuilderAPI_MakeFace as _BRepBuilderAPI_MakeFace,
                BRepBuilderAPI_Sewing as _BRepBuilderAPI_Sewing,
                BRepBuilderAPI_MakeSolid as _BRepBuilderAPI_MakeSolid,
                BRepBuilderAPI_Transform as _BRepBuilderAPI_Transform,
            )
            from OCC.Core.BRepPrimAPI import (
                BRepPrimAPI_MakeBox as _BRepPrimAPI_MakeBox,
                BRepPrimAPI_MakeHalfSpace as _BRepPrimAPI_MakeHalfSpace,
            )
            from OCC.Core.BRepOffsetAPI import (
                BRepOffsetAPI_MakeThickSolid as _BRepOffsetAPI_MakeThickSolid,
                BRepOffsetAPI_MakeOffsetShape as _BRepOffsetAPI_MakeOffsetShape,
            )
            from OCC.Core.BRepAlgoAPI import (
                BRepAlgoAPI_Cut as _BRepAlgoAPI_Cut,
                BRepAlgoAPI_Fuse as _BRepAlgoAPI_Fuse,
            )
            from OCC.Core.BRepCheck import BRepCheck_Analyzer as _BRepCheck_Analyzer
            from OCC.Core.ShapeFix import ShapeFix_Shape as _ShapeFix_Shape, ShapeFix_Solid as _ShapeFix_Solid
            from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh as _BRepMesh_IncrementalMesh
            from OCC.Core.STEPControl import STEPControl_Writer as _STEPControl_Writer
            from OCC.Core.StlAPI import StlAPI_Writer as _StlAPI_Writer
            from OCC.Core.IFSelect import IFSelect_RetDone as _IFSelect_RetDone
            from OCC.Core.GProp import GProp_GProps as _GProp_GProps
            from OCC.Core.BRepGProp import brepgprop as _brepgprop
            from OCC.Core.TopTools import TopTools_ListOfShape as _TopTools_ListOfShape
            from OCC.Core.GeomAbs import GeomAbs_Arc as _GeomAbs_Arc
            from OCC.Core.TopLoc import TopLoc_Location as _TopLoc_Location
            from OCC.Core.gp import gp_Trsf as _gp_Trsf

        gp_Pnt = _gp_Pnt
        gp_Vec = _gp_Vec
        gp_Dir = _gp_Dir
        gp_Pln = _gp_Pln
        BRepBuilderAPI_MakePolygon = _BRepBuilderAPI_MakePolygon
        BRepBuilderAPI_MakeFace = _BRepBuilderAPI_MakeFace
        BRepBuilderAPI_Sewing = _BRepBuilderAPI_Sewing
        BRepBuilderAPI_MakeSolid = _BRepBuilderAPI_MakeSolid
        BRepPrimAPI_MakeBox = _BRepPrimAPI_MakeBox
        BRepPrimAPI_MakeHalfSpace = _BRepPrimAPI_MakeHalfSpace
        BRepOffsetAPI_MakeThickSolid = _BRepOffsetAPI_MakeThickSolid
        BRepOffsetAPI_MakeOffsetShape = _BRepOffsetAPI_MakeOffsetShape
        BRepAlgoAPI_Cut = _BRepAlgoAPI_Cut
        BRepAlgoAPI_Fuse = _BRepAlgoAPI_Fuse
        BRepCheck_Analyzer = _BRepCheck_Analyzer
        ShapeFix_Shape = _ShapeFix_Shape
        ShapeFix_Solid = _ShapeFix_Solid
        BRepMesh_IncrementalMesh = _BRepMesh_IncrementalMesh
        STEPControl_Writer = _STEPControl_Writer
        StlAPI_Writer = _StlAPI_Writer
        IFSelect_RetDone = _IFSelect_RetDone
        GProp_GProps = _GProp_GProps
        brepgprop = _brepgprop
        TopTools_ListOfShape = _TopTools_ListOfShape
        GeomAbs_Arc = _GeomAbs_Arc
        TopLoc_Location = _TopLoc_Location
        BRepBuilderAPI_Transform = _BRepBuilderAPI_Transform
        gp_Trsf = _gp_Trsf

        HAVE_OCC = True
        OCC_ERROR = None
    except Exception as exc:  # pragma: no cover - runtime convenience
        HAVE_OCC = False
        OCC_ERROR = exc

_try_import()

def occ_available() -> bool:
    return HAVE_OCC

def require_occ() -> None:
    if not HAVE_OCC:
        raise RuntimeError(
            "OpenCASCADE/OCP is not available in this environment. "
            "Install cadquery-ocp or FreeCAD Python bindings to run geometry operations."
        ) from OCC_ERROR

def safe_shape_method(shape: Any, method_name: str, default: Any = None) -> Any:
    if shape is None:
        return default
    method = getattr(shape, method_name, None)
    if callable(method):
        try:
            return method()
        except Exception:
            return default
    return default
