from django.core.cache import cache
from decimal import Decimal
import qrcode
from io import BytesIO
import base64
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import json

from .models import GradeScale, DivisionScale, SubjectResult


def calculate_grade(marks, grading_system):
    """
    Calculate grade based on marks and grading system
    """
    marks = float(marks)
    grade_scales = GradeScale.objects.filter(grading_system=grading_system).order_by('-min_marks')
    
    for scale in grade_scales:
        if scale.min_marks <= marks <= scale.max_marks:
            return scale.grade
    
    return 'F'  # Default to Fail


def calculate_division(average_marks, grading_system):
    """
    Calculate division based on average marks
    Example: Division I (75-100), Division II (65-74), etc.
    """
    average_marks = float(average_marks)
    division_scales = DivisionScale.objects.filter(grading_system=grading_system).order_by('-min_average')
    
    for scale in division_scales:
        if scale.min_average <= average_marks <= scale.max_average:
            return scale.division
    
    return 'Division 0'  # Default


def calculate_gpa(subject_results, grading_system):
    """
    Calculate GPA (0-4.0 scale) from subject results
    """
    if not subject_results.exists():
        return 0.0
    
    total_points = 0
    total_subjects = subject_results.count()
    
    for sr in subject_results:
        # Convert marks to GPA (0-4.0)
        if sr.average >= 90:
            gpa_point = 4.0
        elif sr.average >= 80:
            gpa_point = 3.5
        elif sr.average >= 70:
            gpa_point = 3.0
        elif sr.average >= 60:
            gpa_point = 2.5
        elif sr.average >= 50:
            gpa_point = 2.0
        elif sr.average >= 40:
            gpa_point = 1.5
        elif sr.average >= 30:
            gpa_point = 1.0
        else:
            gpa_point = 0.0
        
        total_points += gpa_point
    
    return round(total_points / total_subjects, 2) if total_subjects > 0 else 0.0


def calculate_ranking(result):
    """
    Calculate student rankings:
    - Overall position in school
    - Stream position
    - Gender position
    """
    from .models import StudentResult
    
    # Overall position
    overall_position = StudentResult.objects.filter(
        examination=result.examination,
        average_marks__gt=result.average_marks
    ).count() + 1
    
    # Stream position
    stream_position = StudentResult.objects.filter(
        examination=result.examination,
        student__current_stream=result.student.current_stream,
        average_marks__gt=result.average_marks
    ).count() + 1
    
    # Gender position
    gender_position = StudentResult.objects.filter(
        examination=result.examination,
        student__user__gender=result.student.user.gender,
        average_marks__gt=result.average_marks
    ).count() + 1
    
    return {
        'overall_position': overall_position,
        'stream_position': stream_position,
        'gender_position': gender_position,
    }


def calculate_performance_summary(student_result):
    """
    Calculate subject performance metrics
    """
    subject_results = student_result.subject_results.all()
    
    if not subject_results.exists():
        return {
            'subjects_passed': 0,
            'subjects_failed': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'best_subject': None,
            'weakest_subject': None,
        }
    
    # Count passes and failures
    passed = subject_results.filter(is_passed=True).count()
    failed = subject_results.filter(is_passed=False).count()
    
    # Get highest and lowest scores
    highest_sr = subject_results.order_by('-average').first()
    lowest_sr = subject_results.order_by('average').first()
    
    return {
        'subjects_passed': passed,
        'subjects_failed': failed,
        'highest_score': highest_sr.average if highest_sr else 0,
        'lowest_score': lowest_sr.average if lowest_sr else 0,
        'best_subject': highest_sr.subject if highest_sr else None,
        'weakest_subject': lowest_sr.subject if lowest_sr else None,
    }


def calculate_subject_results(student_result, subject):
    """
    Calculate totals, averages, and grades for a subject
    """
    sr = SubjectResult.objects.get(student_result=student_result, subject=subject)
    
    # Calculate total (assuming weights: CA=10%, Test=15%, Midterm=20%, Final=55%)
    total = (
        sr.ca_marks * 0.10 +
        sr.test_marks * 0.15 +
        sr.midterm_marks * 0.20 +
        sr.final_exam_marks * 0.55
    )
    
    sr.total_marks = total
    sr.average = total
    sr.grade = calculate_grade(total, student_result.examination.grading_system)
    sr.is_passed = total >= 40  # Assuming 40 is pass mark
    sr.save()
    
    return sr


