from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.TextField()
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails', null=True, blank=True)
    base_price = models.IntegerField()
    current_price = models.IntegerField(null=True, blank=True)
    choices = (("Fashion", "Fashion"), ("Electronics", "Electronics"), ("Furniture", "Furniture"), ("Daily Essentials", "Daily Essentials"))
    category = models.CharField(max_length = 100, choices=choices, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closed_listing = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Listings, blank=True)
    def __str__(self):
        return f"{self.user}"

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    comment = models.TextField()
    time = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    bid = models.IntegerField()
    datetime = models.DateTimeField(default=now)