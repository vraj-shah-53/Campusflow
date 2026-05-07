from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object
import openai
import os

from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, Attendance, AttendanceReport, LeaveReportStudent, FeedBackStudent, StudentResult, FeePaymentHistory, CertificateApplication


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()

    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    subject_attendance_percent = []
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
        
        # Calculate subject-wise percentage
        total_subject_attendance = attendance_present_count + attendance_absent_count
        subject_percent = 0
        if total_subject_attendance > 0:
            subject_percent = round((attendance_present_count / total_subject_attendance) * 100, 2)
        subject_attendance_percent.append(subject_percent)
    subject_data_list = list(zip(subject_name, data_present, data_absent, subject_attendance_percent))
    
    attendance_percentage = 0
    if total_attendance > 0:
        attendance_percentage = round((attendance_present / total_attendance) * 100, 2)

    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "attendance_percentage": attendance_percentage,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent,
        "subject_data_list": subject_data_list
    }
    return render(request, "student_template/student_home_template.html", context)


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id) # Getting Logged in Student Data
    course = student.course_id # Getting Course Enrolled of LoggedIn Student
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    subjects = Subjects.objects.filter(course_id=course) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        stud_obj = Students.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'student_template/student_attendance_data.html', context)
       

def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'student_template/student_apply_leave.html', context)


def student_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = Students.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('student_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('student_apply_leave')


def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'student_template/student_feedback.html', context)


def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('student_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = Students.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('student_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('student_feedback')


def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def student_view_result(request):
    student = Students.objects.get(admin=request.user.id)
    student_result = StudentResult.objects.filter(student_id=student.id)
    context = {
        "student_result": student_result,
    }
    return render(request, "student_template/student_view_result.html", context)

def student_fee_payment(request):
    student = Students.objects.get(admin=request.user.id)
    course = student.course_id
    total_fee = course.course_fee
    
    # Calculate Paid Fee
    payment_history = FeePaymentHistory.objects.filter(student_id=student.id).order_by('-created_at')
    paid_fee = 0
    for payment in payment_history:
        paid_fee += payment.amount_paid
        
    pending_fee = total_fee - paid_fee
    
    context = {
        "student": student,
        "course": course,
        "total_fee": total_fee,
        "paid_fee": paid_fee,
        "pending_fee": pending_fee,
        "is_fully_paid": pending_fee <= 0,
        "payment_history": payment_history
    }
    return render(request, "student_template/student_fee_payment.html", context)


def student_fee_payment_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_fee_payment')
    else:
        amount_paid = request.POST.get('amount_paid')
        payment_method = request.POST.get('payment_method')
        
        student = Students.objects.get(admin=request.user.id)
        
        try:
            payment = FeePaymentHistory(student_id=student, amount_paid=amount_paid, payment_method=payment_method)
            payment.save()
            messages.success(request, f"Successfully paid Rs. {amount_paid} via {payment_method}")
            return redirect('student_fee_payment')
        except Exception as e:
            import traceback
            from django.http import HttpResponse
            return HttpResponse(f"ERROR: {str(e)}\n\n{traceback.format_exc()}")


def student_certificate_apply(request):
    student = Students.objects.get(admin=request.user.id)
    certificate_history = CertificateApplication.objects.filter(student_id=student.id).order_by('-created_at')
    
    context = {
        "certificate_history": certificate_history
    }
    return render(request, "student_template/student_certificate.html", context)


def student_certificate_apply_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_certificate_apply')
    else:
        certificate_type = request.POST.get('certificate_type')
        student = Students.objects.get(admin=request.user.id)
        
        try:
            application = CertificateApplication(student_id=student, certificate_type=certificate_type)
            application.save()
            messages.success(request, f"Successfully applied for {certificate_type}.")
            return redirect('student_certificate_apply')
        except:
            messages.error(request, "Failed to Apply for Certificate")
            return redirect('student_certificate_apply')






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def student_chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get('message', '').lower()
        
        # OPENAI Chatbot Integration
        # Ensure you set the environment variable OPENAI_API_KEY
        
        # Optional: You can hardcode your API key here for testing, but it's recommended to use environment variables.
        api_key = os.environ.get('OPENAI_API_KEY', 'your-api-key-here')
        
        if api_key and api_key != 'your-api-key-here':
            try:
                client = openai.OpenAI(api_key=api_key)
                
                # We add system context to make the AI act like a campus helper
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful university AI assistant for the CampusFlow Student Dashboard. You help students understand features like attendance, results, leave application, fee payment, and certificate applications. Keep your answers brief, friendly, and helpful."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150
                )
                
                reply = response.choices[0].message.content
                return JsonResponse({"success": True, "reply": reply})
            except Exception as e:
                # Fallback on the rule-based system if the API call fails
                print(f"OpenAI API Error: {e}")
                pass
                
        # Fallback to Rule-based logic if API Key is not set or failed
        reply = "I am an AI assistant! You can ask me about your Attendance, Results, Applying for Leave, or Paying Fees. How can I help you today?"
        
        if any(word in user_message for word in ['attendance', 'present', 'absent']):
            reply = "You can view your subject-wise attendance by navigating to the 'View Attendance' tab on your dashboard sidebar. Pick the subject and date range to see detailed logs."
        elif any(word in user_message for word in ['result', 'marks', 'score', 'grades', 'grade']):
            reply = "To check your marks, please visit the 'View Result' section in your left sidebar menu."
        elif any(word in user_message for word in ['leave', 'holiday', 'absent', 'sick']):
            reply = "You can apply for leave in the 'Apply for Leave' section. Input the date range and reason, and your assigned staff member will review it."
        elif any(word in user_message for word in ['fee', 'payment', 'pay', 'rupees', 'transactions']):
            reply = "Fees can be managed under 'Pay Fees'. You can see your total fees, check how much is pending, and make a payment from there directly."
        elif any(word in user_message for word in ['certificate', 'degree', 'bonafide', 'document']):
            reply = "You can request certificates like Bonafide, Transfer Certificate, or degree transcripts from the 'Apply Certificate' section on your dashboard."
        elif any(word in user_message for word in ['hi', 'hello', 'hey', 'greetings']):
            reply = "Hello there! Welcome to the student chatbot. How can I assist you with CampusFlow today?"
        elif any(word in user_message for word in ['thank', 'thanks', 'cool']):
            reply = "You're very welcome! Let me know if you need anything else."
        elif any(word in user_message for word in ['password', 'profile', 'name']):
            reply = "You can update your personal information or password by clicking the 'Update Profile' option under the gear icon in the top right navbar."
            
        return JsonResponse({"success": True, "reply": reply})
    return JsonResponse({"success": False, "reply": "Invalid request."})
