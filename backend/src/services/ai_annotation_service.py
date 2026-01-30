"""
AI Annotation Service - Business Logic Layer
Handles AI annotation and heatmap management
"""

from typing import List, Optional
from domain.models.ai_annotation import AiAnnotation
from domain.models.iai_annotation_repository import IAiAnnotationRepository
from domain.exceptions import NotFoundException, ValidationException
from domain.validators import RetinalImageValidator


class AiAnnotationService:
    def __init__(self, repository: IAiAnnotationRepository):
        self.repository = repository
    
    def create_annotation(self, analysis_id: int, heatmap_url: str, 
                         description: Optional[str] = None) -> AiAnnotation:
        """
        Create AI annotation with validation (FR-4)
        
        Args:
            analysis_id: Analysis ID
            heatmap_url: URL to heatmap image
            description: Optional description of annotation
            
        Returns:
            AiAnnotation: Created annotation domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate heatmap URL
        RetinalImageValidator.validate_image_url(heatmap_url)
        
        annotation = self.repository.add(
            analysis_id=analysis_id,
            heatmap_url=heatmap_url,
            description=description
        )
        
        if not annotation:
            raise ValueError("Failed to create annotation")
        
        return annotation
    
    def get_annotation_by_id(self, annotation_id: int) -> AiAnnotation:
        """
        Get annotation by ID
        
        Raises:
            NotFoundException: If annotation not found
        """
        annotation = self.repository.get_by_id(annotation_id)
        if not annotation:
            raise NotFoundException(f"Annotation {annotation_id} not found")
        return annotation
    
    def get_annotation_by_analysis(self, analysis_id: int) -> Optional[AiAnnotation]:
        """Get annotation by analysis ID"""
        return self.repository.get_by_analysis_id(analysis_id)
    
    def get_all_with_descriptions(self) -> List[AiAnnotation]:
        """Get all annotations with descriptions"""
        return self.repository.get_all_with_descriptions()
    
    def list_all_annotations(self) -> List[AiAnnotation]:
        """Get all annotations"""
        return self.repository.get_all()
    
    def update_heatmap(self, annotation_id: int, heatmap_url: str) -> Optional[AiAnnotation]:
        """Update heatmap URL"""
        return self.repository.update_heatmap(annotation_id, heatmap_url)
    
    def update_annotation(self, annotation_id: int, **kwargs) -> Optional[AiAnnotation]:
        """Update annotation"""
        return self.repository.update(annotation_id, **kwargs)
    
    def delete_annotation(self, annotation_id: int) -> bool:
        """Delete annotation"""
        return self.repository.delete(annotation_id)
    
    def count_annotations(self) -> int:
        """Count total annotations"""
        return self.repository.count()
