from django.contrib import admin
from .models import Employee, Department, Designation, Attendance, Leave, Salary
admin.site.register([Employee,Department,Designation,Attendance,Salary])
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    readonly_fields=('status',)
