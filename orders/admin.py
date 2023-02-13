from django.contrib import admin
from .models import Orders,Order_images,Defects,Models,Types,Vehicle
# Register your models here.
admin.site.register(Orders)
admin.site.register(Order_images)
admin.site.register(Defects)
admin.site.register(Models)
admin.site.register(Types)
admin.site.register(Vehicle)