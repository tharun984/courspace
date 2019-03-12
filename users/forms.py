## @brief Forms for the course app.

from django import forms
from django.contrib.auth.models import User
from course.models import Student
from instructor.models import Instructor

## @brief This class represents the form to register a user.
class UserRegistration(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']


## @brief This class represents the form to register a student.
class StudentRegistration(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'email', 'course_list']


class InstructorRegistration(forms.ModelForm):

    class Meta:
        model = Instructor
        fields = ['name', 'email', 'information']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Display name"
        self.fields["email"].label = "Email address"
