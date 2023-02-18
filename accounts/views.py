from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserForm,OrderForm,UserProfileForm, UserInfoForm
from vendor.forms import VendorForm
from .models import User,UserProfile
from django.contrib import messages,auth
from .utils import detect_user,send_verification_email,send_service_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from orders.models import Orders,Order_images,Models
from django.db.models import Q
import datetime

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
    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()

            # send verification email
            mail_subject = 'Please activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request,user, mail_subject, email_template) 

            messages.success(request, 'Registration Sucessful')
            messages.success(request, 'Check your E-mail')
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
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR
            print(user.role)
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification email
            mail_subject = 'Please activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request,user, mail_subject, email_template) 

            messages.success(request, 'Registration Sucessful')
            messages.success(request, 'Check your E-mail')
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

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congrajulation ! Your account activated.')  
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link.')         
        return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'You already logged in !')
        return redirect('myAccount')
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
    return render(request, 'login.html') 


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
    user = request.user
    orders = Orders.objects.filter(user=user,is_seen=False)
    vendors = Vendor.objects.all()[:8]
    print(user)
    return render(request,'home.html',{'orders':orders,'vendors':vendors})

@login_required(login_url ='login')
@user_passes_test(check_role_vendor)
def vendorHome(request):
    print(request.user)
    vendor_id = request.user.id
    print(vendor_id)
    vendor = Vendor.objects.get(user__id=vendor_id)
    orders = Orders.objects.filter(vendor=vendor,status='NEW')
    return render(request,'accounts/vendorHome.html',{'orders':orders})

@login_required(login_url ='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Orders.objects.filter(vendor=vendor).order_by('-created_at')
    recent_orders = orders[:5]
    
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        if i.price:
            current_month_revenue += int(i.price)    

    total_revenue = 0
    for i in orders:
        if i.price:
           total_revenue += int(i.price)

    context = {
        'recent_orders':recent_orders,
        'orders_count':orders.count(),
        'total_revenue':total_revenue,
        'current_month_revenue':current_month_revenue,
    }    

    return render(request,'accounts/vendor_dashboard.html', context)   

@login_required(login_url ='login')
def user_dashboard(request):
    orders = Orders.objects.filter(user=request.user).order_by('-created_at')
    recent_orders = orders[:5]
    context = {'orders':orders,
               'recent_orders':recent_orders,
               'orders_count':orders.count(),
              }
    return render(request,'accounts/user_dashboard.html',context)      

def my_orders(request):
    orders = Orders.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders':orders}
    return render(request, 'user/my_orders.html', context)     

def v_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Orders.objects.filter(vendor=vendor).order_by('-created_at')
    context = {'orders':orders}
    return render(request, 'vendor/my_orders.html', context)      

def my_orders_detail(request, order_id):
    order = Orders.objects.get(id=order_id)
    return render(request, 'user/my_orders_detail.html',{'order':order})   

def v_orders_detail(request, order_id):
    order = Orders.objects.get(id=order_id)
    return render(request, 'vendor/my_orders_detail.html',{'order':order})    

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgot_password')   

    return render(request, 'accounts/forgot_password.html')   

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid   
        messages.info(request, 'Please reset your password') 
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')    

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset Successfull')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

@login_required(login_url ='login')
def on_road(request):
    user = request.user
    print(user)
    vendors = Vendor.objects.filter(user__is_active=True)
    context = {'vendors':vendors}
    return render(request, 'accounts/on_road.html',context)    

def search(request):
    if  not 'address' in request.GET:
        return redirect('on_road')
    else:    
        address = request.GET['address']
        request.session['address'] = address
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        keyword = request.GET['keyword']

        vendors = Vendor.objects.filter(vendor_name__icontains=keyword,user__is_active=True)
        if latitude and longitude:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = Vendor.objects.filter(vendor_name__icontains=keyword,user__is_active=True,user_profile__location__distance_lte=(pnt, D(km=20))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
            for v in vendors:
                v.kms = round(v.distance.km, 1) 

        vendor_count = vendors.count()
        context = {
            'vendors':vendors,
            'vendor_count':vendor_count,
            'source_location':address,
            }

        return render(request, 'accounts/on_road.html',context) 

def search_current(request):
    print('yyyyyyyyyyyyyyyyyyyyyyyyy')
    if get_or_set_current_location(request) is not None:
        print('llllllllllllllllllllllllllllll')

        pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))   
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=20))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        print(vendors)    
        for v in vendors:
            v.kms = round(v.distance.km, 1) 
        return render(request, 'accounts/on_road.html',{'vendors':vendors}) 
    return redirect('on_road')       
   

