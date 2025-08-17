from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE
# Create your models here.

class Transactions(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name='transactions' ,on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    account_no = models.IntegerField(blank=True,default=0)
    balance_after_transactions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)
    
    class Meta:
        ordering =['timestamp']
        


