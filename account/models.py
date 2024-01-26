from django.db import models
from django.contrib.auth.models import User, AbstractUser


# User modeliga o'zgartirishlar kiritish
class UserProfile(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatars/', default='default-user.png')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username


