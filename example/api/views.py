from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from pymongo import MongoClient
import re
from .models import TeacherApprovalRequest, ActivityLog
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import PDFFile, VideoFile, AssignmentFile, Teacher, Student
from .forms import UploadFileForm
import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.academe

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to the custom admin dashboard
            elif user.groups.filter(name='teacher').exists():
                return redirect('teacher_dashboard')  # Redirect to the teacher dashboard
            else:
                return redirect('student_dashboard')  # Redirect to the student dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        id_number = request.POST['id_number']
        username = request.POST['username']
        password = request.POST['password']
        is_teacher = request.POST.get('is_teacher', False)

        # Validate username
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_]).{8,}$', username):
            messages.error(request, 'Username must be longer than 8 characters, contain a special character, and an alphanumeric combination.')
            return render(request, 'signup.html')

        # Validate password
        if not re.match(r'^(?=.*[A-Z])(?=.*\W).+$', password):
            messages.error(request, 'Password must contain at least one uppercase letter and one special character.')
            return render(request, 'signup.html')

        # Check if username is unique
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'signup.html')

        # Create Django user
        user = User.objects.create_user(username=username, password=password)
        
        # Store details in MongoDB
        user_details = {
            "name": name,
            "id_number": id_number,
            "username": username
        }

        if is_teacher:
            # Assign staff status and create approval request for admin
            user.is_staff = True
            user.save()
            db.teacher.insert_one(user_details)
            TeacherApprovalRequest.objects.create(user=user)
            messages.info(request, 'Your request to become a teacher is pending approval.')
        else:
            assign_student_role(user)
            db.student.insert_one(user_details)
            messages.success(request, 'You have successfully signed up as a student.')

        return render(request, 'signup.html')
    return render(request, 'signup.html')

def assign_student_role(user):
    # Assign the user a student role without staff status
    student_group, created = Group.objects.get_or_create(name='student')
    user.groups.add(student_group)
    user.is_staff = False
    user.save()

def approve_teacher(request, pk):
    approval_request = TeacherApprovalRequest.objects.get(pk=pk)
    user = approval_request.user
    teacher_group, created = Group.objects.get_or_create(name='teacher')
    user.groups.add(teacher_group)
    user.is_staff = True
    user.save()
    approval_request.is_approved = True
    approval_request.save()
    return redirect('admin_dashboard')

def reject_teacher(request, pk):
    approval_request = TeacherApprovalRequest.objects.get(pk=pk)
    user = approval_request.user
    assign_student_role(user)
    approval_request.delete()
    return redirect('admin_dashboard')

def student_dashboard(request):
    uploaded_pdfs = PDFFile.objects.all()
    uploaded_videos = VideoFile.objects.all()
    uploaded_assignments = AssignmentFile.objects.all()
    return render(request, 'student_dashboard.html', {
        'uploaded_pdfs': uploaded_pdfs,
        'uploaded_videos': uploaded_videos,
        'uploaded_assignments': uploaded_assignments,
    })

def teacher_dashboard(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_type = form.cleaned_data['file_type']
            year = form.cleaned_data['year']
            semester = form.cleaned_data['semester']
            title = form.cleaned_data['title']
            file = form.cleaned_data['file']
            description = form.cleaned_data['description']
            class_name = form.cleaned_data['class_name']

            # Format class_name
            class_name = ' '.join(class_name.upper().split())

            # Save the file to the appropriate model
            if file_type == 'pdf':
                pdf_file = PDFFile(teacher=request.user, year=year, semester=semester, title=title, file=file, description=description, class_name=class_name)
                pdf_file.save()
            elif file_type == 'video':
                video_file = VideoFile(teacher=request.user, year=year, semester=semester, title=title, file=file, description=description, class_name=class_name)
                video_file.save()
            elif file_type == 'assignment':
                assignment_file = AssignmentFile(teacher=request.user, year=year, semester=semester, title=title, file=file, description=description, class_name=class_name)
                assignment_file.save()

            # Log the activity
            ActivityLog.objects.create(
                teacher=request.user,
                action='Uploaded file',
                file_type=file_type,
                class_name=class_name,
                year=year,
                semester=semester,
                title=title,
                description=description
            )

            # Store details in MongoDB
            upload_details = {
                "teacher": request.user.username,
                "file_type": file_type,
                "year": year,
                "semester": semester,
                "title": title,
                "file_path": file.name,
                "description": description,
                "class_name": class_name,
                "uploaded_at": datetime.datetime.now().isoformat(),
            }
            db.uploads.insert_one(upload_details)

            return redirect('teacher_dashboard')
    else:
        form = UploadFileForm()

    uploaded_pdfs = PDFFile.objects.filter(teacher=request.user)
    uploaded_videos = VideoFile.objects.filter(teacher=request.user)
    uploaded_assignments = AssignmentFile.objects.filter(teacher=request.user)
    return render(request, 'teacher_dashboard.html', {
        'form': form,
        'uploaded_pdfs': uploaded_pdfs,
        'uploaded_videos': uploaded_videos,
        'uploaded_assignments': uploaded_assignments,
    })

def delete_file(request, file_type, pk):
    if file_type == 'pdf':
        file = get_object_or_404(PDFFile, pk=pk, teacher=request.user)
    elif file_type == 'video':
        file = get_object_or_404(VideoFile, pk=pk, teacher=request.user)
    elif file_type == 'assignment':
        file = get_object_or_404(AssignmentFile, pk=pk, teacher=request.user)
    else:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        try:
            # Fetch the file path and other details before deletion
            file_path = file.file.name
            teacher_username = request.user.username
            year = file.year
            semester = file.semester
            title = file.title
            description = file.description
            class_name = file.class_name
            uploaded_at = file.uploaded_at
            
            # Delete the file from the filesystem
            file.file.delete(save=False)
            
            # Directly insert the details into the deleted collection
            deleted_details = {
                "teacher": teacher_username,
                "file_type": file_type,
                "year": year,
                "semester": semester,
                "title": title,
                "file_path": file_path,
                "description": description,
                "class_name": class_name,
                "uploaded_at": uploaded_at,
                "deleted_at": datetime.datetime.now().isoformat()
            }
            db.deleted.insert_one(deleted_details)
            
            # Log the deletion activity
            ActivityLog.objects.create(
                teacher=request.user,
                action='Deleted file',
                file_type=file_type,
                class_name=class_name,
                year=year,
                semester=semester,
                title=title,
                description=description
            )
            
            # Delete the file record from the database
            file.delete()
            
        except Exception as e:
            messages.error(request, "Could not delete the file. Please try again later.")
            return redirect('teacher_dashboard')

        return redirect('teacher_dashboard')

    return redirect('teacher_dashboard')


def logout_view(request):
    logout(request)
    return redirect('index')

def admin_dashboard(request):
    # Display teacher approval requests
    teacher_requests = TeacherApprovalRequest.objects.filter(is_approved=False)

    # Fetch activity logs for uploaded and deleted files
    activity_logs = ActivityLog.objects.filter(action='Uploaded file').order_by('-timestamp')
    deletion_logs = ActivityLog.objects.filter(action='Deleted file').order_by('-timestamp')

    # Fetch lists of teachers and students
    teachers = Teacher.objects.all()
    students = Student.objects.all()

    # Debug statements
    print("Teachers:", list(teachers))
    print("Students:", list(students))

    return render(request, 'admin_dashboard.html', {
        'teacher_requests': teacher_requests,
        'activity_logs': activity_logs,
        'deletion_logs': deletion_logs,
        'teachers': teachers,
        'students': students,
    })
