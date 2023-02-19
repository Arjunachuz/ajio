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
    path('v_orders/',views.v_orders, name='v_orders'),
    path('v_orders_detail/<int:order_id>',views.v_orders_detail, name='v_orders_detail'),

    path('user_dashboard/',views.user_dashboard, name='user_dashboard'),
    path('my_orders/',views.my_orders, name='u_my_orders'),
    path('my_orders_detail/<int:order_id>',views.my_orders_detail, name='u_my_orders_detail'),

    path('on_road/',views.on_road, name='on_road'),

    path('search/',views.search, name='search'),

    path('service/<int:vendor_id>/',views.service, name='service'),
    
    path('order/<int:vendor_id>/',views.order, name='order'),
    path('home_service/<int:vendor_id>/',views.home_service, name='home_service'),
    
    path('ajax/load-models/',views.load_models, name='ajax_load_models'),

    path('order_detail/<int:order_id>/',views.order_detail, name='order_detail'),
    path('order_bill/<int:order_id>/',views.order_bill, name='order_bill'),
    path('order_bill/',views.order_bill, name='order_bill'),

    path('accept/<int:order_id>/',views.accept, name='accept'),
    path('decline/<int:order_id>/',views.decline, name='decline'),

    path('end_page/<uidb64>/<order_id>/',views.end_page, name='end_page'),


    path('vendor/',include('vendor.urls')),


   

    path('u_profile/',views.u_profile, name='u_profile'),
    path('admin/',views.admin_login, name='admin_login'),
    path('admin_home/',views.admin_dashboard, name='admin_dashboard'),

]