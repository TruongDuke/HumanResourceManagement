from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User
from .models import Employee , Contract, Task, Attendance
from .forms import EmployeeForm
from django.http import HttpResponse
from datetime import datetime, date
from django.utils import timezone
from django.utils.timezone import now
from django.db import connection
from django.contrib import messages
import logging
from datetime import time
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Sử dụng backend không yêu cầu GUI
import matplotlib.pyplot as plt
import io
import base64


logger = logging.getLogger(__name__)


def login_form(request):
    return render(request, 'nhanvien/login.html')

def logoutView(request):                            
    logout(request)
    return redirect('home')

def loginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)  
            
            # phân quyền theo group
            if user.is_admin or user.is_superuser:  
                return redirect('dashboard')        
            elif user.is_manager:
                return redirect('manager')
            else: 
                return redirect('employee')
        else:    
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng!")
    
    return render(request, 'nhanvien/login.html')

@login_required
def update_employee_info(request):
    user = request.user 

    try:
        employee = Employee.objects.get(user__email=user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('employee')

    if request.method == 'POST':

        employee.name = request.POST['name']
        employee.address = request.POST['address']
        employee.phone_number = request.POST['phone_number']
        employee.position = request.POST['position']
        employee.save()

        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('employee')  

    context = {
        'employee': employee,
    }
    return render(request, 'employee/update_employee_info.html', context)

@login_required
def dashboard(request):
    return render(request, 'dashboard/home.html')

@login_required
def manage_employees(request):
    employees = Employee.objects.all()  
    search_by = request.GET.get('search_by', 'id')
    query = request.GET.get('query', '')

    context = {
        'employees': employees,
        'search_by': search_by,
        'query': query,
    }
    return render(request, 'dashboard/manage_employees.html', context)

@login_required
def search_employee(request):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'name')  

    if not query:
        return redirect('manage_employees')
    if search_by == 'id':
        employees = Employee.objects.filter(id__icontains=query)
    elif search_by == 'name':
        employees = Employee.objects.filter(name__icontains=query)
    elif search_by == 'email':
        employees = Employee.objects.filter(email__icontains=query)
    elif search_by == 'position':
        employees = Employee.objects.filter(position__icontains=query)
    elif search_by == 'department':
        employees = Employee.objects.filter(department__icontains=query)
    elif search_by == 'status':
        employees = Employee.objects.filter(status__icontains=query)
    elif search_by == 'phone_number':
        employees = Employee.objects.filter(phone_number__icontains=query)
    else:
        employees = Employee.objects.none()  

    context = {
        'employees': employees,
        'query': query,
        'search_by': search_by,  
    }
    
    return render(request, 'dashboard/search_employee.html', context)

@login_required
def edit_employee(request, email):
    employee = get_object_or_404(Employee, email=email)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thành công")
            return redirect('manage_employees')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'dashboard/edit_employee.html', {'form': form})
    
@login_required
def delete_employee(request, email):
    try:
        employee = Employee.objects.get(email=email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy nhân viên với ID này.')
        return redirect('manage_employees')

    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Nhân viên đã được xóa thành công.')
        return redirect('manage_employees')

    return render(request, 'dashboard/delete_employee.html', {'employee': employee})

@login_required
def add_employee(request):
    if request.method == 'POST':
        # Lấy thông tin từ form
        username = request.POST.get('username')  
        password = request.POST.get('password') 
        name = request.POST.get('name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        id_card = request.POST.get('id_card')
        position = request.POST.get('position')
        department = request.POST.get('department')
        
        # Chuyển đổi ngày bắt đầu từ chuỗi sang đối tượng date
        start_date_str = request.POST.get('start_date')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'dashboard/add_employee.html', {'error': 'Ngày bắt đầu không hợp lệ'})

        # Kiểm tra và chuyển đổi lương thành số
        salary = request.POST.get('salary')
        try:
            salary = float(salary)
        except ValueError:
            return render(request, 'dashboard/add_employee.html', {'error': 'Lương phải là số hợp lệ'})

        # Lấy thông tin hợp đồng
        contract_type = request.POST.get('contract_type')
        status = request.POST.get('status')

        # Kiểm tra các trường bắt buộc
        if not all([username, password, name, birth_date, gender, address, phone_number, email, id_card, position, department, contract_type, status]):
            return render(request, 'dashboard/add_employee.html', {'error': 'Vui lòng điền đầy đủ thông tin'})

        # Tạo người dùng
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_employee=True  
        )

        # Tạo nhân viên
        employee = Employee.objects.create(
            user=user,
            name=name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            phone_number=phone_number,
            email=email,
            id_card=id_card,
            position=position,
            department=department,
            start_date=start_date,
            salary=salary,
            contract_type=contract_type,
            status=status
        )
        
        
        contract_end_date = start_date.replace(year=start_date.year + 1)  # Tính ngày kết thúc hợp đồng (1 năm)
        Contract.objects.create(
            employee=employee,
            contract_type=contract_type,
            status=status,  
            start_date=start_date,
            end_date=contract_end_date  
        )
        
        return redirect('manage_employees')  

    return render(request, 'dashboard/add_employee.html')