def get_or_set_current_location(request):
    print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
    if "lat" in request.session:
        print('cccccccccccccccccccccccccccccccc')
        lat = request.session['lat']        
        lng = request.session['lng']
        return lng, lat 
    elif "lat" in request.GET:
        print('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
        lat = request.GET('lat')           
        lng = request.GET('lng')
        request.session['lat'] = lat           
        request.session['lng'] = lng  
        return lng, lat
    else:
        return None  

@login_required(login_url ='login')
def order(request,vendor_id):
    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
    user = request.user
    print(user)
    vendor = Vendor.objects.get(id=vendor_id)
    if request.method == 'POST':
        print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('inside request')
        form = OrderForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            print('form is valid')
            order = form.save(commit=False)
            order.user = user
            order.vendor = vendor
            order.service = 'ROAD'
            order.save()

            for image in images:
                order_images = Order_images.objects.create(
                    order = order,
                    images = image
                )
                order_images.save()
            return redirect('myAccount')    
            
        else:
            print(form.errors)

    form = OrderForm()
    return render(request, 'accounts/order.html',{'form':form,'vendor':vendor})

def service(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)  
    return render(request, 'accounts/service.html',{'vendor':vendor}) 

def home_service(request,vendor_id):
    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
    user = request.user
    print(user)
    vendor = Vendor.objects.get(id=vendor_id)
    if request.method == 'POST':
        print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('inside request')
        form = OrderForm(request.POST)
        images = request.FILES.getlist('images')
        date = request.POST.get('myDate')
        time = request.POST.get('myTime')
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',date)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',time)
        if form.is_valid():
            print('form is valid')
            order = form.save(commit=False)
            order.user = user
            order.vendor = vendor
            order.service = 'HOME'
            order.date = date
            order.time = time
            order.save()

            for image in images:
                order_images = Order_images.objects.create(
                    order = order,
                    images = image
                )
                order_images.save()
            return redirect('myAccount')    
            
        else:
            print(form.errors)

    form = OrderForm()
    return render(request, 'accounts/home_service.html',{'form':form,'vendor':vendor})

def load_models(request):
    vehicle_id = request.GET.get('vehicle_id')
    models = Models.objects.filter(vehicle_id=vehicle_id).all()
    print(models)
    return render(request, 'accounts/load_models.html',{'models':models})    

def order_detail(request,order_id):
    order = Orders.objects.get(id=order_id)
    images = Order_images.objects.filter(order=order)
    return render(request, 'accounts/order_detail.html',{'order':order,'images':images})

def accept(request,order_id):
    order = Orders.objects.get(id=order_id)
    user = order.user
    print(user)
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not order.date:
            eta = request.POST.get('eta')
            order.eta = eta
        order.v_phone_number = phone_number
        order.status = 'ACCEPTED'
        order.save()

        mail_subject = 'Your order has been Accepted.'
        email_template = 'accounts/emails/order_accepted_email.html'
        send_service_email(request,user, mail_subject, email_template,order_id) 

        return redirect('myAccount')
    return render(request, 'accounts/order_accept.html',{'order':order}) 

def order_bill(requset,order_id=None):
    user = requset.user
    vendor_id = user.id
    print(vendor_id)
    vendor = Vendor.objects.get(user__id=vendor_id)
    orders = Orders.objects.filter(Q(vendor=vendor,status='ACCEPTED') | Q(vendor=vendor,status='PENDING'))
    print(orders)
    if requset.method == 'POST':
        price = requset.POST.get('price')
        order = Orders.objects.get(id=order_id)
        order.price = price
        order.status = 'COMPLETED'
        order.save()
        return redirect('myAccount')
    return render(requset, 'accounts/order_bill.html',{'orders':orders})    

def decline(request,order_id):
    order = Orders.objects.get(id=order_id)
    user = order.user
    print(user)
    if request.method == 'POST':
        message = request.POST.get('message')
        order.msg = message
        order.status = 'DECLINED'
        order.save()

        mail_subject = 'Sorry the order has been Declined.'
        email_template = 'accounts/emails/order_declined_email.html'
        send_service_email(request,user, mail_subject, email_template,order_id) 

        return redirect('myAccount')

    return render(request, 'accounts/order_decline.html',{'order':order})    


def end_page(request, uidb64, order_id):
    print('ENDPAGEEEEEEEEEEEEEEEEEEEEEE')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print(uid)
        user = User._default_manager.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
            print('pppppppppppppppppppppppppp')
            order = Orders.objects.get(id=order_id) 
            print('kkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            print(order)
            print(order.status)
            if order.status:
                if order.status == 'ACCEPTED':
                    print('yesssss')
                    order.status = 'PENDING' 
                    order.is_seen = True
                    order.save()
                    print(order.status)    
                else:    
                    order.is_seen = True
                    order.save()    
                return render(request, 'accounts/end_page.html',{'order':order}) 
            else:
                return render(request, 'accounts/end_page.html')       
    return redirect('myAccount')  

@login_required(login_url='login')
def u_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('u_profile')
        else:
            print(profile_form.errors)    
            print(user_form.errors)    
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form':profile_form,
        'user_form': user_form,
        'profile':profile,

    }
    return render(request, 'user/profile.html', context)      

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(request, email=email, password=password, is_admin=True)
        if user is not None and user.is_admin:
            auth.login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'accounts/admin_login.html')    

def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_admin:

       return render(request, 'accounts/admin_dashboard.html') 
    return redirect('admin_login')          




