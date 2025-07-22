from django import forms
from .models import Order

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1)
    override = forms.BooleanField(
    required=False,
    initial=False,
    widget=forms.HiddenInput
)

# orders/forms.py
from django import forms
from .models import Order
from store.models import Address

class OrderCreationForm(forms.ModelForm):
    shipping_address = forms.ModelChoiceField(queryset=Address.objects.none(),
                                              empty_label="Select shipping address")

    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shipping_address'].queryset = Address.objects.filter(user=user)
