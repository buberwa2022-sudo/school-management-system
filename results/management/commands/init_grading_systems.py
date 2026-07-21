# Management Commands for Results App

from django.core.management.base import BaseCommand
from results.models import GradingSystem, GradeScale, DivisionScale


class Command(BaseCommand):
    help = 'Initialize grading systems with Tanzania NECTA standards'

    def handle(self, *args, **options):
        # Create NECTA Grading System
        necta, created = GradingSystem.objects.get_or_create(
            name='NECTA (Tanzania)',
            defaults={
                'system_type': 'necta',
                'is_default': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created NECTA Grading System'))

            # Add Grade Scales
            grades = [
                {'grade': 'A', 'min': 75, 'max': 100, 'remarks': 'Excellent'},
                {'grade': 'B', 'min': 65, 'max': 74, 'remarks': 'Very Good'},
                {'grade': 'C', 'min': 45, 'max': 64, 'remarks': 'Good'},
                {'grade': 'D', 'min': 30, 'max': 44, 'remarks': 'Average'},
                {'grade': 'F', 'min': 0, 'max': 29, 'remarks': 'Fail'},
            ]

            for grade_data in grades:
                GradeScale.objects.get_or_create(
                    grading_system=necta,
                    grade=grade_data['grade'],
                    defaults={
                        'min_marks': grade_data['min'],
                        'max_marks': grade_data['max'],
                        'remarks': grade_data['remarks']
                    }
                )

            # Add Division Scales
            divisions = [
                {'division': 'Division I', 'min': 75, 'max': 100},
                {'division': 'Division II', 'min': 60, 'max': 74},
                {'division': 'Division III', 'min': 45, 'max': 59},
                {'division': 'Division IV', 'min': 30, 'max': 44},
                {'division': 'Division 0', 'min': 0, 'max': 29},
            ]

            for div_data in divisions:
                DivisionScale.objects.get_or_create(
                    grading_system=necta,
                    division=div_data['division'],
                    defaults={
                        'min_average': div_data['min'],
                        'max_average': div_data['max']
                    }
                )

            self.stdout.write(self.style.SUCCESS('Successfully initialized NECTA grading system'))
        else:
            self.stdout.write(self.style.WARNING('NECTA Grading System already exists'))
