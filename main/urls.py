from django.urls import path
from .views import (index, weekly_expenses, monthly_expenses,
                     delete_record, daily_expenses, wallets,
                     delete_wallet, add_wallet, edit_wallet,
                     add_categories, delete_category
                    )


urlpatterns = [
    path('', index, name='index'),
    path('weekly_expenses/', weekly_expenses, name='weekly_expenses'),
    path('monthly_expenses/', monthly_expenses, name='monthly_expenses'),
    path('reports/selected-day/', daily_expenses, name='selected_date'),
    path('delete/<str:suffix>/<int:id>/<str:url>/', delete_record, name='delete'),
    path('wallets/', wallets, name='wallets'),
    path('wallets/delete/<int:wallet_id>/', delete_wallet, name='delete_wallet'),
    path('add-wallet/', add_wallet, name='add_wallet'),
    path('edit_wallet/', edit_wallet, name='edit_wallet'),
    path('add-categories/', add_categories, name='add_categories'),
    path('delete_category/<str:suffix>/<int:category_id>/', delete_category, name='delete_category')
]