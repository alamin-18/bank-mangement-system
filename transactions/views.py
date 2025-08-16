from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404,redirect
from django.views import View
from django.views.generic import CreateView,ListView
from transactions.constants import DEPOSIT,WITHDRAWAL,LOAN,LOAN_PAID,TRANSFER_MONEY
from datetime import datetime
from django.db.models import Sum
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from transactions.forms import DepositForm,WithdrawalFrom,LoabRequestForm,TransferMoney
from .models import Transactions,Bankrupt
from django.http import HttpResponse
from accounts.models import UserBankAccount
# Create your views here.

def transaction_email_send(user,amount,subject,template):
    message = render_to_string(template,{
        'user':user,
        'amount':amount
    })
    send_email = EmailMultiAlternatives(subject,'',to=[user.email])
    send_email.attach_alternative(message,"text/html")
    send_email.send()

class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transactions
    title = ''
    success_url = reverse_lazy('transaction_report')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
             'title': self.title
        })
        return context
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        
        account.balance += amount
        account.save(
            update_fields=['balance']
        )
        transaction_email_send(self.request.user,amount,"Deposit Successfully!!","transactions/deposit_email.html")
        messages.success(self.request,
                         f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully')
        return super().form_valid(form)
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawalFrom
    title = 'Withdrawal'
    
    def get_initial(self):
        initial = {'transaction_type':WITHDRAWAL}
        return initial
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance']
        )
        transaction_email_send(self.request.user,amount,"Withdraw Successfully!!","transactions/withdrawal_email.html")
        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        return super().form_valid(form)

class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferMoney
    title = 'Money Transfer'
    
    def get_initial(self):
        initial ={'transaction_type': TRANSFER_MONEY }
        return initial
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account_no = form.cleaned_data.get('account_no')
        account = self.request.user.account
        found_account = UserBankAccount.objects.get(account_no=account_no)
        account.balance -= amount
        found_account.balance += amount

        account.save(
            update_fields=['balance']
        )
        found_account.save(
            update_fields=['balance']
        )
        messages.success(self.request,
                      f"${amount} successfully transferred"
                      f"from {account.account_no} to {account_no} 🎉"   
                         )
        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class = LoabRequestForm
    title = 'Request for Loan'
    
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count =Transactions.objects.filter(account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >=5:
            return HttpResponse("You have cross the loan limits")
            
        transaction_email_send(self.request.user,amount,"Apply For Loan Successfully!!","transactions/loan_email.html")    
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )   
          

            
        return super().form_valid(form)
class TransactionReportView(LoginRequiredMixin,ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transactions
    balance = 0
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str =self.request.GET.get('start_date')
        end_date_str =self.request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str,'%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str,'%Y-%m-%d').date()
            queryset = queryset.filter(timestamp__date__gte=start_date,timestamp__date__lte=end_date)
            self.balance = Transactions.objects.filter(timestamp__date__gte=start_date,timestamp__date__lte=end_date).aaggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account
        
        })
        return context
class PayLoanView(LoginRequiredMixin,View):
    def get(self,request,loan_id):
        loan = get_object_or_404(Transactions,id=loan_id)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transactions = user_account.balance
                user_account.save()
                loan.loan_approve =True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('transactions:loan_list')
            else:
                messages.error(
            self.request,
            f'Loan amount is greater than available balance'
        )
        return redirect('loan_list')

class LoanListView(LoginRequiredMixin,ListView):
    model = Transactions
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account =self.request.user.account
        queryset = Transactions.objects.filter(account=user_account,transaction_type=3)
        
        return queryset
                