from django.urls import path
from . import views
from .views import report_statistics


urlpatterns = [
    path('', views.login_form, name='home'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('update_employee_info/', views.update_employee_info, name='update_employee_info'),
    
    
#Admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage_employees', views.manage_employees, name='manage_employees'),
    path('search/', views.search_employee, name='search_employee'),
    path('edit/<str:email>/', views.edit_employee, name='edit_employee'),
    path('delete/<str:email>/', views.delete_employee, name='delete_employee'),
    path('add/', views.add_employee, name='add_employee'),
    path('employee/<str:email>/', views.detail_employee, name='detail_employee'),
    
    path('manage_salary/', views.manage_salary, name = 'manage_salary'),
    path('update_salary/<str:email>/', views.update_salary, name='update_salary'),
    path('update_bonus/<str:email>/', views.update_bonus, name='update_bonus'),
    path('search_salary_employee/', views.search_salary_employee, name ='search_salary_employee'),
    
    path('contract/', views.contract, name = 'contract'),
    path('search_contract/', views.search_contract, name = 'search_contract'),
    path('extend_contract/<str:email>/', views.extend_contract, name='extend_contract'),
    
    path('handlework/', views.handlework, name ='handlework'),
    path('approve_renewal/<str:email>/', views.approve_renewal, name='approve_renewal'),
    path('reject_renewal/<str:email>/', views.reject_renewal, name='reject_renewal'),
    path('contract/<int:contract_id>/edit/', views.edit_contract, name='edit_contract'),
    path('contract/<int:contract_id>/', views.view_contract, name='view_contract'),
    
    
    path('task/', views.task, name = 'task'),
    path('add_task/', views.add_task, name = 'add_task'),

    path('attendance/', views.attendance, name='attendance'),

    path('report_statistics/', report_statistics, name='report_statistics'),


    
    
#Employee
    path('employee/', views.employee, name ='employee'),
    path('info_employee/<str:email>/', views.info_employee, name='info_employee'),
    path('edit_info_employee/<str:email>/', views.edit_info_employee, name='edit_info_employee'),
    path('salary_employee/<str:email>/', views.salary_employee, name ='salary_employee'), 
    path('contract_employee/<str:email>/', views.contract_employee, name ='contract_employee'),
    path('extend_contract_employee/<str:email>/', views.extend_contract_employee, name = 'extend_contract_employee'),
    path('task_employee/<str:email>/', views.task_employee, name = 'task_employee'),
    path('task/update/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('employee_attendance/', views.employee_attendance, name='employee_attendance'),
]





