import csv
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Employee, Department, Designation, Attendance, Leave, Salary
from .forms import EmployeeForm, ProfileForm, DepartmentForm, DesignationForm, AttendanceForm, LeaveForm, SalaryForm

def hr(user): return user.is_staff or user.is_superuser

def require_hr(request):
    if not hr(request.user): raise PermissionDenied

def own(request): return get_object_or_404(Employee,user=request.user,active=True)

def scoped(request,model):
    return model.objects.all() if hr(request.user) else model.objects.filter(employee=own(request))

def home(request): return render(request,'home.html')
def about(request): return render(request,'about.html')
def contact(request): return render(request,'contact.html')

@login_required
def dashboard(request):
    if not hr(request.user): return redirect('profile')
    return render(request,'dashboard.html',{'total':Employee.objects.filter(active=True).count(),'departments':Department.objects.count(),'pending':Leave.objects.filter(status='Pending').count()})

@login_required
def employee_list(request):
    require_hr(request)
    rows=Employee.objects.select_related('department','designation').order_by('full_name')
    q=request.GET.get('q','').strip(); dept=request.GET.get('department','')
    if q: rows=rows.filter(Q(full_name__icontains=q)|Q(employee_id__icontains=q)|Q(email__icontains=q))
    if dept.isdigit(): rows=rows.filter(department_id=dept)
    return render(request,'employee_list.html',{'employees':rows,'departments':Department.objects.all(),'q':q,'selected':dept})

def edit_form(request,form_class,title,back,instance=None):
    form=form_class(request.POST if request.method=='POST' else None,instance=instance)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Saved successfully.'); return redirect(back)
    return render(request,'form.html',{'form':form,'title':title,'back':back})

@login_required
def employee_edit(request,pk=None):
    require_hr(request)
    return edit_form(request,EmployeeForm,'Employee details','employee_list',get_object_or_404(Employee,pk=pk) if pk else None)

@login_required
def employee_detail(request,pk):
    require_hr(request)
    return render(request,'profile.html',{'employee':get_object_or_404(Employee,pk=pk)})

@login_required
@require_POST
def deactivate(request,pk):
    require_hr(request)
    employee=get_object_or_404(Employee,pk=pk); employee.active=False; employee.save(update_fields=['active']); return redirect('employee_list')

@login_required
def profile(request): return render(request,'profile.html',{'employee':own(request),'own_profile':True})

@login_required
def profile_edit(request): return edit_form(request,ProfileForm,'Edit my profile','profile',own(request))

@login_required
def department(request):
    require_hr(request)
    return render(request,'department.html',{'departments':Department.objects.all(),'designations':Designation.objects.all()})

@login_required
def department_edit(request,pk=None):
    require_hr(request); return edit_form(request,DepartmentForm,'Department','department',get_object_or_404(Department,pk=pk) if pk else None)

@login_required
def designation_edit(request,pk=None):
    require_hr(request); return edit_form(request,DesignationForm,'Designation','department',get_object_or_404(Designation,pk=pk) if pk else None)

@login_required
def attendance(request): return render(request,'attendance.html',{'rows':scoped(request,Attendance).order_by('-date')})

@login_required
def attendance_edit(request,pk=None):
    require_hr(request); return edit_form(request,AttendanceForm,'Attendance','attendance',get_object_or_404(Attendance,pk=pk) if pk else None)

@login_required
def leaves(request): return render(request,'leaves.html',{'rows':scoped(request,Leave).order_by('-start_date')})

@login_required
def leave_apply(request):
    employee=own(request); form=LeaveForm(request.POST if request.method=='POST' else None)
    if request.method=='POST' and form.is_valid():
        leave=form.save(commit=False); leave.employee=employee
        if leave.days>employee.leave_balance: form.add_error(None,'Insufficient leave balance.')
        else: leave.save(); return redirect('leaves')
    return render(request,'form.html',{'form':form,'title':'Apply for leave','back':'leaves'})

@login_required
@require_POST
@transaction.atomic
def leave_review(request,pk):
    require_hr(request); leave=get_object_or_404(Leave.objects.select_for_update(),pk=pk)
    action=request.POST.get('action')
    if leave.status!='Pending' or action not in ['Approved','Rejected']: return redirect('leaves')
    employee=Employee.objects.select_for_update().get(pk=leave.employee_id)
    if action=='Approved':
        if employee.leave_balance<leave.days or Leave.objects.filter(employee=employee,status='Approved',start_date__lte=leave.end_date,end_date__gte=leave.start_date).exists():
            messages.error(request,'Insufficient balance or overlapping approved leave.'); return redirect('leaves')
        employee.leave_balance-=leave.days; employee.save(update_fields=['leave_balance'])
    leave.status=action; leave.save(update_fields=['status']); return redirect('leaves')

@login_required
def salary(request): return render(request,'salary.html',{'rows':scoped(request,Salary).order_by('-month')})

@login_required
def salary_edit(request,pk=None):
    require_hr(request); return edit_form(request,SalaryForm,'Salary','salary',get_object_or_404(Salary,pk=pk) if pk else None)

@login_required
def report(request):
    require_hr(request)
    response=HttpResponse(content_type='text/csv'); response['Content-Disposition']='attachment; filename="employees.csv"'
    writer=csv.writer(response); writer.writerow(['ID','Name','Department','Designation','Active'])
    def safe(value):
        value=str(value); return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value
    for e in Employee.objects.select_related('department','designation'): writer.writerow([safe(x) for x in [e.employee_id,e.full_name,e.department,e.designation,e.active]])
    return response
