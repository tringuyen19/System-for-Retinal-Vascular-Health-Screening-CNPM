from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
from infrastructure.repositories.medical_report_repository import MedicalReportRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.ai_result_repository import AiResultRepository
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.databases.mssql import session
from services.medical_report_service import MedicalReportService
from services.patient_profile_service import PatientProfileService
from services.doctor_profile_service import DoctorProfileService
from services.ai_analysis_service import AiAnalysisService
from services.ai_result_service import AiResultService
from services.retinal_image_service import RetinalImageService
from services.export_service import ExportService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import MedicalReportCreateRequestSchema, MedicalReportUpdateRequestSchema, MedicalReportResponseSchema
from datetime import datetime

medical_report_bp = Blueprint('medical_report', __name__, url_prefix='/api/medical-reports')

# Initialize repositories (only for service initialization)
report_repo = MedicalReportRepository(session)
patient_repo = PatientProfileRepository(session)
doctor_repo = DoctorProfileRepository(session)
analysis_repo = AiAnalysisRepository(session)
result_repo = AiResultRepository(session)
image_repo = RetinalImageRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
report_service = MedicalReportService(report_repo)
patient_service = PatientProfileService(patient_repo)
doctor_service = DoctorProfileService(doctor_repo)
analysis_service = AiAnalysisService(analysis_repo)
result_service = AiResultService(result_repo)
image_service = RetinalImageService(image_repo)
export_service = ExportService()


@medical_report_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Medical Report
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Medical report service is running")


