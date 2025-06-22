from typing import Any, Dict
 
class DetectorBase:
    def detect(self, frame: Any) -> Dict:
        raise NotImplementedError 