@login_required
def detail_employee(request, email):
    employee = get_object_or_404(Employee, email=email)
    return render(request, 'dashboard/detail_employee.html', {'employee': employee})

# @login_required
# def manage_salary(request):
#     employees = Employee.objects.all()
#     month = request.GET.get('month', now().month)
#     year = request.GET.get('year', now().year)

#     # Tính tổng lương bao gồm giờ làm việc thực tế
#     for employee in employees:
#         employee.total_salary = employee.calculate_monthly_salary(month, year)

#     context = {
#         'employees': employees,
#         'month': month,
#         'year': year,
#     }
#     return render(request, 'dashboard/manage_salary.html', context)

# @login_required
# def manage_salary(request):
#     # Lấy tháng và năm từ query hoặc dùng tháng hiện tại
#     month = int(request.GET.get('month', datetime.now().month))
#     year = int(request.GET.get('year', datetime.now().year))

#     # Lấy danh sách nhân viên và tính lương
#     employees = Employee.objects.all()
#     salary_details = []

#     for employee in employees:
#         salary = employee.calculate_salary(month, year)
#         salary_details.append({
#             'employee': employee,
#             'base_salary': salary['base_salary'],
#             'penalty': salary['penalty'],
#             'gross_salary': salary['gross_salary'],
#             'net_salary': salary['net_salary']
#         })

#     context = {
#         'salary_details': salary_details,
#         'month': month,
#         'year': year
#     }
#     return render(request, 'dashboard/manage_salary.html', context)

@login_required
def manage_salary(request):
    # Lấy tháng và năm từ query hoặc dùng tháng hiện tại
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # Lấy danh sách nhân viên và tính lương
    employees = Employee.objects.all()
    salary_details = []

    for employee in employees:
        salary = employee.calculate_salary_and_save(month, year)
        salary_details.append({
            'employee': employee,
            'base_salary': salary['base_salary'],
            'actual_days': salary['actual_days'],
            'hours_worked': salary['hours_worked'],
            'late_penalty': salary['late_penalty'],
            'gross_salary': salary['gross_salary'],
            'net_salary_after_tax': salary['net_salary_after_tax']
        })

    context = {
        'salary_details': salary_details,
        'month': month,
        'year': year
    }
    return render(request, 'dashboard/manage_salary.html', context)

@login_required
def search_salary_employee(request):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'name') 

    if not query:
        return redirect('manage_salary')

    
    if search_by == 'id':
        employees = Employee.objects.filter(id__icontains=query)
    elif search_by == 'name':
        employees = Employee.objects.filter(name__icontains=query)
    elif search_by == 'email':
        employees = Employee.objects.filter(email__icontains=query)
    elif search_by == 'position':
        employees = Employee.objects.filter(position__icontains=query)
    elif search_by == 'department':
        employees = Employee.objects.filter(department__icontains=query)
    else:
        employees = Employee.objects.none()  

    context = {
        'employees': employees,
        'query': query,
        'search_by': search_by,  \
    }
    
    return render(request, 'dashboard/search_salary_employee.html', context)


@login_required
def update_salary(request, email):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, email= email)
        new_salary = request.POST.get('bonus')
        if new_salary:
            employee.salary = new_salary
            employee.save()
        return redirect('manage_salary')
    

@login_required
def update_bonus(request, email):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, email= email)
        new_bonus = request.POST.get('bonus')
        if new_bonus:
            employee.bonus = new_bonus
            employee.save()
        return redirect('manage_salary')
    
    
    
    
    
