from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.conf import settings
import io
import os
from datetime import datetime


class CertificateGenerator:
    """Generate PDF certificates using ReportLab"""
    
    def __init__(self, certificate):
        self.certificate = certificate
        self.student = certificate.student
        self.course = certificate.course
        self.template = self.get_template()
        
    def get_template(self):
        """Get certificate template or use default"""
        from .models import CertificateTemplate
        
        try:
            return CertificateTemplate.objects.get(is_default=True, is_active=True)
        except CertificateTemplate.DoesNotExist:
            # Create a default template if none exists
            return CertificateTemplate.objects.create(
                name="Default Template",
                description="Default certificate template",
                is_default=True,
                is_active=True
            )
    
    def generate_pdf(self):
        """Generate the certificate PDF"""
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the certificate content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CertificateTitle',
            parent=styles['Heading1'],
            fontSize=self.template.title_font_size,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor(self.template.text_color)
        )
        
        body_style = ParagraphStyle(
            'CertificateBody',
            parent=styles['Normal'],
            fontSize=self.template.body_font_size,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=HexColor(self.template.text_color)
        )
        
        # Add logo if available
        if self.template.logo:
            try:
                logo_path = self.template.logo.path
                if os.path.exists(logo_path):
                    logo = Image(logo_path, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 20))
            except:
                pass
        
        # Certificate title
        story.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        story.append(Spacer(1, 30))
        
        # Student name
        student_name = self.student.get_full_name() or self.student.username
        story.append(Paragraph(f"This is to certify that", body_style))
        story.append(Spacer(1, 10))
        
        name_style = ParagraphStyle(
            'StudentName',
            parent=body_style,
            fontSize=self.template.body_font_size + 4,
            spaceAfter=20,
            textColor=HexColor(self.template.text_color)
        )
        story.append(Paragraph(f"<b>{student_name}</b>", name_style))
        
        # Course completion text
        story.append(Paragraph(
            f"has successfully completed the course",
            body_style
        ))
        story.append(Spacer(1, 10))
        
        course_style = ParagraphStyle(
            'CourseName',
            parent=body_style,
            fontSize=self.template.body_font_size + 2,
            spaceAfter=20,
            textColor=HexColor(self.template.text_color)
        )
        story.append(Paragraph(f"<b>{self.course.title}</b>", course_style))
        
        # Completion details
        story.append(Paragraph(
            f"Completed on: {self.certificate.completion_date.strftime('%B %d, %Y')}",
            body_style
        ))
        story.append(Paragraph(
            f"Final Score: {self.certificate.final_score}%",
            body_style
        ))
        story.append(Spacer(1, 30))
        
        # Instructor signature
        instructor_name = self.course.instructor.get_full_name() or self.course.instructor.username
        story.append(Paragraph(f"Instructor: {instructor_name}", body_style))
        story.append(Spacer(1, 20))
        
        # Certificate details
        story.append(Paragraph(
            f"Certificate ID: {self.certificate.certificate_id}",
            body_style
        ))
        story.append(Paragraph(
            f"Verification Code: {self.certificate.verification_code}",
            body_style
        ))
        story.append(Paragraph(
            f"Issued on: {self.certificate.issued_date.strftime('%B %d, %Y')}",
            body_style
        ))
        
        # Build the PDF
        doc.build(story, onFirstPage=self.add_border, onLaterPages=self.add_border)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def add_border(self, canvas, doc):
        """Add border and background to the certificate"""
        canvas.saveState()
        
        # Set background color
        if self.template.background_color != '#FFFFFF':
            canvas.setFillColor(HexColor(self.template.background_color))
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        
        # Add border
        canvas.setStrokeColor(HexColor(self.template.border_color))
        canvas.setLineWidth(3)
        canvas.rect(36, 36, A4[0] - 72, A4[1] - 72, fill=0, stroke=1)
        
        # Add inner border
        canvas.setLineWidth(1)
        canvas.rect(50, 50, A4[0] - 100, A4[1] - 100, fill=0, stroke=1)
        
        canvas.restoreState()
    
    def save_certificate(self):
        """Generate and save the certificate PDF"""
        pdf_content = self.generate_pdf()
        
        # Create filename
        filename = f"certificate_{self.certificate.certificate_id}.pdf"
        
        # Save the PDF file
        self.certificate.pdf_file.save(
            filename,
            ContentFile(pdf_content),
            save=True
        )
        
        return self.certificate.pdf_file.url


def generate_certificate_for_enrollment(enrollment):
    """Generate certificate when student completes a course"""
    from .models import Certificate
    
    # Check if certificate already exists
    if hasattr(enrollment, 'certificate'):
        return enrollment.certificate
    
    # Create certificate
    certificate = Certificate.objects.create(
        student=enrollment.student,
        course=enrollment.course,
        enrollment=enrollment,
        completion_date=enrollment.completed_at,
        final_score=enrollment.progress_percentage
    )
    
    # Generate PDF
    generator = CertificateGenerator(certificate)
    generator.save_certificate()
    
    return certificate


def verify_certificate(certificate_id=None, verification_code=None):
    """Verify a certificate by ID or verification code"""
    from .models import Certificate
    from django.core.exceptions import ValidationError
    import uuid

    try:
        if certificate_id:
            # Validate UUID format first
            try:
                uuid.UUID(str(certificate_id))
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'message': 'Invalid certificate ID format'
                }

            certificate = Certificate.objects.get(
                certificate_id=certificate_id,
                is_verified=True
            )
        elif verification_code:
            certificate = Certificate.objects.get(
                verification_code=verification_code,
                is_verified=True
            )
        else:
            return {
                'valid': False,
                'message': 'Certificate ID or verification code required'
            }

        return {
            'valid': True,
            'certificate': certificate,
            'student_name': certificate.student.get_full_name() or certificate.student.username,
            'course_title': certificate.course.title,
            'completion_date': certificate.completion_date,
            'final_score': certificate.final_score,
            'issued_date': certificate.issued_date
        }

    except (Certificate.DoesNotExist, ValidationError):
        return {
            'valid': False,
            'message': 'Certificate not found or invalid'
        }
