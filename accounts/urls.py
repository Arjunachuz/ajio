from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.myAccount),
    path('registerUser/',views.registerUser, name='registerUser'),
    path('registerVendor/',views.registerVendor, name='registerVendor'),
    
    path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),

    path('activate/<uidb64>/<token>/',views.activate, name='activate'),

    path('forgot_password/',views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/',views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/',views.reset_password, name='reset_password'),

    path('myAccount/',views.myAccount, name='myAccount'),
    path('userHome/',views.userHome, name='userHome'),
    path('vendorHome/',views.vendorHome, name='vendorHome'),

    path('vendor_dashboard/',views.vendor_dashboard, name='vendor_dashboard'),
    path('user_dashboard/',views.user_dashboard, name='user_dashboard'),

    path('on_road/',views.on_road, name='on_road'),

    path('search/',views.search, name='search'),

    path('vendor/',include('vendor.urls')),

]