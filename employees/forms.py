from django import forms
from .models import Employee, Department, Designation, Attendance, Leave, Salary
class StyledForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if isinstance(field,forms.DateField): field.widget = forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'})
            field.widget.attrs['class'] = 'form-check-input' if isinstance(field.widget,forms.CheckboxInput) else 'form-select' if isinstance(field.widget,forms.Select) else 'form-control'
class EmployeeForm(StyledForm):
    class Meta:
        model=Employee
        fields='__all__'
class ProfileForm(StyledForm):
    class Meta:
        model=Employee
        fields=['phone','address','emergency_contact']
class DepartmentForm(StyledForm):
    class Meta:
        model=Department
        fields=['name']
class DesignationForm(StyledForm):
    class Meta:
        model=Designation
        fields=['name']
class AttendanceForm(StyledForm):
    class Meta:
        model=Attendance
        fields='__all__'
class LeaveForm(StyledForm):
    class Meta:
        model=Leave
        fields=['start_date','end_date','reason']
class SalaryForm(StyledForm):
    class Meta:
        model=Salary
        fields='__all__'
