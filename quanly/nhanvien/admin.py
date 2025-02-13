from django.contrib import admin
from .models import Attendance  # Đảm bảo model Attendance được import chính xác

# Register your models here.
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'hours_worked')  # Các cột hiển thị
    list_filter = ('date', 'employee')  # Bộ lọc
    search_fields = ('employee__name', 'date')  # Tìm kiếm theo tên và ngày