import os
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from pymongo import MongoClient
import re
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404

from django.conf import settings
from .models import PDFFile, VideoFile, AssignmentFile, TeacherApprovalRequest, ActivityLog
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
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'login.html')

import re
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.academe

def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name'].upper()  # Convert name to uppercase
        id_number = request.POST['id_number']
        username = request.POST['username']
        password = request.POST['password']
        is_teacher = 'is_teacher' in request.POST
        is_student = 'is_student' in request.POST

        # Validate username
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_]).{8,}$', username):
            messages.error(request, 'Username must be longer than 8 characters, contain a special character, and an alphanumeric combination.')
            return render(request, 'signup.html', {
                'name': name,
                'id_number': id_number,
                'username': username,
                'is_teacher': is_teacher,
                'is_student': is_student,
                'year': request.POST.get('year', ''),
                'semester': request.POST.get('semester', ''),
                'class_name': request.POST.get('class_name', '')
            })

        # Validate password
        if not re.match(r'^(?=.*[A-Z])(?=.*\W).+$', password):
            messages.error(request, 'Password must contain at least one uppercase letter and one special character.')
            return render(request, 'signup.html', {
                'name': name,
                'id_number': id_number,
                'username': username,
                'is_teacher': is_teacher,
                'is_student': is_student,
                'year': request.POST.get('year', ''),
                'semester': request.POST.get('semester', ''),
                'class_name': request.POST.get('class_name', '')
            })

        # Check if username is unique
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'signup.html', {
                'name': name,
                'id_number': id_number,
                'username': username,
                'is_teacher': is_teacher,
                'is_student': is_student,
                'year': request.POST.get('year', ''),
                'semester': request.POST.get('semester', ''),
                'class_name': request.POST.get('class_name', '')
            })

        # Validate full name
        if not re.match(r'^[A-Z\s]+$', name) or len(name.split()) < 2:
            messages.error(request, 'Please provide your full name in uppercase.')
            return render(request, 'signup.html', {
                'name': name,
                'id_number': id_number,
                'username': username,
                'is_teacher': is_teacher,
                'is_student': is_student,
                'year': request.POST.get('year', ''),
                'semester': request.POST.get('semester', ''),
                'class_name': request.POST.get('class_name', '')
            })

        # Create Django user
        user = User.objects.create_user(username=username, password=password)
        
        # Store common details in MongoDB
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
            messages.info(request, 'Your request to become a teacher is pending approval. Contact the admin for more information.')
        elif is_student:
            # Handle student-specific details
            year = request.POST['year']
            semester = request.POST['semester']
            class_name = request.POST['class_name']

            # Format class_name
            class_name = ' '.join(class_name.upper().split())
            
            user_details.update({
                "year": year,
                "semester": semester,
                "class_name": class_name
            })
            db.student.insert_one(user_details)
            assign_student_role(user)
            messages.success(request, 'You have successfully signed up as a student. Please go back to the login page.')
        else:
            messages.error(request, 'Please select either Teacher or Student role.')
            return render(request, 'signup.html', {
                'name': name,
                'id_number': id_number,
                'username': username,
                'is_teacher': is_teacher,
                'is_student': is_student,
                'year': request.POST.get('year', ''),
                'semester': request.POST.get('semester', ''),
                'class_name': request.POST.get('class_name', '')
            })

        return redirect('index')  # Redirect to the login or index page
    return render(request, 'signup.html')

def assign_student_role(user):
    # Assign the user a student role without staff status
    student_group, _ = Group.objects.get_or_create(name='student')
    user.groups.add(student_group)
    user.is_staff = False
    user.save()


def approve_teacher(_, pk):
    approval_request = TeacherApprovalRequest.objects.get(pk=pk)
    user = approval_request.user
    teacher_group, _ = Group.objects.get_or_create(name='teacher')
    user.groups.add(teacher_group)
    user.is_staff = True
    user.save()
    approval_request.is_approved = True
    approval_request.save()
    return redirect('admin_dashboard')

def reject_teacher(_, pk):
    approval_request = TeacherApprovalRequest.objects.get(pk=pk)
    user = approval_request.user
    assign_student_role(user)
    approval_request.delete()
    return redirect('admin_dashboard')

from .forms import UploadAssignmentForm


