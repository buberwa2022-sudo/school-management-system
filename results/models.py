from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class GradingSystem(models.Model):
    """Configurable grading system (NECTA, Cambridge, IB, etc.)"""
    GRADING_CHOICES = [
        ('necta', 'NECTA (Tanzania)'),
        ('cambridge', 'Cambridge'),
        ('ib', 'International Baccalaureate'),
        ('igcse', 'IGCSE'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100)
    system_type = models.CharField(max_length=20, choices=GRADING_CHOICES)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Grading System'
        verbose_name_plural = 'Grading Systems'
    
    def __str__(self):
        return f"{self.name} ({self.system_type})"


class GradeScale(models.Model):
    """Grade scale configuration (e.g., A=75-100, B=65-74)"""
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.CASCADE, related_name='grade_scales')
    grade = models.CharField(max_length=2)  # A, B, C, D, F
    min_marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    remarks = models.CharField(max_length=50)  # Excellent, Good, Average, Fail
    
    class Meta:
        ordering = ['-min_marks']
        unique_together = ('grading_system', 'grade')
    
    def __str__(self):
        return f"{self.grade} ({self.min_marks}-{self.max_marks}): {self.remarks}"


class DivisionScale(models.Model):
    """Division scale configuration (Division I, II, III, IV, 0)"""
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.CASCADE, related_name='division_scales')
    division = models.CharField(max_length=20)  # Division I, II, III, IV, 0
    min_average = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_average = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        ordering = ['min_average']
        unique_together = ('grading_system', 'division')
    
    def __str__(self):
        return f"{self.division} ({self.min_average}-{self.max_average})"


