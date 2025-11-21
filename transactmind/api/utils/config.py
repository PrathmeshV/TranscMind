from pydantic import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = 'api/models/model.onnx'
    TAXONOMY_PATH: str = 'api/models/taxonomy.json'

settings = Settings()
