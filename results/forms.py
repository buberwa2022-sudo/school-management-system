from django import forms
from django.core.exceptions import ValidationError
from .models import (
    StudentResult, SubjectResult, Attendance, BehaviourAssessment,
    CoCurricularActivity, ResultComment, FeeInfo, Examination,
    GradingSystem, GradeScale, DivisionScale
)


class StudentResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            })
        }


class SubjectResultForm(forms.ModelForm):
    class Meta:
        model = SubjectResult
        fields = ['ca_marks', 'test_marks', 'midterm_marks', 'final_exam_marks', 'remarks']
        widgets = {
            'ca_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Continuous Assessment',
            }),
            'test_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Test/Quiz',
            }),
            'midterm_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Midterm',
            }),
            'final_exam_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Final Exam',
            }),
            'remarks': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Remarks',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total = (
            cleaned_data.get('ca_marks', 0) +
            cleaned_data.get('test_marks', 0) +
            cleaned_data.get('midterm_marks', 0) +
            cleaned_data.get('final_exam_marks', 0)
        )
        
        if total > 100:
            raise ValidationError('Total marks cannot exceed 100')
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['days_present', 'days_absent', 'days_sick', 'days_permission']
        widgets = {
            'days_present': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'days_absent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'days_sick': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'days_permission': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class BehaviourAssessmentForm(forms.ModelForm):
    class Meta:
        model = BehaviourAssessment
        fields = ['discipline', 'leadership', 'punctuality', 'responsibility',
                  'cooperation', 'respect', 'cleanliness', 'creativity']
        widgets = {
            'discipline': forms.Select(attrs={'class': 'form-control'}),
            'leadership': forms.Select(attrs={'class': 'form-control'}),
            'punctuality': forms.Select(attrs={'class': 'form-control'}),
            'responsibility': forms.Select(attrs={'class': 'form-control'}),
            'cooperation': forms.Select(attrs={'class': 'form-control'}),
            'respect': forms.Select(attrs={'class': 'form-control'}),
            'cleanliness': forms.Select(attrs={'class': 'form-control'}),
            'creativity': forms.Select(attrs={'class': 'form-control'}),
        }


class CoCurricularActivityForm(forms.ModelForm):
    class Meta:
        model = CoCurricularActivity
        fields = ['activity', 'participation_level']
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-control'}),
            'participation_level': forms.Select(attrs={'class': 'form-control'}),
        }


class ResultCommentForm(forms.ModelForm):
    class Meta:
        model = ResultComment
        fields = ['comment_type', 'comment']
        widgets = {
            'comment_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your comment here...',
            }),
        }


class FeeInfoForm(forms.ModelForm):
    class Meta:
        model = FeeInfo
        fields = ['total_fees', 'amount_paid', 'status']
        widgets = {
            'total_fees': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_fees = cleaned_data.get('total_fees')
        amount_paid = cleaned_data.get('amount_paid')
        
        if total_fees and amount_paid and amount_paid > total_fees:
            raise ValidationError('Amount paid cannot exceed total fees')
        
        return cleaned_data


class GradingSystemForm(forms.ModelForm):
    class Meta:
        model = GradingSystem
        fields = ['name', 'system_type', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'system_type': forms.Select(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = ['grade', 'min_marks', 'max_marks', 'remarks']
        widgets = {
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '2',
                'placeholder': 'A, B, C, D, F',
            }),
            'min_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
            }),
            'remarks': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Excellent, Good, Average, Fail',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_marks = cleaned_data.get('min_marks')
        max_marks = cleaned_data.get('max_marks')
        
        if min_marks and max_marks and min_marks > max_marks:
            raise ValidationError('Min marks cannot exceed max marks')
        
        return cleaned_data


class DivisionScaleForm(forms.ModelForm):
    class Meta:
        model = DivisionScale
        fields = ['division', 'min_average', 'max_average']
        widgets = {
            'division': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Division I, II, III, IV, 0',
            }),
            'min_average': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
            'max_average': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_avg = cleaned_data.get('min_average')
        max_avg = cleaned_data.get('max_average')
        
        if min_avg and max_avg and min_avg > max_avg:
            raise ValidationError('Min average cannot exceed max average')
        
        return cleaned_data


class BulkResultActionForm(forms.Form):
    """Form for bulk actions on results"""
    ACTION_CHOICES = [
        ('approve', 'Approve All'),
        ('publish', 'Publish All'),
        ('lock', 'Lock Examination'),
        ('export', 'Export to Excel'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    examination = forms.ModelChoiceField(
        queryset=Examination.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
