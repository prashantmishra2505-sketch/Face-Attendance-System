from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        # We leave 'photo' and 'encoding' out so the user doesn't see them!
        fields = ['name', 'email', 'class_section']