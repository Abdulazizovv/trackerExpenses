from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserCreationForm
from django.contrib.auth import get_user_model
from main.models import Wallet
from django.contrib.auth.decorators import login_required

# Create your views here.


class loginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('index') 
    
    def form_invalid(self, form):
        messages.error(self.request, _("Foydalanuvchi nomi yoki parol xato!"))
        return self.render_to_response(self.get_context_data(form=form))
    
def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        User = get_user_model()
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, _("Foydalanuvchi nomi yoki elektron pochta manzili allaqachon mavjud!"))
            return render(request, 'auth/registration.html')
        if password1 == password2:
            try:
                user = UserProfile.objects.create_user(username=username, email=email, password=password1)
                user.save()
                authenticated_user = authenticate(request, username=username, password=password1)

                if authenticated_user:
                    # Log in the user
                    login(request, authenticated_user)

                    messages.success(request, _("Muvaffaqqiyatli!"))
                    return redirect('index')
            except Exception as err:
                print(err)
                messages.error(request, _("Foydalanuvchi nomi yoki parol xato!"))
        else:
            messages.error(request, _("Parollar bir xil emas!"))
    return render(request,'auth/registration.html')


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def profile(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(username=request.user.username)
        wallets = Wallet.objects.filter(user=user)
        usd_summ = 0
        rub_summ = 0
        uzs_summ = 0
        for wallet in wallets:
            if wallet.currency == 'USD':
                usd_summ += wallet.amount
            elif wallet.currency == 'RUB':
                rub_summ += wallet.amount
            elif wallet.currency == 'UZS':
                uzs_summ += wallet.amount
        context = {
            'usd_summ': usd_summ,
            'rub_summ': rub_summ,
            'uzs_summ': uzs_summ,
            'user': user,
            'wallets': wallets
        }
        return render(request, 'profile.html', context=context)
    else:
        return redirect('index')