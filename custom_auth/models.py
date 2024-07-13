from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=18)
    is_manager = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    REQUIRED_FIELDS = ['email']