@login_required
def contract(request):
    contracts = Contract.objects.all()  
    search_by = request.GET.get('search_by', 'id')
    query = request.GET.get('query', '')

    context = {
        'contracts': contracts,
        'search_by': search_by,
        'query': query,
    }
    return render(request, 'dashboard/contract.html', context)



@login_required
def search_contract(request):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'name') 

    if not query:
        return redirect('contract')

    if search_by == 'id':
        contracts = Contract.objects.filter(employee__id__icontains=query)
    elif search_by == 'name':
        contracts = Contract.objects.filter(employee__name__icontains=query)
    elif search_by == 'email':
        contracts = Contract.objects.filter(employee__email__icontains=query)
    elif search_by == 'position':
        contracts = Contract.objects.filter(employee__position__icontains=query)
    elif search_by == 'department':
        contracts = Contract.objects.filter(employee__department__icontains=query)
    elif search_by == 'status':
        contracts = Contract.objects.filter(status__icontains=query)
    else:
        contracts = Contract.objects.none()

    context = {
        'contracts': contracts,  
        'query': query,
        'search_by': search_by,
    }
    
    return render(request, 'dashboard/search_contract.html', context)



@login_required
def extend_contract(request, email):
    
    return render(request, 'extend_contract.html', {'email': email})


@login_required
def handlework(request):
    pending_contracts = Contract.objects.filter(renewal_pending = True)
    return render(request, 'dashboard/handlework.html', {'pending_contracts':pending_contracts})


@login_required
def approve_renewal(request, email):
    # Lấy thông tin nhân viên và hợp đồng
    employee = get_object_or_404(Employee, email=email)
    contract = get_object_or_404(Contract, employee=employee, renewal_pending=True)

    # Kiểm tra nếu hợp đồng đã yêu cầu gia hạn
    if contract.renewal_pending:
        renewal_request_date = contract.renewal_request_date

        # Kiểm tra nếu ngày yêu cầu gia hạn không có giá trị hợp lệ
        if not renewal_request_date:
            messages.error(request, "Ngày yêu cầu gia hạn không hợp lệ.")
            return redirect('handlework')  # Redirect về trang quản lý hợp đồng

        # Cập nhật thông tin hợp đồng sau khi admin phê duyệt gia hạn
        contract.renewal_pending = False  # Đánh dấu hợp đồng đã được phê duyệt
        contract.start_date = renewal_request_date  # Đặt ngày bắt đầu hợp đồng mới

        # Tính ngày kết thúc mới (thêm 1 năm vào start_date)
        contract.end_date = contract.start_date.replace(year=contract.start_date.year + 1)

        contract.save()  # Lưu các thay đổi vào database

        messages.success(request, "Yêu cầu gia hạn hợp đồng đã được phê duyệt.")
    else:
        messages.error(request, "Không có yêu cầu gia hạn nào chờ xử lý.")

    return redirect('handlework')  # Redirect lại trang xử lý hợp đồng

@login_required
def reject_renewal(request, email):
    # Tìm kiếm nhân viên
    employee = get_object_or_404(Employee, email=email)
    
    # Tìm kiếm hợp đồng cần gia hạn
    try:
        contract = get_object_or_404(Contract, employee=employee, renewal_pending=True)
    except Exception:
        messages.error(request, "Không tìm thấy hợp đồng cần gia hạn.")
        return redirect('handlework')

    # Đánh dấu yêu cầu gia hạn đã bị từ chối
    contract.renewal_pending = False
    contract.save()

    messages.success(request, "Yêu cầu gia hạn hợp đồng đã bị từ chối.")
    return redirect('handlework')


# @login_required
# def task(request):
#     tasks = Task.objects.all()
#     return render(request, 'dashboard/task.html', {'tasks': tasks})

@login_required
def task(request):
    # Truy vấn tất cả nhiệm vụ cùng thông tin nhân viên được gán
    tasks = Task.objects.select_related('assigned_to').all()
    
    # Truyền dữ liệu tới template
    return render(request, 'dashboard/task.html', {'tasks': tasks})

@login_required
def add_task(request):
    employees = Employee.objects.all()  
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_email = request.POST.get('assigned_to') 
        start_date = timezone.now().date()
        due_date = request.POST.get('due_date')

        # Tìm nhân viên được giao
        assigned_to = Employee.objects.get(email=assigned_to_email)

        # Tạo nhiệm vụ mới
        Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=request.user,
            start_date=start_date,
            due_date=due_date,
        )
        messages.success(request, "Thêm nhiệm vụ thành công")
        return redirect('task') 

    return render(request, 'dashboard/add_task.html', {'employees': employees})



