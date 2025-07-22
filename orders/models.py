from random import randint
from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import Account
from store.models import Address, Product, ProductVariant

# Create your models here.
class Order(models.Model):
    user =  models.ForeignKey(Account, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
        ],
        default='pending'
)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online_payment', 'Online Payment'),
        ('wallet_payment', 'Wallet Payment'),
    ])
    payment_ref_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def get_total_order_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())

    def get_total_price_after_discount(self):
        total = self.get_total_order_price()
        if self.coupon and self.coupon.is_valid():
            return total - (total * self.coupon.discount / 100)
        return total

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_unique_order_number()
        super().save(*args, **kwargs)
        
    @staticmethod
    def generate_unique_order_number():
        return f"ORD{now().strftime('%Y%m%d')}{randint(1000,9999)}"

 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} of {self.product.name} in Order #{self.order.order_number}'        
    
    def get_total_item_price(self):
        return self.price * self.quantity 
        

class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    discount = models.IntegerField(validators=[MinValueValidator(10), MaxValueValidator(90)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

