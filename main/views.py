from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Debit, Credit, Category, Reason, Wallet
from account.models import UserProfile
from datetime import datetime, date, timedelta
from django.utils import timezone
from .forms import DebitForm, WalletForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required



class loginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('index') 
    
    def form_invalid(self, form):
        messages.error(self.request, _("Foydalanuvchi nomi yoki parol xato!"))
        return self.render_to_response(self.get_context_data(form=form))


def index(request):
    context = {

    }
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        wallets = Wallet.objects.filter(user=user)
        incomes = Debit.objects.filter(user=user).order_by('-created')
        categories = Category.objects.filter(user=user)
        expenses = Credit.objects.filter(user=user).order_by('-created')
        reasons = Reason.objects.filter(user=user)
        # print(Debit.objects.filter(user=user, currency="USD"))
        
        usd_summ = 0
        rub_summ = 0
        uzs_summ = 0

        left_usd = 0
        left_rub = 0
        left_uzs = 0

        usd_exp = 0
        rub_exp = 0
        uzs_exp = 0

        left_summ = 0
        income_summ = 0
        expense_summ = 0
        for i in wallets:
            if i.currency == 'USD':
                for k in Debit.objects.filter(wallet=i):
                    usd_summ += int(k.amount)
                usd_summ += int(i.amount)

            elif i.currency == 'RUB':
                for k in Debit.objects.filter(wallet=i):
                    rub_summ += int(k.amount)
                rub_summ += int(i.amount)
                
            elif i.currency == 'UZS':
                for k in Debit.objects.filter(wallet=i):
                    uzs_summ += int(k.amount)
                uzs_summ += int(i.amount)
                
        for i in incomes:
            income_summ += int(i.amount)

        for i in expenses:
            if i.wallet.currency == 'USD':
                usd_exp += int(i.amount)
            elif i.wallet.currency == 'RUB':
                rub_exp += int(i.amount)
            elif i.wallet.currency == 'UZS':
                uzs_exp += int(i.amount)
        left_usd = usd_summ - usd_exp
        left_rub = rub_summ - rub_exp
        left_uzs = uzs_summ - uzs_exp
        
        left_summ = income_summ - expense_summ
        today_date = timezone.localdate()

        todays_incomes = Debit.objects.filter(user=user, created__date=today_date).order_by('created')
        todays_expenses = Credit.objects.filter(user=user, created__date=today_date).order_by('-created')

        context = {
            'usd_summ': usd_summ,
            'rub_summ': rub_summ,
            'uzs_summ': uzs_summ,
            'left_usd': left_usd,
            'left_rub': left_rub,
            'left_uzs': left_uzs,
            'usd_exp': usd_exp,
            'rub_exp': rub_exp,
            'uzs_exp': uzs_exp,
            'left_summ': left_summ,
            'todays_incomes':todays_incomes,
            'todays_expenses':todays_expenses,
            'wallets': wallets,
            'categories': categories,
            'reasons': reasons,
            'income_summ': income_summ,
            'expense_summ': expense_summ,
            'incomes': incomes,
            'expenses': expenses,
            'today': today_date.strftime('%m-%d')
        }

        if request.method == 'POST':
            which = request.POST.get('which')
            if which == 'income':
                wallet_id = request.POST.get('incomeWallet')
                wallet = Wallet.objects.get(id=int(wallet_id))
                category_id = request.POST.get('incomeCategory')
                category = Category.objects.get(id=int(category_id))
                amount = request.POST.get('incomeAmount')
                new_income = Debit.objects.create(
                    user = user,
                    wallet = wallet,
                    reason = category,
                    amount = amount,
                )
                wallet.amount += int(amount)
                new_income.save()
                wallet.save()
                print("income saved")
                messages.success(request, _('Kirim saqlandi'))
                return redirect('index')
            elif which == 'expense':
                wallet_id = request.POST.get('expenseWallet')
                wallet = Wallet.objects.get(id=int(wallet_id))
                reason_id = request.POST.get('expenseCategory')
                reason = Reason.objects.get(id=int(reason_id))
                amount = request.POST.get('expenseAmount')
                if wallet.currency == 'USD':
                    left_summ = left_usd
                elif wallet.currency == 'RUB':
                    left_summ = left_rub
                elif wallet.currency == 'UZS':
                    left_summ = left_uzs
                if int(amount) <= left_summ:
                    new_expense = Credit.objects.create(
                        user = user,
                        wallet = wallet,
                        reason = reason,
                        amount = amount,
                    )
                    wallet.amount -= int(amount)
                    new_expense.save()
                    wallet.save()
                    print(wallet_id, reason_id, amount)
                    messages.success(request, _('Chiqim saqlandi'))
                    return redirect('index')
                else:
                    messages.warning(request, _('Hamyoningizdagi pul siz kiritgan miqdordan kam!'))
                    return redirect('index')
    return render(request, 'index.html', context)

@login_required(login_url='login')
def delete_record(request, suffix, id, url):
    print(suffix, id, url)
    if request.user.is_authenticated:
        if suffix == 'income':
            income = Debit.objects.get(id=int(id))
            income.delete()
            messages.success(request, _("Muvaffaqqiyatli o'chirildi"))
        elif suffix == 'expense':
            expense = Credit.objects.get(id=int(id))
            expense.delete()
            messages.success(request, _("Muvaffaqqiyatli o'chirildi"))
        return redirect(url)
    else:
        return redirect('index')