#Employee


@login_required
def employee(request):
    employee = get_object_or_404(Employee, user=request.user)  
    return render(request, 'employee/home.html', {'employee': employee})


@login_required
def info_employee(request, email):
    employee = get_object_or_404(Employee, email=email)
    return render(request, 'employee/info_employee.html', {'employee': employee})


@login_required
def edit_info_employee(request, email):
    employee = get_object_or_404(Employee, email=email)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thành công.')
            return redirect('info_employee', email=email)  
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employee/edit_info_employee.html', {'form': form, 'employee': employee})

@login_required
def salary_employee(request, email):
    employee = get_object_or_404(Employee, email=email)
    employee.total_income = employee.salary + (employee.bonus if employee.bonus else 0)
    return render(request, 'employee/salary_employee.html', {'employee': employee})



@login_required
def contract_employee(request, email):
    employee = get_object_or_404(Employee, email=email)
    contracts = Contract.objects.filter(employee=employee).order_by('-start_date')  # Sắp xếp theo ngày bắt đầu

    context = {
        'employee': employee,
        'contracts': contracts,
        'now': now(),  
    }
    return render(request, 'employee/contract_employee.html', context)

@login_required
def extend_contract_employee(request, email):
    # Lấy thông tin nhân viên và hợp đồng
    employee = get_object_or_404(Employee, email=email)
    contract = get_object_or_404(Contract, employee=employee)

    if request.method == "POST":
        # Lấy ngày yêu cầu gia hạn từ form
        renewal_request_date = request.POST.get('renewal_request_date')

        # Kiểm tra nếu không có giá trị cho renewal_request_date
        if not renewal_request_date:
            messages.error(request, "Ngày yêu cầu gia hạn không được để trống.")
            return redirect('contract_employee', email=employee.email)

        try:
            # Chuyển đổi sang định dạng ngày
            renewal_request_date = datetime.strptime(renewal_request_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Định dạng ngày yêu cầu gia hạn không hợp lệ.")
            return redirect('contract_employee', email=employee.email)

        # Cập nhật trạng thái gia hạn
        contract.renewal_pending = True
        contract.renewal_request_date = renewal_request_date

        # Nếu không có start_date, đặt start_date là renewal_request_date
        if not contract.start_date:
            contract.start_date = renewal_request_date

        # Tính ngày kết thúc mới (thêm 1 năm vào start_date)
        contract.end_date = contract.start_date.replace(year=contract.start_date.year + 1)
        contract.save()

        messages.success(request, "Yêu cầu gia hạn đã được gửi và cập nhật thành công.")
        return redirect('contract_employee', email=employee.email)

    # Trả dữ liệu đến template
    return render(request, 'employee/extend_contract.html', {
        'contract': contract,
        'employee': employee,
        'today': date.today(),  # Truyền ngày hiện tại
    })
    
@login_required
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        # Xử lý logic chỉnh sửa hợp đồng ở đây
        contract.contract_type = request.POST.get('contract_type')
        contract.start_date = request.POST.get('start_date')
        contract.end_date = request.POST.get('end_date')
        contract.save()
        messages.success(request, "Hợp đồng đã được cập nhật.")
        return redirect('contract_list')  # Redirect về danh sách hợp đồng

    return render(request, 'dashboard/edit_contract.html', {'contract': contract})

@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'dashboard/view_contract.html', {'contract': contract})
    
    
@login_required
def task_employee(request, email):
    employee = get_object_or_404(Employee, email = email)
    tasks = Task.objects.filter(assigned_to=employee).order_by('due_date')
    
    return render(request, 'employee/task_employee.html', 
                  {'employee': employee,
                  'tasks': tasks } )

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # Lấy nhiệm vụ theo ID
    employee = task.assigned_to  # Lấy nhân viên được giao nhiệm vụ

    if request.method == 'POST':
        new_status = request.POST.get('status')  # Lấy trạng thái mới từ form
        if new_status in dict(Task.STATUS_CHOICES):  # Kiểm tra trạng thái hợp lệ
            task.status = new_status

            # Nếu trạng thái là "Completed", cập nhật ngày hoàn thành (end_date)
            if new_status == 'Completed':
                task.end_date = now().date()  # Ngày hoàn thành là ngày hiện tại
            else:
                task.end_date = None  # Nếu không phải "Completed", xóa ngày hoàn thành

            task.save()  # Lưu thay đổi vào database
            messages.success(request, "Cập nhật trạng thái thành công")
            return redirect('task_employee', email=employee.email)

    return render(request, 'employee/update_task_status.html', {
        'task': task,
        'status_choices': Task.STATUS_CHOICES,
        'employee': employee,
    })

