from django.contrib import admin
from .models import Listings, User, Watchlist, Comments, Bid
# Register your models here.

class ListingsAdmin(admin.ModelAdmin):
    list_display = ("title", "category")

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("products",) 

class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "bid", "datetime")

admin.site.register(Listings, ListingsAdmin)
admin.site.register(User)
admin.site.register(Comments)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)