@login_required(login_url='login')
def weekly_expenses(request):
    current_week_start = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
    current_week_end = current_week_start + timezone.timedelta(days=6)
    if request.user.is_authenticated:
        weekly_credits = Credit.objects.filter(
            user=request.user,
            created__date__range=[current_week_start, current_week_end]
        ).order_by('-created')

        weekly_debits = Debit.objects.filter(
            user=request.user,
            created__date__range=[current_week_start, current_week_end]
        ).order_by('-created')
        print(weekly_debits)
        context = {
            'current_week_start': current_week_start.strftime('%d-%m'),
            'current_week_end': current_week_end.strftime('%d-%m'),
            'weekly_incomes': weekly_debits,
            'weekly_expenses': weekly_credits,
        }
        return render(request, 'weekly_expenses.html', context)

@login_required(login_url='login')
def monthly_expenses(request):
    # Calculate the start and end dates for the current month
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = current_month_start.replace(
        day=1, month=current_month_start.month + 1
    ) - timedelta(days=1)

    if request.user.is_authenticated:
        # Filter credits and debits for the current month
        monthly_credits = Credit.objects.filter(
            user=request.user,
            created__date__range=[current_month_start, current_month_end]
        ).order_by('-created')

        monthly_debits = Debit.objects.filter(
            user=request.user,
            created__date__range=[current_month_start, current_month_end]
        ).order_by('-created')

        context = {
            'current_month_start': current_month_start.strftime('%d-%m'),
            'current_month_end': current_month_end.strftime('%d-%m'),
            'monthly_incomes': monthly_debits,
            'monthly_expenses': monthly_credits,
        }

        return render(request, 'monthly_expenses.html', context)


# for select date
# tanlangan kun uchun hisobotlar
@login_required(login_url='login')
def daily_expenses(request):
    # Convert the selected date parameter to a datetime object
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        request.session['selected_date'] = selected_date
        request.session.modified =True
        # print(selected_date)
        return redirect('selected_date')
    
    if request.method == 'GET':
        selected_date = request.session.get('selected_date')
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')

            # Calculate the start and end of the selected day
        selected_day_start = selected_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        selected_day_end = selected_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)

        if request.user.is_authenticated:
                # Filter credits and debits for the selected day
            daily_credits = Credit.objects.filter(
                    user=request.user,
                    created__range=[selected_day_start, selected_day_end]
                ).order_by('-created')

            daily_debits = Debit.objects.filter(
                    user=request.user,
                    created__range=[selected_day_start, selected_day_end]
                ).order_by('-created')

            context = {
                    'selected_day': selected_datetime.strftime('%d-%m-%Y'),
                    'daily_incomes': daily_debits,
                    'daily_expenses': daily_credits,
                }

            print(request.session.get('selected_date'))
            return render(request, 'selected_day.html', context)
        
@login_required(login_url='login')
def wallets(request):
    if request.user.is_authenticated:

        wallets = Wallet.objects.filter(user=request.user)
        currencies = ['USD', 'EUR', 'UZS']
        context = {
            'wallets': wallets,
            'currencies': currencies
        }
        return render(request, 'wallets.html', context)
    else:
        return redirect('index')


# edit wallet
# hamyon ma'lumotlarini o'zgartirish
@login_required(login_url='login')
def edit_wallet(request):
    if request.method == 'POST':
        wallet = get_object_or_404(Wallet, id=int(request.POST.get('wallet_id')), user=request.user)
        if wallet:
            wallet.title = request.POST.get('title')
            wallet.amount = int(request.POST.get('amount') or 0)
            wallet.currency = request.POST.get('currency')
            wallet.save()
            messages.success(request, _('Hamyon o\'zgartirildi'))
        else:
            messages.warning(request, _('Nimadir xato ketdi!'))
    return redirect('wallets')


@login_required(login_url='login')
def add_wallet(request):
    if request.method == 'POST':
        print(request.user)
        form = WalletForm(request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user
            wallet.save()
            messages.success(request, _('Hamyon qo\'shildi'))
        else:
            print(form.errors)
            messages.warning(request, _('Nimadir xato ketdi!'))
    return redirect('wallets')

@login_required(login_url='login')
def delete_wallet(request, wallet_id):
    if request.user.is_authenticated:
        wallet = Wallet.objects.get(id=int(wallet_id))
        wallet.delete()
        messages.success(request, _('Hamyon o\'chirildi!'))
        return redirect('wallets')
    else:
        return redirect('index')


# add expense types
@login_required(login_url='login')
def add_categories(request):
    if request.method == 'POST':
        print(request.POST)
        which = request.POST.get('which')
        title = request.POST.get('title')
        if which == 'income':
            Category.objects.create(user=request.user, title=title).save()
            messages.success(request, _('Kirim turi saqlandi'))
            return redirect('add_categories')
        elif which == 'expends':
            Reason.objects.create(user=request.user, title=title).save()
            messages.success(request, _('Chiqim turi saqlandi'))
            return redirect('add_categories')
    user = request.user
    incomes = Category.objects.filter(user=user)
    expends = Reason.objects.filter(user=user)
    context = {
        'incomes': incomes,
        'expends': expends,
    }
    return render(request, 'inc_and_exp.html', context)

@login_required(login_url='login')
def delete_category(request, suffix, category_id):
    user = request.user
    which = suffix
    if which == 'income':
        category = Category.objects.get(user=user, id=int(category_id))
        category.delete()
        messages.success(request, _('Kirim turi o\'chirildi'))
        return redirect('add_categories')
    elif which == 'expends':
        reason = Reason.objects.get(user=user, id=int(category_id))
        reason.delete()
        messages.success(request, _('Chiqim turi o\'chirildi'))
        return redirect('add_categories')
