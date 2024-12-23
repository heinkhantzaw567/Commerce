from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,AuctionListing,Bid,Watchlists,Comment,Winner
from django import forms

class CreateListing(forms.Form):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'})
    )
    starting_bid = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Starting Bid'})
    )
    image_url = forms.URLField(
        max_length=200,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter image URL'})
    )
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3})
    )
    element = forms.CharField(label="element",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter element'})
    )

class CommentForm(forms.Form): # comment input form:
    comment = forms.CharField(max_length=400,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comment'}))


class BidForm(forms.Form):
    bid_price =forms.DecimalField(max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Bid'})
    )
def index(request):
    print(request.user)
    if request.user:
        winners = Winner.objects.filter(user=request.user)
        print(winners)
        return render(request, "auctions/index.html",
                    {
                        "listings":AuctionListing.objects.all(),
                        "winners" : winners
                    })
    else:
        
        return render(request, "auctions/index.html",
                  {
                      "listings":AuctionListing.objects.all(),
                      "winners" : ""
                  })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
    
def create(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
            auction_listing = AuctionListing(
                user_id=request.user,  
                title=form.cleaned_data['title'],
                starting_bid=form.cleaned_data['starting_bid'],
                image_url=form.cleaned_data['image_url'],
                description=form.cleaned_data['description'],
                element=form.cleaned_data['element']
            )
            auction_listing.save()
        return HttpResponseRedirect(reverse("auctions:index"))

    return render (request, "auctions/create.html",
                   {
                       "form":CreateListing()
                   })

def active(request, auction_id):
    listing = AuctionListing.objects.get(id=auction_id)
    bids = Bid.objects.filter(auction=listing).order_by('-bid_price').first()  
    countingbids = Bid.objects.filter(auction=listing).count()
    value = Watchlists.objects.filter(auction=auction_id, user=request.user).count()  
    owner = AuctionListing.objects.filter(user_id=request.user, id=auction_id)
    Comments = Comment.objects.filter(auction=listing)
    if value  == 0:
        place = "watchlist"
    else: 
        place ="remove"
    
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        
        form = BidForm(request.POST)
        action = request.POST.get('action')
        print(action)
        
        
        if request.user.is_anonymous:
                return render (request, "auctions/active.html",{
                                    "listing":listing,
                                    "form": BidForm(),
                                    "current_bid":bids,
                                    "count":countingbids,
                                    "place":place,
                                    "owner":owner,
                                    "comment": CommentForm(),
                                    "comments": Comments
                                    })
        if action == 'close':
            
            print(bids)
            print(listing)
            winner = Winner(
                user = bids.user,
                auction_name = listing.title
            )
            winner.save()
            owner.delete()

            return HttpResponseRedirect(reverse('auctions:index'))
        if  form_type == 'bids':
            if action == 'bid':
                price = listing.starting_bid
                if bids is not None :
                        price = bids.bid_price
                
                if form.is_valid():
                    if price >= form.cleaned_data['bid_price'] :
                        return render (request, "auctions/active.html",{
                                        "listing":listing,
                                        "form": BidForm(),
                                        "current_bid":bids,
                                        "count":countingbids,
                                        "place":"remove",
                                        "place":place,
                                        "owner":owner,
                                        "comment": CommentForm(),
                                        "comments": Comments
                                        })
                    bid = Bid(
                        user = request.user,
                        auction = listing,
                        bid_price = form.cleaned_data['bid_price']
                    )
                    listing.starting_bid = form.cleaned_data['bid_price']
                    listing.save()
                    bid.save()
                    return HttpResponseRedirect(reverse("auctions:index"))
                
                return render (request, "auctions/active.html",{
                                        "listing":listing,
                                        "form": BidForm(),
                                        "current_bid":bids,
                                        "count":countingbids,
                                        "place":place,
                                        "owner":owner,
                                        "comment": CommentForm(),
                                        "comments": Comments
                                        }) 
        if form_type == 'comments':
            
            commentform = CommentForm(request.POST)
            
            if commentform.is_valid():
                ex =commentform.cleaned_data['comment']
                print(ex)
                comments = Comment(
                    user = request.user,
                    auction = listing,
                    comment = commentform.cleaned_data['comment']
                )
                comments.save()
                return HttpResponseRedirect(reverse("auctions:index"))
        if action == 'watchlist':
            
            
            watch = Watchlists(
                auction = listing,
                user = request.user
            )
            watch.save()
            
            return render (request, "auctions/active.html",{
                                    "listing":listing,
                                    "form": BidForm(),
                                    "current_bid":bids,
                                    "count":countingbids,
                                   "place":"remove",
                                   "owner":owner,
                                   "comment": CommentForm(),
                                   "comments": Comments
                                    })
        if action == 'remove':
            watch =Watchlists.objects.filter(auction=auction_id, user=request.user)
            watch.delete()
            return render (request, "auctions/active.html",{
                                    "listing":listing,
                                    "form": BidForm(),
                                    "current_bid":bids,
                                    "count":countingbids,
                                    "place":"watchlist",
                                    "comment": CommentForm(),
                                    "comments": Comments
                                    })
                                      
            
     
    return render (request, "auctions/active.html",{
        "listing":listing,
        "form": BidForm(),
        "current_bid":bids,
        "count":countingbids,
        "place":place,
        "owner":owner,
        "comment": CommentForm(),
        "comments": Comments
        })

def watchlist(request):
    listing = Watchlists.objects.filter(user=request.user)
    print(listing)
    return render (request, "auctions/watch.html",
                   {
                       "listings":listing
                   })

def categories(request):
    elements = AuctionListing.objects.values('element').distinct()
    if request.method == "POST":
        listings = AuctionListing.objects.filter(element=request.POST["element"])
        print(listings)
        return render (request, "auctions/categories.html",
                       {"elements":elements,
                       "listings":listings})
    
    
    return render (request, "auctions/categories.html",
                    {"elements":elements,
                        "listings":None})