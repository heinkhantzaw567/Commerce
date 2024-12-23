from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings"
    )   
    title = models.CharField(max_length=120)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=200)
    description = models.CharField(max_length=500)
    element = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.bid_price}"

class Comment(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    comment = models.CharField(max_length=400)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.auction.title}"
    
class Watchlists(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlist_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")


class Winner(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner_user")
    auction_name = models.CharField(max_length=200)