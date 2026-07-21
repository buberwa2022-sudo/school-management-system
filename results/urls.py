from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Student Result Views
    path('student/<uuid:pk>/', views.StudentResultDetailView.as_view(), name='student_detail'),
    path('results/', views.StudentResultListView.as_view(), name='result_list'),
    
    # Examination Views
    path('examination/<int:pk>/dashboard/', views.ExaminationResultsView.as_view(), name='examination_dashboard'),
    path('examination/<int:pk>/analytics/', views.ResultAnalyticsAPIView.as_view(), name='examination_analytics'),
    
    # Export Views
    path('student/<uuid:pk>/pdf/', views.ResultPDFExportView.as_view(), name='student_pdf'),
    path('examination/<int:pk>/excel/', views.ResultExcelExportView.as_view(), name='examination_excel'),
    
    # Actions
    path('approve/<uuid:pk>/', views.approve_result, name='approve_result'),
    path('publish/<uuid:pk>/', views.publish_result, name='publish_result'),
    path('lock/<int:pk>/', views.lock_result, name='lock_result'),
]
