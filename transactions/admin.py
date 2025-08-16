from django.contrib import admin
from .models import Transactions
from .views import transaction_email_send
# Register your models here.
@admin.register(Transactions)
class TransactionAdmin(admin.ModelAdmin):
    list_display =['account','amount','balance_after_transactions','transaction_type','loan_approve']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        transaction_email_send(obj.account.user,obj.amount,"Congratulations your loan is Approved",'transactions/admin_email.html')
        return super().save_model(request, obj, form, change)
