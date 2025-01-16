from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_teacher/<int:pk>/', views.approve_teacher, name='approve_teacher'),
    path('reject_teacher/<int:pk>/', views.reject_teacher, name='reject_teacher'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('delete_file/<str:file_type>/<int:pk>/', views.delete_file, name='delete_file'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-teacher/<str:username>/', views.delete_teacher, name='delete_teacher'),
    path('delete-student/<str:username>/', views.delete_student, name='delete_student'),
    path('clear_activity_log/', views.clear_activity_log, name='clear_activity_log'),
    path('clear_deleted_log/', views.clear_deleted_log, name='clear_deleted_log'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
