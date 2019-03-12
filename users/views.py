## @brief Views for the course app.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import UserRegistration, StudentRegistration,InstructorRegistration
from course.models import Student, User
from instructor.models import Instructor
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

## @brief view for the login page of the website.
#
# This view is called by /login url.\n
# It returns the login page for the students and instructors to login.
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            try:
                student = Student.objects.get(user=request.user)
                return redirect('course:index')
            except:
                return redirect('instructor:instructor_index')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    return render(request, 'login.html')


## @brief view for the registration page for students to register themselves.
#
# This view is called by /register_user url.\n
# It returns the form for students to register themselves.\n
# The students can choose a usename and password and fill out their details and select the courses they wish to enroll in.

def register_instructor(request):
    user_form = UserRegistration(request.POST or None)
    instructor_form = InstructorRegistration(request.POST or None)
    #instructor_form.Meta.fields
    if user_form.is_valid() and instructor_form.is_valid():
        user = user_form.save(commit=False)
        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.save()

        instructor = instructor_form.save(commit=False)
        instructor.user = User.objects.get(id=user.id)
        instructor.save()
        instructor_form.save()
        #student_form.save_m2m() # saves the many to many field relation (between the course and student model) entered in the form while selecting the courses

        return login_user(request)

    return render(request,'register_instructor.html', {'user_form': user_form, 'instructor_form': instructor_form})




def register_user(request):
    user_form = UserRegistration(request.POST or None)
    student_form = StudentRegistration(request.POST or None)

    if user_form.is_valid() and student_form.is_valid():
        user = user_form.save(commit=False)
        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.save()

        student = student_form.save(commit=False)
        student.user = User.objects.get(id=user.id)
        student.save()
        student_form.save_m2m() # saves the many to many field relation (between the course and student model) entered in the form while selecting the courses

        return login_user(request)

    return render(request,'register_user.html', {'user_form': user_form, 'student_form': student_form})
