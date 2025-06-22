from pydantic import BaseModel

class DetectionResult(BaseModel):
    count: int
    boxes: list