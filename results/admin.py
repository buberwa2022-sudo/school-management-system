from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import (
    GradingSystem, GradeScale, DivisionScale, Subject, Examination,
    StudentResult, SubjectResult, Attendance, BehaviourAssessment,
    CoCurricularActivity, ResultComment, FeeInfo, NextTermInfo,
    ResultAuditLog, ResultTemplate
)
from .forms import (
    GradingSystemForm, GradeScaleForm, DivisionScaleForm,
    SubjectResultForm, AttendanceForm, BehaviourAssessmentForm
)


@admin.register(GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'system_type', 'is_default', 'created_at']
    list_filter = ['system_type', 'is_default']
    search_fields = ['name']
    form = GradingSystemForm


class GradeScaleInline(admin.TabularInline):
    model = GradeScale
    form = GradeScaleForm
    extra = 1
    ordering = ['-min_marks']


class DivisionScaleInline(admin.TabularInline):
    model = DivisionScale
    form = DivisionScaleForm
    extra = 1
    ordering = ['min_average']


@admin.register(GradingSystem)
class GradingSystemDetailAdmin(admin.ModelAdmin):
    list_display = ['name', 'system_type', 'is_default']
    inlines = [GradeScaleInline, DivisionScaleInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'term', 'exam_date', 'is_published', 'is_locked']
    list_filter = ['exam_type', 'academic_year', 'term', 'is_published', 'is_locked']
    search_fields = ['name', 'academic_year']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'exam_type', 'academic_year', 'term', 'exam_date')
        }),
        ('Configuration', {
            'fields': ('grading_system',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_locked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SubjectResultInline(admin.TabularInline):
    model = SubjectResult
    form = SubjectResultForm
    extra = 0
    readonly_fields = ['total_marks', 'average', 'grade', 'is_passed']
    fields = ['subject', 'ca_marks', 'test_marks', 'midterm_marks', 'final_exam_marks', 'total_marks', 'average', 'grade', 'remarks']


class AttendanceInline(admin.StackedInline):
    model = Attendance
    form = AttendanceForm
    extra = 0
    readonly_fields = ['attendance_percentage']


class BehaviourAssessmentInline(admin.StackedInline):
    model = BehaviourAssessment
    form = BehaviourAssessmentForm
    extra = 0


class ResultCommentInline(admin.TabularInline):
    model = ResultComment
    extra = 1
    fields = ['comment_type', 'comment', 'commented_by']
    readonly_fields = ['commented_by', 'created_at']


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = [
        'student_link', 'examination', 'average_marks_colored',
        'overall_grade', 'division', 'overall_position', 'status_colored',
        'is_approved', 'is_published'
    ]
    list_filter = [
        'examination', 'status', 'is_approved', 'is_published', 'division',
        'overall_grade', 'created_at'
    ]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    readonly_fields = [
        'total_marks', 'average_marks', 'total_points', 'overall_grade',
        'overall_percentage', 'division', 'gpa', 'subjects_passed',
        'subjects_failed', 'highest_score', 'lowest_score',
        'best_subject', 'weakest_subject', 'overall_position',
        'stream_position', 'gender_position', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Student & Examination', {
            'fields': ('student', 'examination')
        }),
        ('Academic Performance', {
            'fields': (
                'total_marks', 'average_marks', 'overall_percentage',
                'overall_grade', 'division', 'gpa', 'total_points'
            )
        }),
        ('Subject Summary', {
            'fields': (
                'subjects_passed', 'subjects_failed',
                'highest_score', 'lowest_score',
                'best_subject', 'weakest_subject'
            )
        }),
        ('Rankings', {
            'fields': ('overall_position', 'stream_position', 'gender_position')
        }),
        ('Status', {
            'fields': ('status', 'is_approved', 'is_published', 'approved_by')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        SubjectResultInline,
        AttendanceInline,
        BehaviourAssessmentInline,
        ResultCommentInline,
    ]
    
    actions = ['approve_results', 'publish_results', 'export_results']
    
    def student_link(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
    student_link.short_description = 'Student'
    
    def average_marks_colored(self, obj):
        if obj.average_marks >= 75:
            color = 'green'
        elif obj.average_marks >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, obj.average_marks
        )
    average_marks_colored.short_description = 'Average'
    
    def status_colored(self, obj):
        colors = {
            'pass': 'green',
            'fail': 'red',
            'incomplete': 'orange',
            'absent': 'gray',
            'withheld': 'purple',
            'transferred': 'blue',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def approve_results(self, request, queryset):
        count = 0
        for result in queryset:
            if not result.is_approved:
                result.is_approved = True
                result.approved_by = request.user
                result.save()
                count += 1
        self.message_user(request, f'{count} results approved.')
    approve_results.short_description = 'Approve selected results'
    
    def publish_results(self, request, queryset):
        count = 0
        for result in queryset.filter(is_approved=True):
            if not result.is_published:
                result.is_published = True
                result.save()
                count += 1
        self.message_user(request, f'{count} results published.')
    publish_results.short_description = 'Publish selected results'
    
    def export_results(self, request, queryset):
        self.message_user(request, 'Export functionality available in views.')
    export_results.short_description = 'Export to Excel'


@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'subject', 'average', 'grade', 'is_passed']
    list_filter = ['is_passed', 'grade', 'subject']
    search_fields = ['student_result__student__user__first_name', 'subject__name']
    form = SubjectResultForm
    readonly_fields = ['total_marks', 'average', 'grade', 'points', 'is_passed']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student_result', 'days_present', 'days_absent',
        'days_sick', 'attendance_percentage_colored'
    ]
    list_filter = ['days_present', 'days_absent']
    readonly_fields = ['attendance_percentage']
    form = AttendanceForm
    
    def attendance_percentage_colored(self, obj):
        if obj.attendance_percentage >= 90:
            color = 'green'
        elif obj.attendance_percentage >= 75:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.attendance_percentage
        )
    attendance_percentage_colored.short_description = 'Attendance %'


@admin.register(BehaviourAssessment)
class BehaviourAssessmentAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'discipline', 'leadership', 'punctuality', 'responsibility']
    list_filter = ['discipline', 'leadership', 'punctuality']
    form = BehaviourAssessmentForm


@admin.register(CoCurricularActivity)
class CoCurricularActivityAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'activity', 'participation_level']
    list_filter = ['activity', 'participation_level']
    search_fields = ['student_result__student__user__first_name']


@admin.register(ResultComment)
class ResultCommentAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'comment_type', 'commented_by', 'created_at']
    list_filter = ['comment_type', 'created_at']
    search_fields = ['student_result__student__user__first_name', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'commented_by']


@admin.register(FeeInfo)
class FeeInfoAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'total_fees', 'amount_paid', 'balance', 'status_colored']
    list_filter = ['status']
    readonly_fields = ['balance']
    
    def status_colored(self, obj):
        colors = {'paid': 'green', 'partial': 'orange', 'unpaid': 'red'}
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(NextTermInfo)
class NextTermInfoAdmin(admin.ModelAdmin):
    list_display = ['examination', 'opening_date', 'closing_date']
    list_filter = ['opening_date', 'closing_date']


@admin.register(ResultAuditLog)
class ResultAuditLogAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['student_result__student__user__first_name', 'user__username']
    readonly_fields = ['student_result', 'action', 'user', 'changes', 'timestamp', 'ip_address']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ResultTemplate)
class ResultTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'grading_system', 'is_default']
    list_filter = ['grading_system', 'is_default']
    search_fields = ['name', 'description']
