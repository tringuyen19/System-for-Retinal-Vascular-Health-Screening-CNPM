from typing import Optional

class AiAnnotation:
    def __init__(self, annotation_id: int, analysis_id: int, heatmap_url: str, 
                 description: Optional[str]):
        self.annotation_id = annotation_id
        self.analysis_id = analysis_id
        self.heatmap_url = heatmap_url
        self.description = description

