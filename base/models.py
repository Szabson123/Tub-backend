from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from custom_auth.models import CustomUser

class Tub(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    logo_img = models.ImageField(upload_to='logo_tub/', null=True)
    
    def __str__(self) -> str:
        return self.name


class Reservation(models.Model):
    tub = models.ForeignKey(Tub, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_reservations', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    counted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    nobody_status = models.BooleanField(default=True, null=True, blank=True)
    wait_status = models.BooleanField(default=False, null=True, blank=True)
    accepted_status = models.BooleanField(default=False, null=True, blank=True)
    
    def __str__(self) -> str:
        return f'Reservation by {self.user} on {self.tub.name}'


class Address(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='address_to_reservation')
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    home_number = models.CharField(max_length=100)
    

class Image(models.Model):
    tub = models.ForeignKey(Tub, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')


class Rating(models.Model):
    tub = models.ForeignKey(Tub, on_delete=models.CASCADE, related_name='ratings', null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_rating')
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    desciption = models.TextField(null=True)
    
    class Meta:
        unique_together = (('user', 'tub'))
        index_together = (('user', 'tub'))
        

class Discount(models.Model):
    tub = models.ForeignKey(Tub, on_delete=models.CASCADE, null=True, related_name = 'tube_discount')
    main = models.CharField(max_length=15)
    active = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    is_multi_use = models.BooleanField(default=False)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True)
    
    def __str__(self) -> str:
         return f'{self.main} for {self.tub.name if self.tub else "any tub"}'
     

class Faq(models.Model):
    question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=511, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.question if self.question else "FAQ without question"