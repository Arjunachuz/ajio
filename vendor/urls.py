from django.urls import path,include
from .import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendor_dashboard, name='vendor'),
    path('profile/',views.profile, name='vprofile'),

    path('opening-hours/',views.opening_hours, name='opening_hours'),
    path('opening-hours/add/',views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/',views.remove_opening_hours, name='remove_opening_hours'),

]