@medical_report_bp.route('', methods=['POST'])
def create_report():
    """
    Create a new medical report with automated recommendations (FR-16)
    ---
    tags:
      - Medical Report
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - patient_id
            - analysis_id
            - doctor_id
            - report_url
          properties:
            patient_id:
              type: integer
              example: 1
            analysis_id:
              type: integer
              example: 1
            doctor_id:
              type: integer
              example: 2
            report_url:
              type: string
              example: "https://example.com/report.pdf"
    responses:
      201:
        description: Report created successfully with automated recommendations
        schema:
          type: object
          properties:
            message:
              type: string
              example: Medical report created successfully
            data:
              type: object
              properties:
                report_id:
                  type: integer
                recommendations:
                  type: string
                  description: Auto-generated based on risk_level
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate input data with Schema
        schema = MedicalReportCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Validate dependencies (Patient, Doctor, Analysis exist) via SERVICES ✅
        patient = patient_service.get_patient_by_id(data['patient_id'])
        if not patient:
            return not_found_response('Patient not found')
        
        doctor = doctor_service.get_doctor_by_id(data['doctor_id'])
        if not doctor:
            return not_found_response('Doctor not found')
        
        analysis = analysis_service.get_analysis_by_id(data['analysis_id'])
        if not analysis:
            return not_found_response('Analysis not found')
        
        # STEP 3: Call SERVICE (not Repository directly!) ✅
        report = report_service.generate_report(
            patient_id=data['patient_id'],
            analysis_id=data['analysis_id'],
            doctor_id=data['doctor_id'],
            report_url=data['report_url']
        )
        
        # STEP 4: Format and return response
        response_schema = MedicalReportResponseSchema()
        return success_response(response_schema.dump(report), 'Medical report created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """
    Get medical report by ID
    ---
    tags:
      - Medical Report
    parameters:
      - name: report_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Report found
      404:
        description: Report not found
    """
    try:
        # Call SERVICE instead of Repository ✅
        report = report_service.get_report_by_id(report_id)
        if not report:
            return not_found_response('Report not found')
        
        schema = MedicalReportResponseSchema()
        return success_response(schema.dump(report))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_report_by_analysis(analysis_id):
    """
    Get report for a specific analysis
    ---
    tags:
      - Medical Report
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Report found
      404:
        description: Report not found
    """
    try:
        # Call SERVICE ✅
        report = report_service.get_report_by_analysis(analysis_id)
        if not report:
            return not_found_response('Report not found for this analysis')
        
        schema = MedicalReportResponseSchema()
        return success_response(schema.dump(report))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_reports_by_patient(patient_id):
    """
    Get all reports for a patient
    ---
    tags:
      - Medical Report
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: List of reports
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Call SERVICE ✅
        if limit:
            reports = report_service.get_recent_reports_by_patient(patient_id, limit)
        else:
            reports = report_service.get_reports_by_patient(patient_id)
        
        return success_response({
            'patient_id': patient_id,
            'count': len(reports),
            'reports': [{
                'report_id': r.report_id,
                'analysis_id': r.analysis_id,
                'doctor_id': r.doctor_id,
                'report_url': r.report_url,
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in reports]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_reports_by_doctor(doctor_id):
    """
    Get all reports created by a doctor
    ---
    tags:
      - Medical Report
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of reports
    """
    try:
        # Call SERVICE ✅
        reports = report_service.get_reports_by_doctor(doctor_id)
        
        return success_response({
            'doctor_id': doctor_id,
            'count': len(reports),
            'reports': [{
                'report_id': r.report_id,
                'patient_id': r.patient_id,
                'analysis_id': r.analysis_id,
                'report_url': r.report_url,
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in reports]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('', methods=['GET'])
def get_all_reports():
    """
    Get all medical reports
    ---
    tags:
      - Medical Report
    parameters:
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
    responses:
      200:
        description: List of reports
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Call SERVICE ✅
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                reports = report_service.get_reports_by_date_range(start, end)
            except ValueError:
                return validation_error_response({'date': 'Invalid date format. Use YYYY-MM-DD'})
        else:
            reports = report_service.list_all_reports()
        
        return success_response({
            'count': len(reports),
            'reports': [{
                'report_id': r.report_id,
                'patient_id': r.patient_id,
                'analysis_id': r.analysis_id,
                'doctor_id': r.doctor_id,
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in reports]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/<int:report_id>/url', methods=['PUT'])
def update_report_url(report_id):
    """
    Update report URL (re-generate report)
    ---
    tags:
      - Medical Report
    parameters:
      - name: report_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: report_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - report_url
          properties:
            report_url:
              type: string
              example: "https://example.com/report.pdf"
    responses:
      200:
        description: Report URL updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Report URL updated successfully
            data:
              type: object
      400:
        description: Report URL is required
      404:
        description: Report not found
    """
    try:
        data = request.get_json()
        if not data.get('report_url'):
            return validation_error_response({'report_url': 'Report URL is required'})
        
        # Call SERVICE ✅
        report = report_service.update_report_url(report_id, data['report_url'])
        if not report:
            return not_found_response('Report not found')
        
        return success_response({
            'report_id': report.report_id,
            'report_url': report.report_url
        }, 'Report URL updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """
    Delete medical report
    ---
    tags:
      - Medical Report
    parameters:
      - name: report_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Report deleted successfully
      404:
        description: Report not found
    """
    try:
        # Call SERVICE ✅
        result = report_service.delete_report(report_id)
        if not result:
            return not_found_response('Report not found')
        
        return success_response(None, 'Report deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get medical report statistics
    ---
    tags:
      - Medical Report
    parameters:
      - name: patient_id
        in: query
        required: false
        schema:
          type: integer
      - name: doctor_id
        in: query
        required: false
        schema:
          type: integer
    responses:
      200:
        description: Report statistics
    """
    try:
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        
        # Call SERVICE ✅
        if patient_id:
            count = report_service.count_by_patient(patient_id)
            return success_response({
                'patient_id': patient_id,
                'total_reports': count
            })
        elif doctor_id:
            count = report_service.count_by_doctor(doctor_id)
            return success_response({
                'doctor_id': doctor_id,
                'total_reports': count
            })
        else:
            # Get overall statistics
            stats = report_service.get_report_statistics()
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@medical_report_bp.route('/<int:report_id>/export', methods=['GET'])
def export_report(report_id):
    """
    Export medical report as PDF or CSV
    ---
    tags:
      - Medical Report
    parameters:
      - name: report_id
        in: path
        required: true
        schema:
          type: integer
      - name: format
        in: query
        required: false
        schema:
          type: string
          enum: [pdf, csv]
          default: pdf
    responses:
      200:
        description: Report exported successfully
      404:
        description: Report not found
      400:
        description: Invalid format
    """
    try:
        # Get format (pdf or csv)
        export_format = request.args.get('format', 'pdf').lower()
        if export_format not in ['pdf', 'csv']:
            return error_response('Invalid format. Use "pdf" or "csv"', 400)
        
        # Get report
        report = report_service.get_report_by_id(report_id)
        if not report:
            return not_found_response('Report not found')
        
        # Get related data
        patient = patient_service.get_patient_by_id(report.patient_id)
        if not patient:
            return not_found_response('Patient not found')
        
        doctor = doctor_service.get_doctor_by_id(report.doctor_id)
        if not doctor:
            return not_found_response('Doctor not found')
        
        analysis = analysis_service.get_analysis_by_id(report.analysis_id)
        if not analysis:
            return not_found_response('Analysis not found')
        
        # Get AI result
        ai_results = result_service.get_results_by_analysis(report.analysis_id)
        ai_result = ai_results[0] if ai_results else None
        
        # Get image info
        image = image_service.get_image_by_id(analysis.image_id) if hasattr(analysis, 'image_id') and analysis.image_id else None
        
        # Prepare report data
        report_data = {
            'report_id': report.report_id,
            'patient_name': patient.patient_name,
            'patient_id': patient.patient_id,
            'patient_dob': patient.date_of_birth,
            'patient_gender': patient.gender,
            'doctor_name': doctor.doctor_name,
            'doctor_id': doctor.doctor_id,
            'doctor_specialization': doctor.specialization,
            'analysis_date': analysis.analysis_time if hasattr(analysis, 'analysis_time') else report.created_at,
            'image_type': image.image_type if image else 'N/A',
            'eye_side': image.eye_side if image else 'N/A',
            'disease_type': ai_result.disease_type if ai_result else 'N/A',
            'risk_level': ai_result.risk_level if ai_result else 'N/A',
            'confidence_score': float(ai_result.confidence_score) if ai_result else 0.0,
            'created_at': report.created_at
        }
        
        # Generate recommendations using RecommendationService (business logic)
        from services.recommendation_service import RecommendationService
        risk_level = report_data['risk_level'] if report_data['risk_level'] != 'N/A' else 'low'
        disease_type = report_data.get('disease_type') if report_data.get('disease_type') != 'N/A' else None
        
        report_data['recommendations'] = RecommendationService.generate_recommendations(
            risk_level=risk_level,
            disease_type=disease_type
        )
        
        # Generate warnings if needed
        if ai_result:
            warnings = RecommendationService.generate_warnings(
                risk_level=risk_level,
                confidence_score=float(ai_result.confidence_score)
            )
            if warnings:
                report_data['warnings'] = warnings
        
        # Generate export
        if export_format == 'pdf':
            pdf_buffer = export_service.generate_pdf_report(report_data)
            return Response(
                pdf_buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=medical_report_{report_id}.pdf'
                }
            )
        else:  # csv
            csv_buffer = export_service.generate_csv_report(report_data)
            return Response(
                csv_buffer.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=medical_report_{report_id}.csv'
                }
            )
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

