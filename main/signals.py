from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Reason, Category

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_reasons(sender, instance, created, **kwargs):
    if created:
        # Check if the user is newly created and create default reasons
        Category.objects.create(user=instance, title='Oylik maosh', icon='icon-1')
        Category.objects.create(user=instance, title='Kundalik tushum', icon='icon-2')
        Category.objects.create(user=instance, title='Stipendiya', icon='icon-3')
        Category.objects.create(user=instance, title='Pensiya', icon='icon-3')
        Category.objects.create(user=instance, title='Qo\'shimcha daromad', icon='icon-3')
        # Add more default reasons as needed

        Reason.objects.create(user=instance, title='Kundalik harajatlar')
        Reason.objects.create(user=instance, title='Yo\'l haqi')
        Reason.objects.create(user=instance, title='Ovqatlanish')
        Reason.objects.create(user=instance, title='Internet')

