from django.db import models
from accounts.models import Account
from store.models import Address, Product, ProductVariant
from django.utils.timezone import now
from random import randint

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online_payment', 'Online Payment'),
        ('wallet_payment', 'Wallet Payment'),
    ])
    payment_ref_id = models.CharField(max_length=100, blank=True, null=True)  # 👈 اضافه کن

    def __str__(self):
        return f"Order #{self.order_number}"
    
    def get_total_order_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())

    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_unique_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_order_number():
        from random import randint
        from django.utils.timezone import now
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