@login_required
def task(request):
    query = request.GET.get('query', '')  # Lấy từ khóa tìm kiếm
    search_by = request.GET.get('search_by', 'id')  # Lấy tiêu chí tìm kiếm, mặc định là 'id'
    status_filter = request.GET.get('status', '')  # Lấy trạng thái được chọn (nếu có)

    # Truy vấn các nhiệm vụ
    tasks = Task.objects.all()

    if search_by == 'id':
        tasks = tasks.filter(id__icontains=query)
    elif search_by == 'title':
        tasks = tasks.filter(title__icontains=query)
    elif search_by == 'description':
        tasks = tasks.filter(description__icontains=query)
    elif search_by == 'assigned_to':
        tasks = tasks.filter(assigned_to__name__icontains=query)

    # Nếu có trạng thái được chọn, lọc thêm theo trạng thái
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks,
        'query': query,
        'search_by': search_by,
        'status_filter': status_filter,
        'status_choices': Task.STATUS_CHOICES,  # Truyền danh sách trạng thái vào context
    }

    return render(request, 'dashboard/task.html', context)


@login_required
def attendance(request):
    # Lấy giá trị tháng và năm từ query
    month_year = request.GET.get('month', f"{now().year}-{now().month}")  # Mặc định là tháng hiện tại
    try:
        # Chuyển đổi chuỗi "YYYY-MM" thành datetime
        selected_date = datetime.strptime(month_year, "%Y-%m")
        selected_month = selected_date.month
        selected_year = selected_date.year
    except ValueError:
        # Nếu giá trị không hợp lệ, sử dụng tháng và năm hiện tại
        selected_month = now().month
        selected_year = now().year

    # Lọc các bản ghi chấm công theo tháng và năm
    attendances = Attendance.objects.filter(date__month=selected_month, date__year=selected_year)

    context = {
        'attendances': attendances,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_year': month_year,  # Truyền lại giá trị để hiển thị trên giao diện
    }
    return render(request, 'dashboard/attendance.html', context)

@login_required
def employee_attendance(request):
    # Tìm Employee liên kết với User
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        return render(request, 'employee/attendance.html', {
            'error': 'Không tìm thấy thông tin nhân viên liên kết với tài khoản của bạn.'
        })

    # Tìm hoặc tạo bản ghi Attendance cho hôm nay
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=now().date())

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'check_in' and not attendance.check_in:
            attendance.check_in = now().time()
            messages.success(request, "Check-in thành công!")
        elif action == 'check_out' and not attendance.check_out:
            attendance.check_out = now().time()
            messages.success(request, "Check-out thành công!")
        attendance.save()
        return redirect('employee_attendance')

    return render(request, 'employee/attendance.html', {
        'attendance': attendance,
        'employee': employee,  # Truyền employee vào context
    })


# @login_required
# def report_statistics(request):
#     # Lấy tháng và năm từ query hoặc mặc định là tháng/năm hiện tại
#     month = int(request.GET.get('month', now().month))
#     year = int(request.GET.get('year', now().year))

#     # Danh sách nhân viên
#     employees = Employee.objects.all()

#     # Chuẩn bị dữ liệu thống kê
#     statistics = []

#     for employee in employees:
#         # Số lượng task hoàn thành trong tháng
#         tasks_completed = Task.objects.filter(
#             assigned_to=employee,
#             status='Completed',
#             start_date__month=month,
#             start_date__year=year
#         ).count()

#         # Số lượng task trễ của nhân viên
#         delayed_tasks = Task.objects.filter(
#             assigned_to=employee,
#             status='Delayed',
#             start_date__month=month,
#             start_date__year=year
#         ).count()

#         # Số lần đi muộn trong tháng
#         late_count = Attendance.objects.filter(
#             employee=employee,
#             status='Trễ giờ',
#             date__month=month,
#             date__year=year
#         ).count()

#         # Thêm thông tin vào danh sách thống kê
#         statistics.append({
#             'employee': employee,
#             'tasks_completed': tasks_completed,
#             'late_count': late_count,
#             'delayed_tasks': delayed_tasks,

