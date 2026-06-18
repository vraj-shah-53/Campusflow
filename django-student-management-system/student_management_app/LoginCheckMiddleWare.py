from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect
from django.urls import reverse


class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        # print(modulename)
        user = request.user

        #Check whether the user is logged in or not
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("admin_home")
            
            elif user.user_type == "2":
                if modulename == "student_management_app.StaffViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("staff_home")
            
            elif user.user_type == "3":
                if modulename == "student_management_app.StudentViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("student_home")

            else:
                return redirect("login")

        else:
            allowed_paths = []
            try:
                allowed_paths.append(reverse("entrance"))
            except:
                pass
            try:
                allowed_paths.append(reverse("login"))
            except:
                pass
            try:
                allowed_paths.append(reverse("doLogin"))
            except:
                pass
            try:
                allowed_paths.append(reverse("admin_register"))
            except:
                pass
            try:
                allowed_paths.append(reverse("do_admin_register"))
            except:
                pass
            
            for r in ['admin', 'faculty', 'staff', 'student']:
                try:
                    allowed_paths.append(reverse("login_with_role", kwargs={"role": r}))
                except:
                    pass

            if request.path in allowed_paths:
                pass
            else:
                return redirect("entrance")
