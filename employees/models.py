from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, blank=True)
    address = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    date_of_joining = models.DateField()
    employment_type = models.CharField(max_length=30, choices=[(x,x) for x in ['Full-time','Part-time','Contract']])
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    leave_balance = models.PositiveIntegerField(default=20)
    def __str__(self): return self.full_name

class Attendance(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[(x,x) for x in ['Present','Absent','Late','Leave']])
    class Meta:
        constraints = [models.UniqueConstraint(fields=['employee','date'],name='unique_attendance')]
    def __str__(self): return f'{self.employee} - {self.date}'

class Leave(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[(x,x) for x in ['Pending','Approved','Rejected']],default='Pending')
    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date must not precede start date.')
    @property
    def days(self): return (self.end_date-self.start_date).days+1
    def __str__(self): return f'{self.employee} - {self.start_date}'

class Salary(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    month = models.DateField(help_text='Use the first day of the salary month.')
    amount = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=['employee','month'],name='unique_salary')]
    def clean(self):
        if self.month and self.month.day != 1: raise ValidationError('Use the first day of the month.')
    def __str__(self): return f'{self.employee} - {self.month}'