from bson import ObjectId
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os

@login_required
def student_dashboard(request):
    teachers_collection = db.teacher
    tchr = list(teachers_collection.find({}, {"_id": 0, "name": 1, "id_number": 1, "username": 1}))

    # Get the logged-in student's details
    student = request.user
    student_details = db.student.find_one({"username": student.username})

    print(f"Student Username: {student.username}")  # Debug print

    if student_details:
        year = student_details.get("year")
        semester = student_details.get("semester")
        class_name = student_details.get("class_name")
        student_name = student_details.get("name")  # Get the student's name
        
        print(f"Student Details: Year - {year}, Semester - {semester}, Class Name - {class_name}, Name - {student_name}")  # Debug print

        # Format class_name to match the formatting used during upload
        class_name = ' '.join(class_name.upper().split())

        # Filter files based on the student's details
        uploaded_pdfs = PDFFile.objects.filter(year=year, semester=semester, class_name=class_name)
        uploaded_videos = VideoFile.objects.filter(year=year, semester=semester, class_name=class_name)
        uploaded_assignments = AssignmentFile.objects.filter(year=year, semester=semester, class_name=class_name)
        
        print(f"Uploaded PDFs: {uploaded_pdfs.count()}")  # Debug print
        print(f"Uploaded Videos: {uploaded_videos.count()}")  # Debug print
        print(f"Uploaded Assignments: {uploaded_assignments.count()}")  # Debug print

        if request.method == 'POST':
            # Get the teacher's username from the submitted form
            teacher_username = request.POST.get('teacher_username')
            form = UploadAssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment_file = request.FILES['assignment']
                
                # Create a directory for storing assignments if it doesn't exist
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'resources', 'student_assignments', year, semester, class_name)
                os.makedirs(upload_dir, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_dir, assignment_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in assignment_file.chunks():
                        destination.write(chunk)

                # Construct the URL path for the file
                file_url = os.path.join(settings.MEDIA_URL,'resources', 'student_assignments', year, semester, class_name, assignment_file.name)

                # Store student information in MongoDB
                upload_details = {
                    "student_username": student.username,
                    "student_name": student_name,  # Add the student's name
                    "teacher_username": teacher_username,  # Store the teacher's username
                    "year": year,
                    "semester": semester,
                    "class_name": class_name,
                    "file_name": assignment_file.name,
                    "file_url": file_url,  # Store the file URL
                    "uploaded_at": datetime.now().isoformat(),
                    }
                db.assignments.insert_one(upload_details)

                return redirect('student_dashboard')  # Redirect to the same page or another page

        else:
            form = UploadAssignmentForm()
    else:
        print("Student details not found in the database.")  # Debug print
        uploaded_pdfs = []
        uploaded_videos = []
        uploaded_assignments = []
    
    posts = handle_blog_posts(request)

    return render(request, 'student_dashboard.html', {
        'form': form,
        'teachers': tchr,
        'uploaded_pdfs': uploaded_pdfs,
        'uploaded_videos': uploaded_videos,
        'uploaded_assignments': uploaded_assignments,
        'posts':posts
    })

def fetch_data_from_db():
    # Fetch teachers data
    teachers_collection = db.teacher
    teachers = list(teachers_collection.find({}, {"_id": 0, "name": 1, "id_number": 1, "username": 1}))

    # Fetch students data
    students_collection = db.student
    students = list(students_collection.find({}, {"_id": 0, "name": 1, "id_number": 1, "username": 1, "year": 1, "semester": 1, "class_name": 1}))

    # Fetch activity logs
    activity_logs_collection = db.uploads
    activity_logs = list(activity_logs_collection.find({}, {"_id": 0, "teacher": 1, "file_type": 1, "class_name": 1, "year": 1, "semester": 1, "title": 1, "description": 1, "uploaded_at": 1}))

    # Fetch deleted logs
    deleted_logs_collection = db.deleted
    deletion_logs = list(deleted_logs_collection.find({}, {"_id": 0, "teacher": 1, "file_type": 1, "class_name": 1, "year": 1, "semester": 1, "title": 1, "description": 1, "deleted_at": 1}))

    return teachers, students, activity_logs, deletion_logs

from bson import ObjectId
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os

@login_required
def teacher_dashboard(request):
    assignment_collection = db.assignments
    students_collection = db.student

    # Initialize filter parameters
    year = request.GET.get('year')
    semester = request.GET.get('semester')
    class_name = request.GET.get('class_name')

    # Build the query for filtering students
    query = {}
    if year:
        query['year'] = year
    if semester:
        query['semester'] = semester
    if class_name:
        query['class_name'] = class_name.upper().strip()

    # Fetch students based on the query
    stds = list(students_collection.find(query, {"_id": 0, "name": 1, "id_number": 1, "username": 1, "year": 1, "semester": 1, "class_name": 1}))
    assg = list(assignment_collection.find({"teacher_username": request.user.username}, {"_id": 0, "student_username": 1, "teacher_username": 1, "year": 1, "semester": 1, "class_name": 1, "file_name": 1, "file_url": 1, "uploaded_at": 1}))
    student_assignments = list(assignment_collection.find({"teacher_username": request.user.username}, {"_id": 0, "student_name": 1, "year": 1, "semester": 1, "class_name": 1, "file_name": 1, "file_url": 1, "uploaded_at": 1}))

    form = UploadFileForm()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_type = form.cleaned_data['file_type']
            year = form.cleaned_data['year']
            semester = form.cleaned_data['semester']
            title = form.cleaned_data['title']
            file = form.cleaned_data['file']
            description = form.cleaned_data['description']
            class_name = ' '.join(form.cleaned_data['class_name'].upper().split())

            # Save the file to the appropriate model and directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'resources', file_type, year, semester, class_name)
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            file_url = os.path.join(settings.MEDIA_URL, 'resources', file_type, year, semester, class_name, file.name)

            # Save the file to the appropriate model
            if file_type == 'pdf':
                PDFFile(teacher=request.user, year=year, semester=semester, title=title, file=file_path, description=description, class_name=class_name).save()
            elif file_type == 'video':
                VideoFile(teacher=request.user, year=year, semester=semester, title=title, file=file_path, description=description, class_name=class_name).save()
            elif file_type == 'assignment':
                AssignmentFile(teacher=request.user, year=year, semester=semester, title=title, file=file_path, description=description, class_name=class_name).save()

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

            upload_details = {
                "teacher": request.user.username,
                "file_type": file_type,
                "year": year,
                "semester": semester,
                "title": title,
                "file_url": file_url,
                "description": description,
                "class_name": class_name,
                "uploaded_at": datetime.now().isoformat(),
            }
            db.uploads.insert_one(upload_details)

            return redirect('teacher_dashboard')
        else:
            print("Form errors:", form.errors)

    uploaded_pdfs = PDFFile.objects.filter(teacher=request.user)
    uploaded_videos = VideoFile.objects.filter(teacher=request.user)
    uploaded_assignments = AssignmentFile.objects.filter(teacher=request.user)

    posts = handle_blog_posts(request)

    return render(request, 'teacher_dashboard.html', {
        'form': form,
        'uploaded_pdfs': uploaded_pdfs,
        'uploaded_videos': uploaded_videos,
        'uploaded_assignments': uploaded_assignments,
        'students': stds,
        'assignment': assg,
        'student_assignments': student_assignments,
        "posts":posts
    })


from datetime import datetime, timedelta

def handle_blog_posts(request):
    user = request.user

    if request.method == 'POST':
        # Handle blog post creation
        if 'post_title' in request.POST:
            post_title = request.POST.get('post_title')
            post_content = request.POST.get('post_content')
            author_name = "Admin Announcement" if user.is_superuser else user.username

            # Check for duplicate post content within the last 6 hours
            six_hours_ago = datetime.now() - timedelta(hours=6)
            existing_post = db.posts.find_one({
                "author": author_name,
                "title": post_title,
                "content": post_content,
                "created_at": {"$gte": six_hours_ago.isoformat()}
            })

            if not existing_post:
                new_post = {
                    "author": author_name,
                    "title": post_title,
                    "content": post_content,
                    "created_at": datetime.now().isoformat(),
                    "likes": 0,
                    "liked_by": [],
                    "followups": [],
                    "is_superuser_post": user.is_superuser  # flag to identify superuser posts
                }
                db.posts.insert_one(new_post)

        # Handle follow-up creation
        elif 'followup_content' in request.POST:
            post_id = request.POST.get('post_id')
            followup_content = request.POST.get('followup_content')
            post = db.posts.find_one({"_id": ObjectId(post_id)})

            # Prevent follow-ups for superuser posts
            if not post.get('is_superuser_post'):
                followup = {
                    "author": user.username,
                    "content": followup_content,
                    "created_at": datetime.now().isoformat(),
                    "likes": 0,
                    "liked_by": []
                }
                db.posts.update_one({"_id": ObjectId(post_id)}, {"$push": {"followups": followup}})

        # Handle likes for posts
        elif 'like_post' in request.POST:
            post_id = request.POST.get('like_post')
            post = db.posts.find_one({"_id": ObjectId(post_id)})
            if user.username not in post['liked_by']:
                db.posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes": 1}, "$push": {"liked_by": user.username}})
                
        # Handle likes for follow-ups
        elif 'like_followup' in request.POST:
            post_id = request.POST.get('post_id')
            followup_index = int(request.POST.get('like_followup'))
            followup_path = f"followups.{followup_index}.likes"
            liked_by_path = f"followups.{followup_index}.liked_by"
            post = db.posts.find_one({"_id": ObjectId(post_id)})
            if user.username not in post['followups'][followup_index]['liked_by']:
                db.posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {followup_path: 1}, "$push": {liked_by_path: user.username}})

    posts = list(db.posts.find().sort("created_at", -1))

    # Convert ObjectId to string and rename _id to id for the template
    for post in posts:
        post['id'] = str(post['_id'])
        post['created_at'] = datetime.fromisoformat(post['created_at'])
        del post['_id']
        for followup in post['followups']:
            followup['id'] = str(followup.get('_id', ''))
            followup['created_at'] = datetime.fromisoformat(followup['created_at'])
            if '_id' in followup:
                del followup['_id']

    return posts

