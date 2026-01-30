"""
Export Service - Generate PDF and CSV reports
"""

from typing import Dict, Any, Optional
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import csv
import io


class ExportService:
    """Service for exporting medical reports to PDF and CSV"""
    
    @staticmethod
    def generate_pdf_report(report_data: Dict[str, Any]) -> BytesIO:
        """
        Generate PDF report from report data
        
        Args:
            report_data: Dictionary containing:
                - patient_name, patient_id, patient_dob, patient_gender
                - doctor_name, doctor_id, doctor_specialization
                - analysis_date, image_type, eye_side
                - disease_type, risk_level, confidence_score
                - recommendations (optional)
                - created_at
        
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("AURA - Medical Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", heading_style))
        patient_info = [
            ['Patient Name:', report_data.get('patient_name', 'N/A')],
            ['Patient ID:', str(report_data.get('patient_id', 'N/A'))],
            ['Date of Birth:', str(report_data.get('patient_dob', 'N/A'))],
            ['Gender:', report_data.get('patient_gender', 'N/A')]
        ]
        patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Doctor Information
        story.append(Paragraph("Doctor Information", heading_style))
        doctor_info = [
            ['Doctor Name:', report_data.get('doctor_name', 'N/A')],
            ['Doctor ID:', str(report_data.get('doctor_id', 'N/A'))],
            ['Specialization:', report_data.get('doctor_specialization', 'N/A')]
        ]
        doctor_table = Table(doctor_info, colWidths=[2*inch, 4*inch])
        doctor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(doctor_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analysis Information
        story.append(Paragraph("Analysis Results", heading_style))
        analysis_info = [
            ['Analysis Date:', str(report_data.get('analysis_date', 'N/A'))],
            ['Image Type:', report_data.get('image_type', 'N/A')],
            ['Eye Side:', report_data.get('eye_side', 'N/A')],
            ['Disease Type:', report_data.get('disease_type', 'N/A')],
            ['Risk Level:', report_data.get('risk_level', 'N/A').upper()],
            ['Confidence Score:', f"{report_data.get('confidence_score', 0):.2f}%"]
        ]
        
        # Color code risk level
        risk_level = report_data.get('risk_level', '').lower()
        risk_color = colors.black
        if risk_level == 'high':
            risk_color = colors.red
        elif risk_level == 'medium':
            risk_color = colors.orange
        elif risk_level == 'low':
            risk_color = colors.green
        
        analysis_table = Table(analysis_info, colWidths=[2*inch, 4*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (1, 4), (1, 4), risk_color),  # Risk level color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 4), (1, 4), 'Helvetica-Bold'),  # Bold risk level
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(analysis_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        recommendations = report_data.get('recommendations')
        if recommendations:
            story.append(Paragraph("Recommendations", heading_style))
            story.append(Paragraph(recommendations, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_csv_report(report_data: Dict[str, Any]) -> BytesIO:
        """
        Generate CSV report from report data
        
        Args:
            report_data: Dictionary containing report information
        
        Returns:
            BytesIO buffer containing CSV
        """
        # Use StringIO for text mode, then convert to BytesIO
        string_buffer = io.StringIO()
        writer = csv.writer(string_buffer)
        
        # Write header
        writer.writerow(['Field', 'Value'])
        
        # Write data
        writer.writerow(['Report ID', report_data.get('report_id', 'N/A')])
        writer.writerow(['Patient Name', report_data.get('patient_name', 'N/A')])
        writer.writerow(['Patient ID', report_data.get('patient_id', 'N/A')])
        writer.writerow(['Date of Birth', str(report_data.get('patient_dob', 'N/A'))])
        writer.writerow(['Gender', report_data.get('patient_gender', 'N/A')])
        writer.writerow(['Doctor Name', report_data.get('doctor_name', 'N/A')])
        writer.writerow(['Doctor ID', report_data.get('doctor_id', 'N/A')])
        writer.writerow(['Specialization', report_data.get('doctor_specialization', 'N/A')])
        writer.writerow(['Analysis Date', str(report_data.get('analysis_date', 'N/A'))])
        writer.writerow(['Image Type', report_data.get('image_type', 'N/A')])
        writer.writerow(['Eye Side', report_data.get('eye_side', 'N/A')])
        writer.writerow(['Disease Type', report_data.get('disease_type', 'N/A')])
        writer.writerow(['Risk Level', report_data.get('risk_level', 'N/A')])
        writer.writerow(['Confidence Score', f"{report_data.get('confidence_score', 0):.2f}%"])
        
        recommendations = report_data.get('recommendations')
        if recommendations:
            writer.writerow(['Recommendations', recommendations])
        
        writer.writerow(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        # Convert StringIO to BytesIO
        string_buffer.seek(0)
        csv_content = string_buffer.getvalue()
        string_buffer.close()
        
        # Create BytesIO with encoded content
        buffer = BytesIO()
        buffer.write(csv_content.encode('utf-8'))
        buffer.seek(0)
        return buffer

