from django.shortcuts import redirect, get_object_or_404
from store.models import Product
from django.views import View
from django.views.generic import FormView, TemplateView
from .forms import CartAddProductForm
from .cart import Cart
# Create your views here.

class CartView(TemplateView):
    template_name = 'orders/cart_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart'] = cart
        total = sum(item['total_price'] for item in cart)
        context['total'] = total
        return context

class CartAddView(FormView):
    form_class = CartAddProductForm
    template_name = 'orders/cart_add.html' 
    
    def form_valid(self, form):    
        cart = Cart(self.request)
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        cd = form.cleaned_data
        cart.add(product, quantity=cd['quantity'], override_quantity=cd['override'])
        return redirect('orders:cart_detail')

    
    