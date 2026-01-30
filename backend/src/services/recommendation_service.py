"""
Recommendation Service - Generate Automated Health Recommendations
Business logic for generating recommendations based on AI analysis results
"""

from typing import List, Optional
from domain.exceptions import ValidationException


class RecommendationService:
    """Service for generating automated health recommendations and warnings"""
    
    @staticmethod
    def generate_recommendations(risk_level: str, disease_type: Optional[str] = None) -> str:
        """
        Generate health recommendations based on risk level
        
        Args:
            risk_level: Risk level ('high', 'medium', 'low')
            disease_type: Optional disease type for more specific recommendations
            
        Returns:
            str: Recommendation message
            
        Raises:
            ValidationException: If risk_level is invalid
        """
        risk_level = risk_level.lower()
        
        recommendations_map = {
            'high': (
                "⚠️ HIGH RISK DETECTED: Immediate consultation with an ophthalmologist "
                "is strongly recommended. Please schedule an appointment as soon as possible "
                "for further evaluation and treatment planning."
            ),
            'medium': (
                "⚠️ MODERATE RISK: Regular monitoring is advised. Please schedule a "
                "follow-up appointment within 1-2 months to track any changes in your condition."
            ),
            'low': (
                "✅ LOW RISK: Continue with regular eye checkups as recommended by your "
                "healthcare provider. Maintain a healthy lifestyle and monitor any changes in vision."
            )
        }
        
        if risk_level not in recommendations_map:
            raise ValidationException(f"Invalid risk level: {risk_level}. Must be 'high', 'medium', or 'low'")
        
        recommendation = recommendations_map[risk_level]
        
        # Add disease-specific recommendations if provided
        if disease_type and disease_type.lower() != 'normal':
            recommendation += f"\n\nDisease detected: {disease_type}. Please discuss this with your doctor."
        
        return recommendation
    
    @staticmethod
    def generate_warnings(risk_level: str, confidence_score: float) -> List[str]:
        """
        Generate warnings based on risk level and confidence score
        
        Args:
            risk_level: Risk level ('high', 'medium', 'low')
            confidence_score: AI confidence score (0.0 to 1.0)
            
        Returns:
            List[str]: List of warning messages
        """
        warnings = []
        risk_level = risk_level.lower()
        
        # High risk with high confidence
        if risk_level == 'high' and confidence_score > 0.9:
            warnings.append("🚨 URGENT: High confidence high-risk detection detected. Immediate medical attention recommended.")
        
        # High risk with low confidence
        if risk_level == 'high' and confidence_score < 0.6:
            warnings.append("⚠️ CAUTION: High risk detected but with lower confidence. Manual review by doctor is strongly recommended.")
        
        # Low confidence regardless of risk
        if confidence_score < 0.5:
            warnings.append("⚠️ NOTE: Low confidence score. Manual review by healthcare professional is recommended.")
        
        # Medium risk with high confidence
        if risk_level == 'medium' and confidence_score > 0.8:
            warnings.append("📋 REMINDER: Moderate risk detected. Regular follow-up appointments are important.")
        
        return warnings
    
    @staticmethod
    def generate_preventive_advice(risk_level: str) -> str:
        """
        Generate preventive advice based on risk level
        
        Args:
            risk_level: Risk level ('high', 'medium', 'low')
            
        Returns:
            str: Preventive advice message
        """
        risk_level = risk_level.lower()
        
        advice_map = {
            'high': (
                "Preventive Measures:\n"
                "- Avoid smoking and limit alcohol consumption\n"
                "- Control blood sugar and blood pressure if diabetic/hypertensive\n"
                "- Protect eyes from UV radiation with sunglasses\n"
                "- Maintain a healthy diet rich in antioxidants\n"
                "- Follow your doctor's treatment plan strictly"
            ),
            'medium': (
                "Preventive Measures:\n"
                "- Regular eye examinations every 6-12 months\n"
                "- Monitor blood sugar and blood pressure\n"
                "- Maintain healthy lifestyle habits\n"
                "- Report any vision changes immediately"
            ),
            'low': (
                "Preventive Measures:\n"
                "- Continue regular eye checkups annually\n"
                "- Maintain healthy lifestyle\n"
                "- Protect eyes from UV radiation\n"
                "- Stay hydrated and eat a balanced diet"
            )
        }
        
        return advice_map.get(risk_level, advice_map['low'])

