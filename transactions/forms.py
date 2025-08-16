from django import forms
from .models import Transactions
from accounts.models import UserBankAccount

class TransactionsForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ['amount' ,'account_no', 'transaction_type']
        
    def __init__(self,*args,**kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args,**kwargs)
        self.fields['transaction_type'].disabled =True
        self.fields['transaction_type'].widget =forms.HiddenInput()
        
    def save(self, commit = True):
        self.instance.account =self.account
        self.instance.balance_after_transaction =self.account.balance
        return super().save()
    
class DepositForm(TransactionsForm):
    def clean_amount(self):
        min_deposit_amount=100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"You need to deposit at least {min_deposit_amount}"
                
            )
        return amount
class WithdrawalFrom(TransactionsForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )
        
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )
        return amount
class LoabRequestForm(TransactionsForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        return amount

class TransferMoney(TransactionsForm):
    def clean(self):
        cleaned_data = super().clean()
        account = self.account
        amount = cleaned_data.get('amount')
        account_no = cleaned_data.get('account_no')

        if amount and amount > account.balance:
            raise forms.ValidationError("You don't have enough balance.")

        if account_no == account.account_no:
            raise forms.ValidationError("You cannot transfer to your own account.")

        try:
            target_account = UserBankAccount.objects.get(account_no=account_no)
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError("Target account not found.")

        cleaned_data['to_account'] = target_account
        return cleaned_data
        
        
        
        
    