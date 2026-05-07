import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import CustomUser, Courses, SessionYearModel, AdminHOD, Staffs, Students

print("Cleaning existing users...")
CustomUser.objects.all().delete()
Courses.objects.all().delete()
SessionYearModel.objects.all().delete()

print("Creating default Course and SessionYear...")
course, created = Courses.objects.get_or_create(id=1, defaults={"course_name": "Default Course"})
session, created = SessionYearModel.objects.get_or_create(
    id=1, 
    defaults={
        "session_start_year": date(2023, 1, 1), 
        "session_end_year": date(2024, 1, 1)
    }
)

print("Creating Superuser (Admin)...")
# Since the model has `user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))`
# The model uses `CharField` for user_type by default=1. Let's pass string values to be safe.
admin = CustomUser.objects.create_superuser(username='admin', password='admin_vraj', email='admin@test.com', user_type="1")
# Just to be sure the profile is created, let's check
if not hasattr(admin, 'adminhod'):
    AdminHOD.objects.get_or_create(admin=admin)

print("Creating Student...")
student = CustomUser.objects.create_user(username='dhara', password='dhara7115', email='dhara@test.com', user_type="3")
if not hasattr(student, 'students'):
    Students.objects.get_or_create(
        admin=student, 
        course_id=course, 
        session_year_id=session, 
        address="", 
        profile_pic="", 
        gender="Female"
    )

print("Creating Staff...")
staff = CustomUser.objects.create_user(username='jaswant', password='jaswant@vgec', email='jaswant@test.com', user_type="2")
if not hasattr(staff, 'staffs'):
    Staffs.objects.get_or_create(admin=staff, address="")

print("Database reset completed with explicit 3 users.")
