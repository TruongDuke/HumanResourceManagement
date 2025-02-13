from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from datetime import date, datetime
from django.utils.timezone import now
from datetime import time
from decimal import Decimal


class User(AbstractUser):
    email = models.EmailField(unique=True)  
    is_admin = models.BooleanField(default=False) 
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)  
    
    class Meta:
        swappable = 'AUTH_USER_MODEL' 
        
class Department(models.Model):
    ACCOUNTING = 'Kế toán'
    ADMINISTRATION = 'Hành chính'
    IT = 'IT'
    MARKETING = 'Marketing'

    DEPARTMENT_CHOICES = [
        (ACCOUNTING, 'Kế toán'),
        (ADMINISTRATION, 'Hành chính'),
        (IT, 'IT'),
        (MARKETING, 'Marketing'),
    ]

    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
        
class Employee(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    id_card = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100, choices=Department.DEPARTMENT_CHOICES)
    start_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=0)
    contract_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    bonus = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  
    hourly_rate = models.DecimalField(default=50000,max_digits=10, decimal_places=0)  # Lương theo giờ (giả sử 50K/giờ)
    late_penalty = models.DecimalField(max_digits=10, decimal_places=0, default=50000)  # Phạt mỗi lần đi muộn
    standard_days = models.IntegerField(default=22)  # Số công tiêu chuẩn (22 ngày/tháng)
    net_salary_after_tax = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)  # Lương thực nhận

    def __str__(self):
        return self.name

    def calculate_salary(self):
        return self.salary + self.bonus

    def get_all_info_employees(self):
        return f"ID: {self.id}, Name: {self.name}, Email: {self.email}, Position: {self.position}, Department: {self.department}, Phone_Number; {self.phone_number}"
        
    def calculate_monthly_salary(self, month, year):
        attendances = self.attendances.filter(date__month=month, date__year=year)
        total_hours = sum([attendance.hours_worked for attendance in attendances])
        # Chuyển đổi total_hours sang Decimal
        return self.salary + Decimal(total_hours) * self.hourly_rate

    def calculate_salary_and_save(self, month, year):
    # Lấy danh sách chấm công
        attendances = self.attendances.filter(date__month=month, date__year=year)

    # Số công thực tế
        total_days = attendances.count()

    # Tính tổng số lần đi muộn
        late_count = attendances.filter(status='Trễ giờ').count()

    # Tính phạt đi muộn
        total_penalty = Decimal(late_count) * self.late_penalty

    # Tổng số giờ làm việc
        total_hours = sum([attendance.hours_worked for attendance in attendances])

    # Lương cơ bản
        gross_salary = self.salary

    # Cộng thêm lương giờ làm việc
        gross_salary += Decimal(total_hours) * self.hourly_rate

    # Trừ phạt đi muộn
        net_salary = gross_salary - total_penalty

    # Trừ thuế 10%
        net_salary_after_tax = net_salary * Decimal(1.0)

    # Cập nhật lương thực nhận vào cơ sở dữ liệu
        self.net_salary_after_tax = net_salary_after_tax
        self.save()

    # Trả về chi tiết lương
        return {
            'base_salary': self.salary,
            'actual_days': total_days,
            'hours_worked': total_hours,
            'late_penalty': total_penalty,
            'gross_salary': gross_salary,
            'net_salary_after_tax': net_salary_after_tax
        }


class Contract(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    contract_type = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('Active', 'Còn hạn'),
        ('Expired', 'Hết hạn'),
        ('Renewed', 'Đã gia hạn'),
        ('Terminated', 'Đã kết thúc')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    start_date = models.DateField(default=timezone.now)  
    end_date = models.DateField(null=True, blank=True)
    
    renewal_pending = models.BooleanField(default=False) 
    renewal_request_date = models.DateTimeField(null=True, blank=True) 
    approval_status = models.CharField(max_length=50, null=True, blank=True)  
    approval_date = models.DateTimeField(null=True, blank=True) 
    
    def __str__(self):
        return f"Hợp đồng của {self.employee.name}"
    
    @property
    def is_active(self):
        if self.end_date and self.end_date < date.today():
            return False
        return True
    
    
    def get_contract_details(self):
        status_display = {
            'Active': 'Còn hạn',
            'Expired': 'Hết hạn',
            'Renewed': 'Đã gia hạn',
            'Terminated': 'Đã kết thúc',
        }.get(self.status, 'Không xác định')
        return {
            "id": self.employee.id,
            "name": self.employee.name,
            "position": self.employee.position,
            "department": self.employee.department,
            "contract_type": self.contract_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": status_display,
        }
        

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Chưa bắt đầu'),
        ('In Progress', 'Đang thực hiện'),
        ('Completed', 'Đã hoàn thành'),
        ('Delayed', 'Bị trì hoãn'),
    ]

    title = models.CharField(max_length=255)  
    description = models.TextField()  
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')  # Giao cho nhân viên
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')  # Người giao việc (Admin)
    start_date = models.DateField(default=timezone.now)  # Ngày bắt đầu
    end_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()  # Ngày hoàn thành
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # Trạng thái
    progress = models.PositiveIntegerField(default=0)  # Tiến độ (%)

    def __str__(self):
        return f"Task: {self.title} - {self.get_status_display()}"
    
    def get_status_display(self):
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status)

    def is_overdue(self):
        """Kiểm tra xem công việc có bị quá hạn không."""
        return self.due_date < timezone.now().date() and self.status != 'Completed'

    def update_progress(self, new_progress):
        """Cập nhật tiến độ và trạng thái công việc."""
        if 0 <= new_progress <= 100:
            self.progress = new_progress
            if new_progress == 100:
                self.status = 'Completed'
            elif new_progress > 0:
                self.status = 'In Progress'
            self.save()
        else:
            raise ValueError("Tiến độ phải nằm trong khoảng từ 0 đến 100.")

class Attendance(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    hours_worked = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='Đúng giờ')  # Trạng thái: Đúng giờ hoặc Trễ giờ

    def calculate_status(self):
        """Tính trạng thái dựa trên giờ check-in."""
        work_start_time = time(9, 0)  # Giả sử giờ bắt đầu làm việc là 9:00 sáng
        if self.check_in and self.check_in > work_start_time:
            self.status = 'Trễ giờ'
        else:
            self.status = 'Đúng giờ'

    def calculate_hours(self):
        """Tính số giờ làm việc dựa trên check-in và check-out."""
        if self.check_in and self.check_out:
            delta = datetime.combine(self.date, self.check_out) - datetime.combine(self.date, self.check_in)
            self.hours_worked = round(delta.total_seconds() / 3600.0, 2)

    def save(self, *args, **kwargs):
        self.calculate_status()
        self.calculate_hours()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

