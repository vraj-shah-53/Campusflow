from student_management_app.models import CollegeSetting

def college_settings_processor(request):
    college_setting = None
    if request.user.is_authenticated:
        try:
            if request.user.user_type == '1':
                college_setting = CollegeSetting.objects.filter(admin_creator=request.user).first()
            elif request.user.user_type == '2':
                college_setting = CollegeSetting.objects.filter(admin_creator=request.user.staffs.admin_creator).first()
            elif request.user.user_type == '3':
                college_setting = CollegeSetting.objects.filter(admin_creator=request.user.students.admin_creator).first()
        except Exception:
            pass
    return {
        'college_setting': college_setting
    }
