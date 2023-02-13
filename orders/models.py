from django.db import models
from accounts.models import User
from vendor.models import Vendor
# Create your models here.
class Defects(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
class Vehicle(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Models(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name 

 

class Types(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Orders(models.Model):

    STATUS_CHOICES = [
        ('NEW', 'NEW'),
        ('ACCEPTED', 'ACCEPTED'),
        ('DECLINED', 'DECLINED'),
        ('COMPLETED', 'COMPLETED'),
        ('PENDING', 'PENDING'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    u_phone_number = models.CharField(max_length=12, blank=True)
    v_phone_number = models.CharField(max_length=12, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    type = models.ForeignKey(Types, on_delete=models.CASCADE, blank=True, null=True)
    model = models.ForeignKey(Models, on_delete=models.CASCADE, blank=True, null=True)
    defect = models.ForeignKey(Defects, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    eta = models.CharField(max_length=200, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.description

class Order_images(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.order.description       
                       