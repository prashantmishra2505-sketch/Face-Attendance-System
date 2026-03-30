from django.db import models
from django.core.exceptions import ValidationError

# 1. Custom Validator to force the college email
def validate_jss_email(value):
    if not value.endswith('@jssaten.ac.in'):
        raise ValidationError('Only official @jssaten.ac.in emails are allowed.')

# 2. The Student Registration Table
class Student(models.Model):
    # Dropdown choices for the class
    CLASS_CHOICES = [
        ('IT 1', 'Information Technology - Section 1'),
        ('IT 2', 'Information Technology - Section 2'),
        ('IT 3', 'Information Technology - Section 3'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[validate_jss_email])
    class_section = models.CharField(max_length=10, choices=CLASS_CHOICES)
    
    # The photo and encoding
    photo = models.ImageField(upload_to='student_photos/')
    encoding = models.BinaryField() # We use BinaryField to store the pickle bytes cleanly
    
    def __str__(self):
        return f"{self.name} ({self.class_section})"

# 3. The New Attendance Log Table
class Attendance(models.Model):
    # This links the attendance record directly to the specific student
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    # Automatically saves the exact date and time they are recognized
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.date} at {self.time}"