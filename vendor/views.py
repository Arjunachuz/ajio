from django.shortcuts import render,get_object_or_404, redirect,HttpResponse
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from vendor.models import Vendor,OpeningHour
from vendor.forms import VendorForm,OpeningHourForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_vendor
from django.db import IntegrityError
from django.http import JsonResponse


# Create your views here.
def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url ='login')
@user_passes_test(check_role_vendor)
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request,'Settings Updated')
            return redirect('vprofile')
        else:
            print('error:',profile_form.errors)    
            print('error:',vendor_form.errors)   
    else:       
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form':profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor
    }
    return render(request,'vendor/profile.html', context)

def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    print(opening_hours)
    form = OpeningHourForm()
    context = {
        'form':form,
        'opening_hours':opening_hours,
    }
    return render(request, 'vendor/opening_hours.html',context)     

def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status':'success','id':hour.id, 'day':day.get_day_display(), 'is_closed':'Closed'}
                    else:
                        response = {'status':'success','id':hour.id, 'day':day.get_day_display(), 'from_hour':hour.from_hour, 'to_hour':hour.to_hour}   
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status':'failed', 'message': from_hour+'-'+to_hour+'  already existfor this day !'}
                return JsonResponse(response)

        else:
            HttpResponse('Invalid Request')

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status':'success','id':pk})
