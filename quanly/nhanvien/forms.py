from django import forms
from .models import Employee
from .models import Contract

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Tên đăng nhập")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee  
        fields = ['name', 'birth_date', 'gender', 'address', 'phone_number', 'id_card', 'position', 'department', 'start_date', 'salary', 'contract_type', 'status', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        
class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['employee', 'contract_type', 'start_date', 'end_date', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].disabled = True