#         })

#     context = {
#         'statistics': statistics,
#         'month': month,
#         'year': year,
#     }
#     return render(request, 'dashboard/report_statistics.html', context)

# @login_required
# def report_statistics(request):
#     # Lấy tháng và năm từ query hoặc mặc định là tháng/năm hiện tại
#     month = int(request.GET.get('month', now().month))
#     year = int(request.GET.get('year', now().year))

#     # Danh sách nhân viên
#     employees = Employee.objects.all()

#     # Chuẩn bị dữ liệu thống kê
#     statistics = []
#     labels = []
#     values = []

#     for employee in employees:
#         # Số lượng task hoàn thành trong tháng
#         tasks_completed = Task.objects.filter(
#             assigned_to=employee,
#             status='Completed',
#             start_date__month=month,
#             start_date__year=year
#         ).count()

#         # Số lượng task trễ của nhân viên
#         delayed_tasks = Task.objects.filter(
#             assigned_to=employee,
#             status='Delayed',
#             start_date__month=month,
#             start_date__year=year
#         ).count()

#         # Tổng số task
#         total_tasks = tasks_completed + delayed_tasks

#         if total_tasks > 0:
#             # Ghi dữ liệu vào danh sách
#             statistics.append({
#                 'employee': employee,
#                 'tasks_completed': tasks_completed,
#                 'delayed_tasks': delayed_tasks,
#                 'total_tasks': total_tasks,
#             })

#             # Chuẩn bị dữ liệu biểu đồ
#             labels.append(f"{employee.name} (Trễ: {delayed_tasks}, Hoàn: {tasks_completed})")
#             values.append([tasks_completed, delayed_tasks])

#     # Vẽ biểu đồ cho tất cả nhân viên
#     fig, ax = plt.subplots(figsize=(8, 6))
#     for i, employee_values in enumerate(values):
#         ax.pie(
#             employee_values,
#             labels=['Hoàn thành', 'Trễ'],
#             autopct='%1.1f%%',
#             startangle=90,
#             radius=1 - i * 0.2,  # Biểu đồ lồng vào nhau
#         )

#     ax.set_title(f'Tỉ lệ Task Hoàn Thành và Trễ Hẹn ({month}/{year})')

#     # Chuyển đổi biểu đồ thành base64 để hiển thị trên web
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()

#     context = {
#         'statistics': statistics,
#         'chart_base64': chart_base64,
#         'month': month,
#         'year': year,
#     }
#     return render(request, 'dashboard/report_statistics.html', context)

@login_required
def report_statistics(request):
    # Lấy tháng và năm từ query hoặc mặc định là tháng/năm hiện tại
    month = int(request.GET.get('month', now().month))
    year = int(request.GET.get('year', now().year))

    # Danh sách nhân viên
    employees = Employee.objects.all()

    # Thống kê tổng task hoàn thành và trễ
    total_completed_tasks = Task.objects.filter(
        status='Completed',
        start_date__month=month,
        start_date__year=year
    ).count()

    total_delayed_tasks = Task.objects.filter(
        status='Delayed',
        start_date__month=month,
        start_date__year=year
    ).count()

    # Tổng số task
    total_tasks = total_completed_tasks + total_delayed_tasks

    # Tạo biểu đồ nếu có dữ liệu
    if total_tasks > 0:
        labels = ['Hoàn thành', 'Trễ']
        sizes = [total_completed_tasks, total_delayed_tasks]
        colors = ['#4CAF50', '#FF5722']  # Màu sắc cho biểu đồ
        explode = (0.1, 0)  # Làm nổi phần đầu tiên

        fig, ax = plt.subplots()
        ax.pie(
            sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90
        )
        ax.axis('equal')  # Đảm bảo biểu đồ là hình tròn
        plt.title(f'Tỉ lệ Task Hoàn Thành và Trễ Hẹn ({month}/{year})')

        # Chuyển biểu đồ thành base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
    else:
        chart_base64 = None  # Nếu không có dữ liệu, không tạo biểu đồ

    context = {
        'total_completed_tasks': total_completed_tasks,
        'total_delayed_tasks': total_delayed_tasks,
        'total_tasks': total_tasks,
        'chart_base64': chart_base64,
        'month': month,
        'year': year,
    }
    return render(request, 'dashboard/report_statistics.html', context)