class Subject(models.Model):
    """Subject configuration"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Examination(models.Model):
    """Examination/Assessment configuration"""
    EXAM_TYPES = [
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('mock', 'Mock Exam'),
        ('diagnostic', 'Diagnostic Exam'),
    ]
    
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    academic_year = models.CharField(max_length=9)  # 2023/2024
    term = models.IntegerField(choices=[(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')])
    exam_date = models.DateField()
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.PROTECT)
    is_published = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exam_date']
        unique_together = ('academic_year', 'term', 'exam_type')
    
    def __str__(self):
        return f"{self.name} - {self.academic_year} Term {self.term}"


class StudentResult(models.Model):
    """Main student result record"""
    STATUS_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('incomplete', 'Incomplete'),
        ('absent', 'Absent'),
        ('withheld', 'Withheld'),
        ('transferred', 'Transferred'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='results')
    
    # Summary calculations
    total_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])
    average_marks = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_points = models.FloatField(default=0)
    overall_grade = models.CharField(max_length=2, blank=True)
    overall_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    division = models.CharField(max_length=20, blank=True)  # Division I, II, III, IV, 0
    gpa = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    
    # Ranking
    overall_position = models.IntegerField(null=True, blank=True)
    stream_position = models.IntegerField(null=True, blank=True)
    gender_position = models.IntegerField(null=True, blank=True)
    
    # Subject performance
    subjects_passed = models.IntegerField(default=0)
    subjects_failed = models.IntegerField(default=0)
    highest_score = models.FloatField(default=0)
    lowest_score = models.FloatField(default=0)
    best_subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='best_results')
    weakest_subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='weakest_results')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_results')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_results')
    
    class Meta:
        ordering = ['-examination__exam_date', 'student']
        unique_together = ('student', 'examination')
        indexes = [
            models.Index(fields=['student', 'examination']),
            models.Index(fields=['is_published', 'examination']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.examination}"


class SubjectResult(models.Model):
    """Individual subject result for a student"""
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE, related_name='subject_results')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    
    # Assessment components
    ca_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Continuous Assessment
    test_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Test/Quiz
    midterm_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Midterm
    final_exam_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Final Exam
    
    total_marks = models.FloatField(default=0, validators=[MinValueValidator(0)])
    average = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = models.CharField(max_length=2, blank=True)
    points = models.FloatField(default=0, validators=[MinValueValidator(0)])
    remarks = models.CharField(max_length=100, blank=True)
    
    # Performance tracking
    is_passed = models.BooleanField(default=False)
    previous_average = models.FloatField(null=True, blank=True)  # For comparison
    improvement = models.FloatField(default=0)  # Current - Previous
    
    class Meta:
        unique_together = ('student_result', 'subject')
        ordering = ['-average']
    
    def __str__(self):
        return f"{self.student_result.student} - {self.subject}: {self.grade}"


class Attendance(models.Model):
    """Student attendance record"""
    student_result = models.OneToOneField(StudentResult, on_delete=models.CASCADE, related_name='attendance')
    days_present = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_absent = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_sick = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_permission = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    attendance_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return f"Attendance - {self.student_result.student}"


class BehaviourAssessment(models.Model):
    """Behaviour and conduct assessment"""
    GRADE_CHOICES = [
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Average'),
        ('D', 'Needs Improvement'),
    ]
    
    student_result = models.OneToOneField(StudentResult, on_delete=models.CASCADE, related_name='behaviour')
    discipline = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    leadership = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    punctuality = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    responsibility = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    cooperation = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    respect = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    cleanliness = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    creativity = models.CharField(max_length=1, choices=GRADE_CHOICES, default='C')
    
    def __str__(self):
        return f"Behaviour - {self.student_result.student}"


class CoCurricularActivity(models.Model):
    """Co-curricular activity participation"""
    ACTIVITY_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('athletics', 'Athletics'),
        ('debate', 'Debate Club'),
        ('choir', 'Choir'),
        ('scout', 'Scout'),
        ('ict', 'ICT Club'),
        ('environment', 'Environmental Club'),
        ('entrepreneurship', 'Entrepreneurship Club'),
    ]
    
    LEVEL_CHOICES = [
        ('member', 'Member'),
        ('leader', 'Leader'),
        ('participant', 'Participant'),
        ('non', 'Non-Participant'),
    ]
    
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE, related_name='activities')
    activity = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    participation_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    
    class Meta:
        unique_together = ('student_result', 'activity')
    
    def __str__(self):
        return f"{self.student_result.student} - {self.activity}: {self.participation_level}"


class ResultComment(models.Model):
    """Comments from teachers on student results"""
    COMMENT_TYPES = [
        ('class_teacher', 'Class Teacher'),
        ('academic_teacher', 'Academic Master/Mistress'),
        ('headmaster', 'Headmaster/Headmistress'),
    ]
    
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE, related_name='comments')
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES)
    comment = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        unique_together = ('student_result', 'comment_type')
    
    def __str__(self):
        return f"{self.comment_type} - {self.student_result.student}"


class FeeInfo(models.Model):
    """Student fee information"""
    FEE_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('unpaid', 'Not Paid'),
    ]
    
    student_result = models.OneToOneField(StudentResult, on_delete=models.CASCADE, related_name='fee_info')
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=FEE_STATUS_CHOICES)
    
    def __str__(self):
        return f"Fee Info - {self.student_result.student}"


class NextTermInfo(models.Model):
    """Next term information"""
    examination = models.OneToOneField(Examination, on_delete=models.CASCADE, related_name='next_term_info')
    opening_date = models.DateField()
    closing_date = models.DateField()
    reporting_time = models.TimeField()
    required_materials = models.TextField()  # Rich text
    announcements = models.TextField(blank=True)  # Rich text
    
    def __str__(self):
        return f"Next Term Info - {self.examination}"


class ResultAuditLog(models.Model):
    """Audit trail for all result modifications"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('approve', 'Approved'),
        ('publish', 'Published'),
        ('lock', 'Locked'),
        ('unlock', 'Unlocked'),
        ('delete', 'Deleted'),
    ]
    
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changes = models.JSONField(default=dict, blank=True)  # What changed
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['student_result', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.student_result.student} - {self.timestamp}"


class ResultTemplate(models.Model):
    """Customizable result report template"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    grading_system = models.ForeignKey(GradingSystem, on_delete=models.CASCADE, related_name='templates')
    html_template = models.TextField()  # Store custom HTML template
    css_styles = models.TextField(blank=True)  # Custom CSS
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
