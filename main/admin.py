from django.contrib import admin
from .models import Wallet, Credit, Debit, Reason, Category


admin.site.register(Wallet)
admin.site.register(Credit)
admin.site.register(Debit)
admin.site.register(Reason)
admin.site.register(Category)
