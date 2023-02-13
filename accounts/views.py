from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import UserForm,OrderForm
from vendor.forms import VendorForm
from .models import User,UserProfile
from django.contrib import messages,auth
from .utils import detect_user,send_verification_email
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
    user = request.user
    orders = Orders.objects.filter(Q(user=user,status='ACCEPTED',is_seen=False) | Q(user=user,status='DECLINED',is_seen=False))
    print(user)
    return render(request,'accounts/userHome.html',{'orders':orders})

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
    return render(request,'accounts/vendor_dashboard.html')   

@login_required(login_url ='login')
def user_dashboard(request):
    return render(request,'accounts/user_dashboard.html')        

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
        eta = request.POST.get('eta')

        order.v_phone_number = phone_number
        order.eta = eta
        order.status = 'ACCEPTED'
        order.save()

        mail_subject = 'Your order has been Accepted.'
        email_template = 'accounts/emails/order_accepted_email.html'
        send_verification_email(request,user, mail_subject, email_template) 

        return redirect('order_bill',order_id=order_id)
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
        send_verification_email(request,user, mail_subject, email_template) 

        return redirect('myAccount')

    return render(request, 'accounts/order_decline.html',{'order':order})    


def end_page(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print(uid)
        user = User._default_manager.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
            order = Orders.objects.filter(Q(user=user,status='ACCEPTED') | Q(user=user,status='DECLINED')).first()  
            # order2 = Orders.objects.filter(user=user,status='DECLINED').first()  
            print('kkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            print(order)
            if order.status == 'ACCEPTED':
                order.status = 'PENDING' 
                order.is_seen = True
                order.save()
                print(order.status)    
                return render(request, 'accounts/end_page.html',{'order':order}) 
            order.is_seen = True
            order.save()    
            return render(request, 'accounts/end_page.html',{'order':order}) 
            # elif order2:
            #     return render(request, 'accounts/end_page.html',{'order2':order2})    
    return redirect('myAccount')        




