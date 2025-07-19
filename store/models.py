from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from accounts.validators import phone_validator, postal_code_validator


def unique_slug_generator(instance, slug_field_name, value_to_slugify):
    slug = slugify(value_to_slugify)
    modelclass = instance.__class__
    unique_slug = slug
    num = 1
    while modelclass.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug}-{num}"
        num += 1

    return unique_slug


class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE,
                                     null=True, blank=True,
                                     related_name='s_category'
                                    )
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        
        return self.name

    def get_absolute_url(self):
        return reverse("store:category", kwargs={"slug": self.slug})
    
    
    
    
class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ManyToManyField(Category, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', self.name)
        if self.stock == 0:
            self.available = False
        else:
            self.available = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
	    return reverse('store:product_detail', args=[self.slug,])


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    products = models.ManyToManyField(Product, blank=True, related_name='tags')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, 'slug', self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Address(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=11, validators=[phone_validator])
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, validators=[postal_code_validator])
    address_line = models.TextField()
    province = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.postal_code})"

    def get_full_address(self):
        return f"{self.province}، {self.city}، {self.address_line}، Postal Code : {self.postal_code}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"


class Wishlist(models.Model):
    user = models.OneToOneField('accounts.Account', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist of {self.user.email}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE,)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    # comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - by {self.user}"

