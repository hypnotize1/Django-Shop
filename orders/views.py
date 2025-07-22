import requests
from django.shortcuts import redirect, get_object_or_404, HttpResponse, render
from django.urls import reverse
from django.views import View
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView, DetailView, CreateView
from django.conf import settings
from django.contrib import messages


from .forms import CartAddProductForm, OrderCreationForm, CouponApplyForm
from .cart import Cart
from .models import Order, OrderItem, Coupon
from store.models import Product


# Create your views here.

class CartView(TemplateView):
    template_name = 'orders/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart'] = cart
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


class CartRemoveView(View):
    def post(self, request , product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart_detail')
    
    
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderCreationForm
    template_name = 'orders/order_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    def form_valid(self, form):
        cart = Cart(self.request)
        if not cart.cart:
            return redirect('store:home')  

        order = form.save(commit=False)
        order.user = self.request.user
        order.save()

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant=item.get('variant', None),
                quantity=item['quantity'],
                price=item['price'],
            )
        cart.clear()
        return redirect('orders:order_detail', order_id=order.id)
    

class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    form_class = CouponApplyForm
    
    def get_object(self):
        order_id = self.kwargs['order_id']
        user = self.request.user
        return get_object_or_404(Order, id=order_id, user=user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        context['form'] = self.form_class()
        return context

        
class PayOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order =  get_object_or_404(Order, id=kwargs['order_id'])
        
        if order.user != request.user:
            return HttpResponse("You don't have permission to pay this order.", status=403)
        
        request.session['order_pay'] = {'order_id': order.id}
        
        callback_url = request.build_absolute_uri(reverse('orders:payment_verify'))
        
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(order.get_total_order_price()),
            "callback_url": callback_url,
            "description": "پرداخت سفارش شماره " + str(order.id),
            "metadata": {
                "mobile": request.user.phone,
                "email": request.user.email
            }
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
            
        }
        
        try:
            response = requests.post(settings.ZARINPAL_REQUEST_URL, json=data, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return HttpResponse(f"Connection error: {e}", status=503)
        response_data = response.json()
        
        
        # check request status
        if 'data' in response_data and response_data['data'].get('code') == 100:
            authority = response_data['data']['authority']
            return redirect(settings.ZARINPAL_STARTPAY_URL.format(authority=authority))
      

        # errors
        error = response_data.get('errors', {})
        return HttpResponse(f"Error code: {error.get('code')}, Error message: {error.get('message')}")


class PaymentVerifyView(LoginRequiredMixin, View):
    
    def get(self, request):
        # Get data from Zarinpal callback
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        
        session_data = request.session.get('order_pay')
        
        if not session_data or not authority:
            return HttpResponse('Invalid session or missing authority.')
        
        order_id = session_data.get('order_id')
        
        try:
            order = Order.objects.get(id=int(order_id), user=request.user)
        except Order.DoesNotExist:
            return HttpResponse('Order not found or access denied.', status=404)
        
        if status != 'OK':
            return render(request, 'orders/payment_failed.html', {"order": order})
        
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(order.get_total_order_price()),
            "authority": authority
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(settings.ZARINPAL_VERIFY_URL, json=data, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return HttpResponse(f"Connection error: {e}", status=503)

        response_data = response.json()
        if 'data' in response_data and response_data['data'].get('code') == 100:
            # Payment successful
            ref_id = response_data['data'].get('ref_id')
            order.paid = True
            order.payment_ref_id = ref_id
            order.status = 'processing'  # if you want to update status
            order.save()

            # Clean session
            del request.session['order_pay']

            return render(request, 'orders/payment_success.html', {
                "order": order,
                "ref_id": ref_id
            })
    
        # Payment failed
        error_code = response_data.get('errors', {}).get('code', 'No code')
        error_message = response_data.get('errors', {}).get('message', 'No message')

        return render(request, 'orders/payment_failed.html', {
            "order": order,
            "error_code": error_code,
            "error_message": error_message
        })


class CouponApplyView(View):
    def post(self, request, order_id):
        form = CouponApplyForm(request.POST)
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if form.is_valid():
            code = form.cleaned_data['code']
            now = timezone.now()
            try:
                coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
                order.coupon = coupon
                order.save()
                messages.success(request, 'Coupon applied successfully.')
            except Coupon.DoesNotExist:
                messages.error(request, 'This coupon is not valid.')
        else:
            messages.error(request, 'Invalid form submission.')
        return redirect('orders:order_detail', order_id=order.id)
