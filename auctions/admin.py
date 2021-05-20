from django.contrib import admin

from .models import Listings, Bids, Comments

# Register your models here.
class ListingsAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "category", "picture", "bid", "time", "user", "active")
    filter_horizontal = ("watchlist", )

class BidsAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "bid", "time")

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "comment", "time")

admin.site.register(Listings, ListingsAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
