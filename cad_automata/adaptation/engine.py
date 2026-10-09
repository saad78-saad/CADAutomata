from pydantic import BaseModel, ConfigDict
from cad_automata.ingestion.bom_parser import BOMItem
from cad_automata.geometry.parser import GeometricMetrics
from cad_automata.logger import get_logger

logger = get_logger(__name__)

class ScalingDelta(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    delta_x: float
    delta_y: float
    delta_z: float
    is_within_tolerance: bool

class AdaptationEngine:
    @staticmethod
    def evaluate_fitting(bom_item: BOMItem, metrics: GeometricMetrics, tolerance: float = 0.01) -> ScalingDelta:
        cur_x, cur_y, cur_z = metrics.bounding_box_dims
        
        dx = bom_item.target_length_mm - cur_x
        dy = bom_item.target_width_mm - cur_y
        dz = bom_item.target_height_mm - cur_z
        
        within_tolerance = all(abs(d) <= tolerance for d in [dx, dy, dz])
        
        logger.info(f"Calculated scaling deltas for {bom_item.component_id}: dX={dx:.3f}, dY={dy:.3f}, dZ={dz:.3f}")
        return ScalingDelta(delta_x=dx, delta_y=dy, delta_z=dz, is_within_tolerance=within_tolerance)