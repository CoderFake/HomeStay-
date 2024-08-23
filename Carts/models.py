from django.db import models
from Accounts.models import User
from Homestays.models import Homestays


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    homestay_name = models.CharField(max_length=250)
    homestay_price = models.FloatField()
    homestay_discount = models.FloatField()
    user = models.ForeignKey(User, related_name="cart_user", on_delete=models.CASCADE, null=True)
    homestay = models.ForeignKey(Homestays, on_delete=models.CASCADE, related_name="cart_homestay")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)

    def sub_total(self):
        return round(self.homestay_price - self.homestay_discount*self.homestay_price, 2)