def generate_qrcode(student_result):
    """
    Generate QR code for result verification
    QR code contains: Student ID, Result ID, Verification URL
    """
    verification_url = f"https://yourschool.com/verify/{student_result.id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def generate_pdf_report(student_result):
    """
    Generate comprehensive PDF report of student result
    """
    from django.conf import settings
    from django.templatetags.static import static
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a3a52'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#1a3a52'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # School Header
    school = student_result.student.current_class.stream.school
    
    header_data = [
        [Paragraph(f"<b>{school.name}</b>", title_style)],
        [Paragraph(school.motto or "", styles['Normal'])],
        [Paragraph(f"{school.address}, {school.district}", styles['Normal'])],
        [Paragraph(f"Tel: {school.phone} | Email: {school.email}", styles['Normal'])],
    ]
    
    header_table = Table(header_data, colWidths=[7.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Exam Info
    exam_info = f"""<b>Academic Year:</b> {student_result.examination.academic_year} | 
    <b>Term:</b> {student_result.examination.get_term_display()} | 
    <b>Exam:</b> {student_result.examination.name}"""
    story.append(Paragraph(exam_info, styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Student Profile
    story.append(Paragraph("STUDENT INFORMATION", heading_style))
    student_data = [
        ["Name:", str(student_result.student.user), "Admission No:", student_result.student.admission_number],
        ["Gender:", student_result.student.user.gender or "N/A", "DOB:", student_result.student.date_of_birth.strftime('%d-%m-%Y') if student_result.student.date_of_birth else "N/A"],
        ["Class:", str(student_result.student.current_class), "Stream:", student_result.student.current_stream or "N/A"],
    ]
    
    student_table = Table(student_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Subject Results
    story.append(Paragraph("SUBJECT RESULTS", heading_style))
    subject_data = [['Subject', 'C.A', 'Test', 'Midterm', 'Final', 'Total', 'Avg', 'Grade', 'Remarks']]
    
    for sr in student_result.subject_results.all().order_by('-average'):
        subject_data.append([
            sr.subject.name,
            f"{sr.ca_marks:.0f}",
            f"{sr.test_marks:.0f}",
            f"{sr.midterm_marks:.0f}",
            f"{sr.final_exam_marks:.0f}",
            f"{sr.total_marks:.1f}",
            f"{sr.average:.1f}",
            sr.grade,
            sr.remarks or "-",
        ])
    
    subject_table = Table(subject_data, colWidths=[1.8*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.65*inch, 0.65*inch, 0.55*inch, 0.5*inch, 0.7*inch])
    subject_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a52')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Academic Summary
    summary_data = [
        [f"Total Subjects: {student_result.subject_results.count()}", f"Passed: {student_result.subjects_passed}", f"Failed: {student_result.subjects_failed}"],
        [f"Overall Average: {student_result.average_marks:.2f}%", f"Overall Grade: {student_result.overall_grade}", f"Division: {student_result.division}"],
        [f"Overall Position: {student_result.overall_position}", f"Stream Position: {student_result.stream_position}", f"GPA: {student_result.gpa:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a3a52')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Comments
    if student_result.comments.exists():
        story.append(Paragraph("TEACHER COMMENTS", heading_style))
        for comment in student_result.comments.all():
            story.append(Paragraph(f"<b>{comment.get_comment_type_display()}:</b> {comment.comment}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer


def send_result_email(student_result, recipient_email):
    """
    Send result via email
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    subject = f"Academic Results - {student_result.examination.name}"
    context = {'result': student_result}
    
    html_message = render_to_string('results/email_result.html', context)
    
    send_mail(
        subject,
        'Please view your academic results attached.',
        'noreply@school.com',
        [recipient_email],
        html_message=html_message,
        fail_silently=False,
    )


def bulk_approve_results(examination_id, user):
    """
    Bulk approve all results for an examination
    """
    from .models import StudentResult, ResultAuditLog
    
    results = StudentResult.objects.filter(examination_id=examination_id, is_approved=False)
    
    for result in results:
        result.is_approved = True
        result.approved_by = user
        result.save()
        
        ResultAuditLog.objects.create(
            student_result=result,
            action='approve',
            user=user,
        )
    
    return results.count()
