from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import os

from cad_automata.ingestion.bom_parser import BOMItem
from cad_automata.rag.vector_store import LocalVectorStore
from cad_automata.geometry.parser import GeometryParser, GeometricMetrics
from cad_automata.adaptation.engine import AdaptationEngine
from cad_automata.integration.cad_client import CADClient

app = FastAPI(
    title="CADAutomata Cloud API",
    version="0.1.0",
    servers=[
        {"url": "https://cadautomata.onrender.com", "description": "Render Production Server"},
        {"url": "http://localhost:8000", "description": "Local Development Server"}
    ]
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessBOMRequest(BaseModel):
    component_id: str
    name: str
    target_length_mm: float
    target_width_mm: float
    target_height_mm: float
    material: str

@app.post("/api/process-component")
def process_component(req: ProcessBOMRequest):
    try:
        bom_item = BOMItem(
            component_id=req.component_id,
            name=req.name,
            target_length_mm=req.target_length_mm,
            target_width_mm=req.target_width_mm,
            target_height_mm=req.target_height_mm,
            material=req.material
        )

        vector_store = LocalVectorStore()
        match = vector_store.search(query_text=bom_item.name)

        metrics = GeometricMetrics(
            bounding_box_dims=(100.0, 50.0, 20.0),
            volume=10000.0,
            surface_area=2500.0,
            hole_count=4
        )

        delta = AdaptationEngine.evaluate_fitting(bom_item, metrics)

        cad_client = CADClient()
        output_filename = f"output_{bom_item.component_id}.sldprt"
        cad_client.open_part(match.get('file_path', 'sample.stl'))
        cad_client.execute_adaptation(
            part_name=match.get('id', 'TEMPLATE'),
            dx=delta.delta_x,
            dy=delta.delta_y,
            dz=delta.delta_z,
            output_path=output_filename
        )

        return {
            "status": "success",
            "component_id": bom_item.component_id,
            "scaling_deltas": {
                "dx": delta.delta_x,
                "dy": delta.delta_y,
                "dz": delta.delta_z,
                "within_tolerance": delta.is_within_tolerance
            },
            "output_file": output_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))