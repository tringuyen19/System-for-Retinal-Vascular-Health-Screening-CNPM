"""
Retinal Image Service - Business Logic Layer
Handles retinal image upload and management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from domain.models.retinal_image import RetinalImage
from domain.models.iretinal_image_repository import IRetinalImageRepository
from domain.exceptions import NotFoundException, ValidationException
from domain.validators import RetinalImageValidator


class RetinalImageService:
    def __init__(self, repository: IRetinalImageRepository):
        self.repository = repository
    
    def upload_image(self, patient_id: int, clinic_id: int, uploaded_by: int,
                    image_type: str, eye_side: str, image_url: str, 
                    status: str = 'uploaded') -> RetinalImage:
        """
        Upload retinal image with validation
        
        Args:
            patient_id: Patient ID
            clinic_id: Clinic ID
            uploaded_by: Account ID of uploader
            image_type: Type of image (fundus, oct, fluorescein)
            eye_side: Eye side (left, right, both)
            image_url: URL to the image
            status: Image status (default: 'uploaded')
            
        Returns:
            RetinalImage: Created image domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate using domain validators
        RetinalImageValidator.validate_image_type(image_type)
        RetinalImageValidator.validate_eye_side(eye_side)
        RetinalImageValidator.validate_image_url(image_url)
        
        # Business rule: Validate status
        valid_statuses = ['uploaded', 'processing', 'analyzed', 'error']
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status. Must be one of: {valid_statuses}")
        
        image = self.repository.add(
            patient_id=patient_id,
            clinic_id=clinic_id,
            uploaded_by=uploaded_by,
            image_type=image_type,
            eye_side=eye_side,
            image_url=image_url,
            upload_time=datetime.now(),
            status=status
        )
        
        if not image:
            raise ValueError("Failed to upload image")
        
        return image
    
    def get_image_by_id(self, image_id: int) -> RetinalImage:
        """
        Get image by ID
        
        Raises:
            NotFoundException: If image not found
        """
        image = self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundException(f"Image {image_id} not found")
        return image
    
    def get_images_by_patient(self, patient_id: int) -> List[RetinalImage]:
        """Get all images for a patient"""
        return self.repository.get_by_patient(patient_id)
    
    def get_images_by_clinic(self, clinic_id: int) -> List[RetinalImage]:
        """Get all images from a clinic"""
        return self.repository.get_by_clinic(clinic_id)
    
    def get_images_by_status(self, status: str) -> List[RetinalImage]:
        """Get images by status"""
        return self.repository.get_by_status(status)
    
    def get_pending_analysis(self) -> List[RetinalImage]:
        """Get images pending AI analysis"""
        return self.repository.get_pending_analysis()
    
    def mark_as_processing(self, image_id: int) -> Optional[RetinalImage]:
        """Mark image as processing"""
        return self.repository.mark_as_processing(image_id)
    
    def mark_as_analyzed(self, image_id: int) -> Optional[RetinalImage]:
        """Mark image as analyzed"""
        return self.repository.mark_as_analyzed(image_id)
    
    def mark_as_error(self, image_id: int) -> Optional[RetinalImage]:
        """Mark image as error"""
        return self.repository.mark_as_error(image_id)
    
    def update_image(self, image_id: int, **kwargs) -> Optional[RetinalImage]:
        """Update image information"""
        return self.repository.update(image_id, **kwargs)
    
    def delete_image(self, image_id: int) -> bool:
        """Delete image"""
        return self.repository.delete(image_id)
    
    def count_by_status(self, status: str) -> int:
        """Count images by status"""
        return self.repository.count_by_status(status)
    
    def get_image_statistics(self) -> dict:
        """Get image statistics"""
        return {
            'total_images': len(self.repository.get_all()),
            'uploaded': self.repository.count_by_status('uploaded'),
            'processing': self.repository.count_by_status('processing'),
            'analyzed': self.repository.count_by_status('analyzed'),
            'error': self.repository.count_by_status('error')
        }
    
    def upload_bulk_images(self, images_data: List[dict]) -> Dict[str, Any]:
        """Upload multiple images in bulk"""
        uploaded_images = []
        errors = []
        
        for img_data in images_data:
            try:
                # Validate image type
                valid_types = ['fundus', 'oct', 'angiography']
                if img_data.get('image_type') not in valid_types:
                    errors.append({
                        'index': len(uploaded_images) + len(errors),
                        'error': f"Invalid image type: {img_data.get('image_type')}"
                    })
                    continue
                
                # Validate eye side
                valid_sides = ['left', 'right', 'both']
                if img_data.get('eye_side') not in valid_sides:
                    errors.append({
                        'index': len(uploaded_images) + len(errors),
                        'error': f"Invalid eye side: {img_data.get('eye_side')}"
                    })
                    continue
                
                # Upload image
                image = self.repository.add(
                    patient_id=img_data['patient_id'],
                    clinic_id=img_data['clinic_id'],
                    uploaded_by=img_data['uploaded_by'],
                    image_type=img_data['image_type'],
                    eye_side=img_data['eye_side'],
                    image_url=img_data['image_url'],
                    upload_time=datetime.now(),
                    status=img_data.get('status', 'uploaded')
                )
                
                if image:
                    uploaded_images.append(image)
                else:
                    errors.append({
                        'index': len(uploaded_images) + len(errors),
                        'error': 'Failed to upload image'
                    })
            except Exception as e:
                errors.append({
                    'index': len(uploaded_images) + len(errors),
                    'error': str(e)
                })
        
        return {
            'uploaded': uploaded_images,
            'errors': errors,
            'total': len(images_data),
            'success_count': len(uploaded_images),
            'error_count': len(errors)
        }