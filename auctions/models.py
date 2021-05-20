from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timezone
import pytz

# class user inherits from AbstractUser to represent each registered user
class User(AbstractUser):
    # return user details
    def __str__(self):
        return f"{self.username}"

# class Listings to represent each auction listings
class Listings(models.Model):
    title = models.CharField(max_length=255, primary_key=True) # listing title
    description = models.CharField(max_length=2048) # listing description and details
    category = models.CharField(max_length=64, default="") # listing category
    picture = models.CharField(max_length=2048) # listing picture to be retrieved from url
    bid = models.DecimalField(max_digits=19, decimal_places=2) # starting bid
    time = models.DateTimeField(auto_now=True) # time of listing
    # each listing could be in watchlist from multiple users
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_listings") # user who lists
    active = models.BooleanField(default=True) # active/passive listings

    # return listing details
    def __str__(self):
        return f"{self.title} - {self.description} has current bid of {self.bid}"

    def serialize(self):
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "picture": self.picture,
            "bid": self.bid, 
            "time": utc_to_local(self.time).strftime("%b %d %Y, %I:%M %p"),
            "watchlist": [user.username for user in self.watchlist.all()],
            "user": self.user.username,
            "active": self.active,
        }

# class Bids to represent all bids for Listings
class Bids(models.Model):
    # listing title that references title in class Listing
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    # user name that references username in class User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_bids")
    #listing = models.ManyToManyField(Listings, blank=True, related_name="bids")
    bid = models.DecimalField(max_digits=19, decimal_places=2) # the value of this bid
    time = models.DateTimeField(auto_now=True) # the time of this bid

    def __str__(self):
        return f"{self.user} bids on {self.listing} at {self.time} for {self.bid}"

    def serialize(self):
        return {
            "id": self.id,
            "listing": self.listing.title,
            "user": self.user.username,
            "bid": self.bid, 
            "time": utc_to_local(self.time).strftime("%b %d %Y, %I:%M %p"),
        }

# class Comments to represent all comments on Listings
class Comments(models.Model):
    # listing title that references title in class Listings
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    # user name that references username in class User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_comments")
    comment = models.CharField(max_length=255) # the value of this commend
    time = models.DateTimeField(auto_now=True) # the time of this comment

    def __str__(self):
        return f"{self.user} comments on {self.listing} at {self.time} with {self.comment}"
        
    def serialize(self):
        return {
            "id": self.id,
            "listing": self.listing.title,
            "user": self.user.username,
            "comment": self.comment, 
            "time": utc_to_local(self.time).strftime("%b %d %Y, %I:%M %p"),
        }

# convert timezone
def utc_to_local(utc_dt):
    tz = pytz.timezone('Australia/Sydney')
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=tz)





