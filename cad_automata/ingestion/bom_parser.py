import csv
from pathlib import Path
from typing import Generator
from pydantic import BaseModel, Field
from cad_automata.logger import get_logger

logger = get_logger(__name__)

class BOMItem(BaseModel):
    component_id: str = Field(..., description="Unique part identifier")
    name: str
    target_length_mm: float = Field(..., gt=0)
    target_width_mm: float = Field(..., gt=0)
    target_height_mm: float = Field(..., gt=0)
    material: str

class BOMParser:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def parse_sequential(self) -> Generator[BOMItem, None, None]:
        """Parses BOM line-by-line to strictly eliminate concurrency and rate-limit risks."""
        if not self.file_path.exists():
            logger.error(f"BOM file not found at {self.file_path}")
            raise FileNotFoundError(f"BOM file missing: {self.file_path}")

        logger.info(f"Starting sequential BOM ingestion from {self.file_path}")
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    item = BOMItem(
                        component_id=row["component_id"],
                        name=row["name"],
                        target_length_mm=float(row["target_length_mm"]),
                        target_width_mm=float(row["target_width_mm"]),
                        target_height_mm=float(row["target_height_mm"]),
                        material=row["material"]
                    )
                    yield item
                except Exception as e:
                    logger.error(f"Validation error on BOM row {row_idx}: {e}")
                    raise ValueError(f"Invalid BOM format at row {row_idx}: {e}")