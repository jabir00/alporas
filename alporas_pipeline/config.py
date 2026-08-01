"""Configuration dataclass and helpers."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class PipelineConfig:
    input_path: Path
    output_path: Path
    wall_thickness: float = 0.20
    tolerance: float = 1e-6
    margin: float = 2.0
    fuse_output: bool = True
    export_intermediates: bool = False
    debug_dir: Path | None = None
    log_level: str = "INFO"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_path"] = str(self.input_path)
        data["output_path"] = str(self.output_path)
        data["debug_dir"] = str(self.debug_dir) if self.debug_dir else None
        return data