def delete_file(request, file_type, pk):
    if file_type == 'pdf':
        file = get_object_or_404(PDFFile, pk=pk, teacher=request.user)
    elif file_type == 'video':
        file = get_object_or_404(VideoFile, pk=pk, teacher=request.user)
    elif file_type == 'assignment':
        file = get_object_or_404(AssignmentFile, pk=pk, teacher=request.user)
    elif file_type == 'student_assignment':
        file = get_object_or_404(AssignmentFile, pk=pk)
    else:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        try:
            # Fetch the file path and other details before deletion
            file_path = file.file.name
            teacher_username = request.user.username if file_type != 'student_assignment' else file.teacher.username
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
                "deleted_at": datetime.now().isoformat()
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
            messages.error(request, f"Could not delete the file. Error: {e}")
            return redirect('teacher_dashboard')

        return redirect('teacher_dashboard')

    return redirect('teacher_dashboard')
    
def logout_view(request):
    logout(request)
    return redirect('index')

def admin_dashboard(request):
    # Display teacher approval requests
    teacher_requests = TeacherApprovalRequest.objects.filter(is_approved=False)

    # Fetch lists of teachers and students using pymongo
    teachers, students, activity_logs, deletion_logs = fetch_data_from_db()

    posts = handle_blog_posts(request)

    return render(request, 'admin_dashboard.html', {
        'teacher_requests': teacher_requests,
        'activity_logs': activity_logs,
        'deletion_logs': deletion_logs,
        'teachers': teachers,
        'students': students,
        'posts':posts
    })

def delete_teacher(request, username):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
            # Remove teacher from MongoDB
            db.teacher.delete_one({"username": username})
            # Remove teacher from Django user table
            user.delete()

            messages.success(request, f'Teacher {username} has been deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, f'Teacher {username} does not exist.')
        return redirect('admin_dashboard')

def delete_student(request, username):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
            # Remove student from MongoDB
            db.student.delete_one({"username": username})
            # Remove student from Django user table
            user.delete()

            messages.success(request, f'Student {username} has been deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, f'Student {username} does not exist.')
        return redirect('admin_dashboard')

def clear_activity_log(request):
    if request.method == 'POST':
        db.uploads.delete_many({})
        return redirect('admin_dashboard')

def clear_deleted_log(request):
    if request.method == 'POST':
        db.deleted.delete_many({})
        return redirect('admin_dashboard')
