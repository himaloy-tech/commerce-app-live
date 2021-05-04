from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Listings, Watchlist, Comments, Bid


def index(request):
    return render(request, "auctions/index.html", {
        "Products" : Listings.objects.filter(closed_listing=False)
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

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
        watchlist_obj = Watchlist(user=user)
        watchlist_obj.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def details(request, id):
    listing = Listings.objects.get(id=id)
    comments = Comments.objects.filter(listing=listing)
    if listing is not None:
        if not listing.closed_listing:
            if request.user.is_authenticated:
                return render(request, 'auctions/details.html', {
                    "item": listing,
                    "comments":comments,
                    "Already_in_watchlist": Watchlist.objects.filter(user=request.user, products=id).exists()
                })
            else:
                return render(request, 'auctions/details.html', {
                    "item": listing,
                    "comments":comments
                })
        else:
            bids = Bid.objects.filter(listing=listing)
            if len(bids) != 0:
                winner = max({item.user.username : item.bid for item in bids})
                messages.info(request, "This Listing has been closed")
                return render(request, "auctions/details.html", {
                    "winner": winner,
                    "item": listing,
                    "comments":comments,
                    "Already_in_watchlist": Watchlist.objects.filter(user=request.user, products=id).exists()
                })
            else:
                messages.info(request, "This Listing has been closed")
                return render(request, "auctions/details.html", {
                    "item": listing,
                    "comments":comments,
                    "Already_in_watchlist": Watchlist.objects.filter(user=request.user, products=id).exists()
                })
    else:
        return HttpResponseRedirect(reverse(request.META.get("HTTP_REFERER")))

@login_required(login_url="/login")
def create_listings(request):
    if request.method == "POST":
        title = request.POST['title']
        desc = request.POST.get('Description')
        st_bid = request.POST['st_bid']
        category = request.POST['category']
        obj = Listings(title=title, description=desc, category=category, base_price=st_bid, current_price=st_bid, user=request.user, thumbnail=request.FILES.get('thumbnail'))
        obj.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, 'auctions/create.html')

@login_required(login_url="/login")
def watchlist(request):
    products = Watchlist.objects.get(user=request.user)
    return render(request, 'auctions/watchlist.html', {
        "Products": Watchlist.objects.filter(user=request.user),
        "All_Products": products.products.all()
    })

@login_required(login_url="/login")
def add_watchlist(request, pro_id):
    if Watchlist.objects.filter(user=request.user, products=pro_id).exists():
        messages.warning(request, "The item already exists in your watchlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        watchlist = Watchlist.objects.filter(user=request.user)
        for watchlist_item in watchlist:
            pass
        product = Listings.objects.filter(id=pro_id)
        for item in product:
            watchlist_item.products.add(item)
        messages.success(request, "Product Succesfully Added to watchlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url="/login")
def remove_watchlist(request, pro_id):
    if Watchlist.objects.filter(user=request.user).exists():
        watchlist = Watchlist.objects.filter(user=request.user)
        for watchlist_item in watchlist:
            pass
        product = Listings.objects.filter(id=pro_id)
        for item in product:
            watchlist_item.products.remove(item)
        messages.success(request, "Product Succesfully Removed from watchlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(request, "The item does not exist in your watchlist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def category(request, ct):
    if ct == " ":
        return render(request, 'auctions/category.html', {
            "Products" : Listings.objects.all()
        })
    else:
        objects = Listings.objects.filter(category=ct)
        if not objects.exists():
            return HttpResponseRedirect(reverse("category", kwargs={"ct": " "}))
        else:
            return render(request, 'auctions/category.html', {
                "Products": objects
            })

@login_required(login_url="/login")
def PostComment(request, pro_id):
    if request.method == "POST":
        text = request.POST.get("text")
        user = request.user
        product = Listings.objects.get(id=pro_id)
        if product is not None:
            obj = Comments(comment=text, user=user, listing=product)
            obj.save()
            messages.success(request, "Comment Posted Succesfully")
            return HttpResponseRedirect(reverse("details", kwargs={"id":pro_id}))
        else:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    else:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url="/login")
def PlaceBid(request, pro_id):
    if request.method == "POST":
        price = int(request.POST.get("price"))
        listing = Listings.objects.get(id=pro_id)
        if listing is not None:
            if price > listing.current_price:
                obj = Bid(user=request.user, listing=listing, bid=price)
                obj.save()
                listing.current_price = price
                listing.save()
                messages.success(request, "Succesfully placed bid")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, "Your bid was smaller than the current price")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url="/login")
def CloseListing(request):
    if request.method == "POST":
        id = request.POST.get("id")
        listing = Listings.objects.get(id=id)
        if request.user == listing.user:
            listing.closed_listing = True
            listing.save()
            return HttpResponseRedirect(reverse("index"))