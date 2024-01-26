from django.db import models
from account.models import UserProfile


class Reason(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


# for debits reason
class Category(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.title


# Hisoblar uchun
# Bunda foydalanuvchi bir nechta karta yoki hamyon qo'shishi mumkin
class Wallet(models.Model):
    currencies = (
        ('USD', 'USD'),
        ('RUB', 'RUB'),
        ('UZS', 'UZS'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)
    amount = models.PositiveBigIntegerField(default=0)
    currency = models.CharField(max_length=10, choices=currencies)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


# model for incomes
# kirimlar uchun model
class Debit(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) # qaysi user
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE) # qaysi wallet dan
    reason = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True) #sababi
    amount = models.PositiveBigIntegerField() #miqdori
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.wallet.title +'-'+ self.reason.title


# for expenses
# chiqimlar uchun
class Credit(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    reason = models.ForeignKey(Reason, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.wallet.title +'-'+ self.reason.title
