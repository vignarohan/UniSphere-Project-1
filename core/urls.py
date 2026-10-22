from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry, name='entry'),
    path('login/<str:role>/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject-detail'),
    path('subjects/<int:pk>/materials/new/', views.resource_new, name='resource-new'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/new/', views.assignment_new, name='assignment-new'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment-detail'),
    path('assignments/<int:pk>/publish/', views.assignment_publish, name='assignment-publish'),
    path('submissions/<int:pk>/feedback/', views.feedback_edit, name='feedback-edit'),
    path('submissions/<int:pk>/download/', views.submission_download, name='submission-download'),
    path('resources/<int:pk>/download/', views.resource_download, name='resource-download'),
    path('attendance/', views.attendance, name='attendance'),
    path('timetable/', views.timetable, name='timetable'),
    path('results/', views.results, name='results'),
    path('fees/', views.fees, name='fees'),
    path('helper/records/', views.helper_records, name='helper-records'),
    path('manifest.webmanifest', views.manifest, name='manifest'),
    path('service-worker.js', views.service_worker, name='service-worker'),
    path('offline/', views.offline, name='offline'),
]
