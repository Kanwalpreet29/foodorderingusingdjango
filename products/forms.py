from django import forms

class OrderForm(forms.Form):
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('CARD', 'Credit/Debit Card'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect, required=True)
    card_number = forms.CharField(max_length=16, required=False, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    card_expiry = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    card_cvc = forms.CharField(max_length=3, required=False, widget=forms.TextInput(attrs={'placeholder': 'CVC'}))

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')

        if payment_method == 'CARD':
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvc = cleaned_data.get('card_cvc')

            if not card_number or not card_expiry or not card_cvc:
                raise forms.ValidationError("All card details are required for card payment.")
        return cleaned_data
