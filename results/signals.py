# results/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import (
    StudentResult, SubjectResult, Attendance, BehaviourAssessment
)
from .utils import (
    calculate_grade, calculate_division, calculate_gpa,
    calculate_ranking, calculate_performance_summary
)


@receiver(post_save, sender=SubjectResult)
def update_student_result_on_subject_save(sender, instance, created, **kwargs):
    """
    Update StudentResult totals when SubjectResult is saved
    """
    student_result = instance.student_result
    
    # Recalculate subject results for this student
    subject_results = student_result.subject_results.all()
    
    if not subject_results.exists():
        return
    
    # Calculate totals
    total_marks = sum(sr.average for sr in subject_results)
    avg_marks = total_marks / subject_results.count() if subject_results.count() > 0 else 0
    
    # Update overall fields
    student_result.total_marks = total_marks
    student_result.average_marks = avg_marks
    student_result.overall_percentage = avg_marks
    student_result.overall_grade = calculate_grade(avg_marks, student_result.examination.grading_system)
    student_result.division = calculate_division(avg_marks, student_result.examination.grading_system)
    student_result.gpa = calculate_gpa(subject_results, student_result.examination.grading_system)
    
    # Update performance summary
    perf_summary = calculate_performance_summary(student_result)
    student_result.subjects_passed = perf_summary['subjects_passed']
    student_result.subjects_failed = perf_summary['subjects_failed']
    student_result.highest_score = perf_summary['highest_score']
    student_result.lowest_score = perf_summary['lowest_score']
    student_result.best_subject = perf_summary['best_subject']
    student_result.weakest_subject = perf_summary['weakest_subject']
    
    # Update status
    if student_result.subjects_failed == 0:
        student_result.status = 'pass'
    else:
        student_result.status = 'fail'
    
    # Calculate rankings
    rankings = calculate_ranking(student_result)
    student_result.overall_position = rankings['overall_position']
    student_result.stream_position = rankings['stream_position']
    student_result.gender_position = rankings['gender_position']
    
    student_result.save()
    
    # Clear cache
    cache.delete(f'result_{student_result.id}')


@receiver(post_save, sender=StudentResult)
def recalculate_rankings_on_result_save(sender, instance, created, **kwargs):
    """
    Recalculate all rankings when a StudentResult is saved
    """
    # Get all results for the same examination
    results = StudentResult.objects.filter(
        examination=instance.examination
    ).order_by('-average_marks')
    
    # Recalculate overall positions
    for position, result in enumerate(results, 1):
        result.overall_position = position
        result.save(update_fields=['overall_position'])
    
    # Clear cache
    cache.delete(f'exam_results_{instance.examination.id}')


@receiver(post_save, sender=Attendance)
def calculate_attendance_percentage(sender, instance, created, **kwargs):
    """
    Calculate attendance percentage
    """
    total_days = (
        instance.days_present +
        instance.days_absent +
        instance.days_sick +
        instance.days_permission
    )
    
    if total_days > 0:
        instance.attendance_percentage = (instance.days_present / total_days) * 100
        instance.save(update_fields=['attendance_percentage'])
