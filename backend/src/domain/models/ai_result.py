from decimal import Decimal

class AiResult:
    def __init__(self, result_id: int, analysis_id: int, disease_type: str, 
                 risk_level: str, confidence_score: Decimal):
        self.result_id = result_id
        self.analysis_id = analysis_id
        self.disease_type = disease_type
        self.risk_level = risk_level
        self.confidence_score = confidence_score

