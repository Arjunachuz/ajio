from django import forms
from .models import User,UserProfile
from orders.models import Orders,Models

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password doesn't match!")   

class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Start Typing...','required':'required'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'btn btn-primary'}))
    cover_photos = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'btn btn-primary'}))
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    longititude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = UserProfile     
        fields = ['profile_picture','cover_photos','address','country','state','city','pin_code','latitude','longititude',]       

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['vehicle','type', 'model', 'defect', 'description','u_phone_number','latitude','longitude']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = Models.objects.none()

        if 'vehicle' in self.data:
            try:
                vehicle_id = int(self.data.get('vehicle'))
                self.fields['model'].queryset = Models.objects.filter(vehicle_id=vehicle_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['model'].queryset = self.instance.vehicle.model_set.order_by('name')        

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']            
