from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User,UserProfile
from django.contrib import messages,auth
from .utils import detect_user
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
# Create your views here.

# Restrict vendor from user's pages
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied    

# Restrict user from vendor's pages
def check_role_user(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied    

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,'You already logged in !')
        return redirect('userHome')
    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Registration Sucessful')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)    
    else:
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request,'You already logged in !')
        return redirect('vendorHome')
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Registration Sucessful')
            return redirect('registerVendor')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, 'accounts/registerVendor.html', context)

def login(request):
    # if request.user.is_authenticated:
    #     messages.warning(request,'You already logged in !')
    #     return redirect('myAccount')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are logged in')
            return redirect('myAccount')  
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')    
    return render(request, 'accounts/login.html') 


def logout(request):
    auth.logout(request)
    messages.info(request,'You are logged out')
    return redirect('login')

@login_required(login_url ='login')
def myAccount(request):
    user = request.user
    redirectUrl = detect_user(user)
    return redirect(redirectUrl)

@login_required(login_url ='login')
@user_passes_test(check_role_user)
def userHome(request):
        return render(request,'accounts/userHome.html')

@login_required(login_url ='login')
@user_passes_test(check_role_vendor)
def vendorHome(request):
        return render(request,'accounts/vendorHome.html')




