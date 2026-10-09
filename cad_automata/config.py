import logging
import sys
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CADAutomata"
    sqlite_db_path: str = "./cad_vectors.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    solidworks_visible: bool = True
    max_workers: int = 1  # Strictly sequential to prevent COM thread race conditions
    tolerance_limit: float = 0.01

    class Config:
        env_file = ".env"

settings = Settings()

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger