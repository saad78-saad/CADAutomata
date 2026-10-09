import trimesh
from pydantic import BaseModel
from cad_automata.logger import get_logger

logger = get_logger(__name__)

class GeometricMetrics(BaseModel):
    bounding_box_dims: tuple[float, float, float]
    volume: float
    surface_area: float
    hole_count: int

class GeometryParser:
    @staticmethod
    def parse_mesh(file_path: str) -> GeometricMetrics:
        logger.info(f"Loading mesh for geometric analysis: {file_path}")
        mesh = trimesh.load(file_path, force="mesh")
        
        extents = mesh.bounding_box.extents
        volume = float(mesh.volume)
        surface_area = float(mesh.area)
        
        # Heuristic topological check for internal cylindrical features (holes)
        euler_char = mesh.euler_number
        hole_count = max(0, int((2 - euler_char) / 2))

        metrics = GeometricMetrics(
            bounding_box_dims=(float(extents[0]), float(extents[1]), float(extents[2])),
            volume=volume,
            surface_area=surface_area,
            hole_count=hole_count
        )
        logger.info(f"Extracted metrics - BBox: {metrics.bounding_box_dims}, Volume: {volume:.2f}")
        return metrics