from django import forms
from .models import Debit, Wallet

class DebitForm(forms.ModelForm):
    class Meta:
        model = Debit
        fields = ['wallet', 'reason', 'amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        wallet = self.cleaned_data.get('wallet')

        if amount and wallet and amount > wallet.amount:
            raise forms.ValidationError('Entered amount cannot be greater than the wallet amount.')

        return amount


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['title', 'amount', 'currency']