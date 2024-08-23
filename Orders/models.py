from django.db import models
from Accounts.models import User
from Homestays.models import Homestays


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payment')
    transaction_id = models.CharField(max_length=100)
    amount = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    payment_method = models.CharField(max_length=100)
    status = models.BooleanField(default=False)


class Order(models.Model):
    order_code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    check_in_date = models.DateField()
    checkout_date = models.DateField()
    order_total = models.FloatField()
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_order')
    payment = models.OneToOneField(Payment, related_name="payment_order", on_delete=models.SET_NULL, blank=True, null=True)


class OrderHomestay(models.Model):
    homestay_name = models.CharField(max_length=100)
    homestay_price = models.FloatField()
    homestay_discount = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orderhomestay')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_orderhomestay')
    homestay = models.ForeignKey(Homestays, on_delete=models.CASCADE, related_name='homestay_orderhomestay')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="payment_orderhomestay", null=True, blank=True)



