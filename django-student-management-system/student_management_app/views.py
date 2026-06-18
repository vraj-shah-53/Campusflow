from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from student_management_app.EmailBackEnd import EmailBackEnd
from student_management_app.models import CustomUser, Courses, SessionYearModel, Staffs, Students


def entrance(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect('admin_home')
        elif request.user.user_type == '2':
            return redirect('staff_home')
        elif request.user.user_type == '3':
            return redirect('student_home')
    return render(request, 'entrance.html')


def loginPage(request, role=None):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect('admin_home')
        elif request.user.user_type == '2':
            return redirect('staff_home')
        elif request.user.user_type == '3':
            return redirect('student_home')
            
    if not role:
        return redirect('entrance')
        
    if role == 'faculty':
        role = 'staff'
        
    if role == 'admin':
        return render(request, 'admin_login_register.html')
    elif role in ['staff', 'student']:
        return render(request, 'login.html', {"role": role})
    else:
        return redirect('entrance')


def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        role = request.POST.get('role')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = EmailBackEnd.authenticate(request, username=email, password=password)
        if user != None:
            user_type = user.user_type
            
            # Enforce role matching
            if role == 'admin' and user_type != '1':
                messages.error(request, "This account is not registered as an Admin.")
                return redirect('login_with_role', role='admin')
            elif role == 'staff' and user_type != '2':
                messages.error(request, "This account is not registered as Faculty.")
                return redirect('login_with_role', role='faculty')
            elif role == 'student' and user_type != '3':
                messages.error(request, "This account is not registered as a Student.")
                return redirect('login_with_role', role='student')
                
            login(request, user)
            if user_type == '1':
                # Dynamically claim legacy records for original admin accounts
                if user.username in ['admin', 'vraj', 'ameechhayaa@vgecg.ac.in']:
                    Courses.objects.filter(admin_creator__isnull=True).update(admin_creator=user)
                    SessionYearModel.objects.filter(admin_creator__isnull=True).update(admin_creator=user)
                    Staffs.objects.filter(admin_creator__isnull=True).update(admin_creator=user)
                    Students.objects.filter(admin_creator__isnull=True).update(admin_creator=user)
                return redirect('admin_home')
            elif user_type == '2':
                return redirect('staff_home')
            elif user_type == '3':
                return redirect('student_home')
            else:
                messages.error(request, "Invalid Login!")
                return redirect('entrance')
        else:
            messages.error(request, "Invalid Login Credentials!")
            if role == 'staff':
                return redirect('login_with_role', role='faculty')
            elif role in ['admin', 'student']:
                return redirect('login_with_role', role=role)
            else:
                return redirect('entrance')


def get_user_details(request):
    if request.user.is_authenticated:
        return HttpResponse("User: "+request.user.email+" User Type: "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


def admin_register(request):
    if request.user.is_authenticated:
        return redirect('entrance')
    return render(request, 'admin_login_register.html', {"register_active": True})


def do_admin_register(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not username or not email or not password:
            messages.error(request, "All registration fields are required!")
            return render(request, 'admin_login_register.html', {"register_active": True})
            
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return render(request, 'admin_login_register.html', {"register_active": True})
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'admin_login_register.html', {"register_active": True})
            
        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=1)
            messages.success(request, "Admin account created successfully! Please login.")
            return redirect('login_with_role', role='admin')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'admin_login_register.html', {"register_active": True})
