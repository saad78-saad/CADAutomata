from pathlib import Path
from cad_automata.ingestion.bom_parser import BOMParser
from cad_automata.rag.vector_store import LocalVectorStore
from cad_automata.geometry.parser import GeometryParser, GeometricMetrics
from cad_automata.adaptation.engine import AdaptationEngine
from cad_automata.integration.cad_client import CADClient
from cad_automata.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting CADAutomata pipeline test...")

    # 1. Initialize RAG Vector Store & Index a component
    vector_store = LocalVectorStore()
    sample_part_path = "sample_bracket.stl"
    vector_store.add_component(
        comp_id="BRACKET-001",
        text_metadata="Standard L-bracket steel mounting bracket with 4 holes",
        file_path=sample_part_path
    )

    # 2. Create a sample BOM CSV file for testing
    bom_file = Path("sample_bom.csv")
    with open(bom_file, "w", encoding="utf-8") as f:
        f.write("component_id,name,target_length_mm,target_width_mm,target_height_mm,material\n")
        f.write("BRACKET-001,Mounting Bracket,105.0,52.0,25.0,Steel\n")

    # 3. Initialize CAD Client (automatically enters mock mode on your laptop)
    cad_client = CADClient()

    # 4. Ingest BOM sequentially
    parser = BOMParser(bom_file)
    for bom_item in parser.parse_sequential():
        logger.info(f"Processing BOM Item: {bom_item.component_id} - {bom_item.name}")

        # RAG Retrieval
        match = vector_store.search(query_text=bom_item.name)
        logger.info(f"Retrieved base template: {match['id']} from {match['file_path']}")

        # Geometric Parsing (Falls back to mock metrics if STL doesn't exist)
        if Path(match['file_path']).exists():
            metrics = GeometryParser.parse_mesh(match['file_path'])
        else:
            metrics = GeometricMetrics(
                bounding_box_dims=(100.0, 50.0, 20.0),
                volume=10000.0,
                surface_area=2500.0,
                hole_count=4
            )

        # Adaptation Evaluation
        delta = AdaptationEngine.evaluate_fitting(bom_item, metrics)

        # CAD Client Execution (Simulated locally, live on your friend's PC)
        output_filename = f"output_{bom_item.component_id}.sldprt"
        cad_client.open_part(match['file_path'])
        cad_client.execute_adaptation(
            part_name=match['id'],
            dx=delta.delta_x,
            dy=delta.delta_y,
            dz=delta.delta_z,
            output_path=output_filename
        )

    logger.info("CADAutomata pipeline test completed successfully!")

if __name__ == "__main__":
    main()