from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models.base import ObjectDoesNotExist

from .models import User, Listings, Bids, Comments
from datetime import datetime, timezone
import pytz

# render homepage for user
def index(request):
    # get current listings from database
    listings = Listings.objects.exclude(active=False).all().order_by("-time")
    paginator = Paginator(listings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        return render(request, "auctions/index.html", {
            "title": "Auctions",
            "listings": page_obj,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })
    else:
        return render(request, "auctions/index.html", {
            "title": "Auctions",
            "listings": page_obj
        })

# render login page for users
def login_view(request):
    # if user reach route via POST method as by submitting form
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
    # if user reach route via GET method
    else:
        # only allow user to reach login page if not already logged in
        if not request.user.is_authenticated:
            return render(request, "auctions/login.html")
        # else redirect user to homepage
        else:
            return HttpResponseRedirect(reverse("index"))


# render logout page for user
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# render register page for users
def register(request):
    # only allow user to reach register page if not already logged in
    if not request.user.is_authenticated:
        # if user reach route via POST method as by submitting a form
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            # Ensure password matches confirmation
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
            return HttpResponseRedirect(reverse("index"))

        # if user reach route via GET method
        else:
            return render(request, "auctions/register.html")
    # else redirect user to homepage
    else:
        return HttpResponseRedirect(reverse("index"))

# allow users to change password
def change_password(request):
    # only allow authenticated user to change password
    if request.user.is_authenticated:

        # if user reach route via POST method as by submitting a form
        if request.method == "POST":
            # get all required fields
            old_password = request.POST["old_password"]
            new_password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            # new password must be different from old password
            if old_password == new_password:
                return render(request, "auctions/change_password.html", {
                    "message": "New passwords must be different from old password.",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })

            # check if user enter correct old password
            if authenticate(request, username=request.user.username, password=old_password) is None:
                return render(request, "auctions/change_password.html", {
                    "message": "Old password is not correct.",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })

            # Ensure password matches confirmation
            if new_password != confirmation:
                return render(request, "auctions/change_password.html", {
                    "message": "New passwords must match.",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })

            # attempt to change password
            user = User.objects.get(username__exact=request.user.username)
            user.set_password(new_password)
            user.save()

            # ask user to log in again
            logout(request)
            return render(request, "auctions/login.html", {
                "message": "Successfully change password. Please login again"
            })

        # if user reach route via GET method
        else:
            return render(request, "auctions/change_password.html")

    else:
        return HttpResponseRedirect(reverse("login"))

# render a new page for user to add listings
def create_listings(request):
    # only allow logged in user to reach create page page
    if request.user.is_authenticated:
        # if user reach route via POST method as by submitting a form
        if request.method == "POST":
            # get all listing details
            listing = request.POST["listing"].capitalize()
            description = request.POST["description"]
            category = request.POST["category"].upper()
            bid = request.POST["bid"]
            picture = request.POST["picture"]

            # listing must not contain '/'
            if '/' in listing:
                return render(request, "auctions/create_listing.html", {
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count(),
                    "message": "Listing title must not contain special character '/'",
                    "listing": listing,
                    "description": description,
                    "category": category,
                    "bid": bid,
                    "picture": picture
                })

            # check if there is already a listing of the same name
            try:
                same_listing = Listings.objects.get(title=listing)
                return render(request, "auctions/create_listing.html", {
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count(),
                    "message": "There is already a listing with the same title. Please try again",
                    "listing": listing,
                    "description": description,
                    "category": category,
                    "bid": bid,
                    "picture": picture
                })
            except ObjectDoesNotExist:
                # give grumpy cat if user didn't provide image link
                if (picture == ""):
                    picture += 'https://i.imgur.com/CsCgN7Ll.png'

                # create new listing object
                new_listing = Listings.objects.create(
                    title=listing, description=description, category=category, picture=picture, bid=bid, user=request.user)

                # redirect user to homepage
                return HttpResponseRedirect(reverse("index"))

        # if user reach route via GET method
        else:
            return render(request, "auctions/create_listing.html", {
                "watchlist_count": request.user.watchlist.count(),
                "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                "listing_count": request.user.users_listings.count()
            })
    # else redirect user to login page
    else:
        return HttpResponseRedirect(reverse("login"))

# render a page that show details on each listing
def view_listings(request, title):

    # get all biddings on current listing
    try:
        listings = Listings.objects.get(pk=title)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Listing not existed."}, status=404)

    bids = Bids.objects.filter(listing=title).values_list('bid', flat=True)
    message = ""
    winner_message = ""

    # if there are bids on listing, check if current user has the highest bid
    # get the max bid on item
    max_bid = max(bids) if bids else 0
    if request.user.is_authenticated:

        # if there is a max bid
        if (max_bid):
            highest_user = Bids.objects.get(listing=title, bid=max_bid).user

            # if user has the highest bid, let user know
            if request.user == highest_user:
                message += "You have the highest bid"

                # if user has the highest bid and bidding over, user wins
                if not listings.active:
                    winner_message += "Congratulations, you have won the auction"

            # if user is not the highest bid
            else:
                # if user doesn't have the highest bid and bidding over, user loses
                if not listings.active:
                    # if user bids and loses
                    if User.objects.get(username=request.user.username).id in Bids.objects.filter(listing=title).values_list('user', flat=True):
                        winner_message += "Bidding over. You didn't win"
                else:
                    if User.objects.get(username=request.user.username).id in Bids.objects.filter(listing=title).values_list('user', flat=True):
                        message += "You don't have the highest bid"
                    else:
                        message += "Place your bid below for a chance to win"
        # if there is no max bid
        else:
            # if listing no longer active
            winner_message += "This listing is no longer active"

    # if user is not logged in
    else:
        if not listings.active:
            winner_message += "This listing is no longer active"
        else:
            winner_message += "You need to log in to bid"

    # get all comments on this listing
    comments = Comments.objects.filter(listing=title).order_by('-time')
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "listing": listings,
            "price": f"{max_bid if max_bid else Listings.objects.get(pk=title).bid:,}",
            "watchlist": User.objects.get(username=request.user) in Listings.objects.get(title=title).watchlist.all(),
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count(),
            "bids": len(bids),
            "if_bid": User.objects.get(username=request.user.username).id in Bids.objects.filter(listing=title).values_list('user', flat=True),
            "message": message,
            "winner_message": winner_message,
            "comments": page_obj,
            # check if logged in user is owner
            "is_owner": request.user == Listings.objects.get(title=title).user
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listings,
            "price": f"{max_bid if max_bid else Listings.objects.get(pk=title).bid:,}",
            "bids": len(bids),
            "comments": page_obj,
            "winner_message": winner_message
        })

# add listing to user's watchlist
def add_watchlist(request, title, user):

    # only allow logged in user to view add to watchlist
    if request.user.is_authenticated:
        user = User.objects.get(username=user)
        listing = Listings.objects.get(title=title)

        # if listing is not in user's watchlist, add
        if user not in listing.watchlist.all():
            listing.watchlist.add(user)
        # if listing is already in user's watchlist, remove
        else:
            listing.watchlist.remove(user)

        return HttpResponseRedirect(reverse("listing", args=(title, )))

    # else redirect user to login page
    else:
        return HttpResponseRedirect(reverse("login"))

# render a page that shows user's watchlist
def view_watchlist(request, user):

    # only allow logged in user to view watchlist
    if request.user.is_authenticated:
        user = User.objects.get(username=user)

        watchlists = user.watchlist.all().order_by("-time")
        paginator = Paginator(watchlists, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "auctions/watchlist.html", {
            "title": "watchlist",
            "watchlists": page_obj,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })

    # else redirect user to login page
    else:
        return HttpResponseRedirect(reverse("login"))


# render a page that shows all categories
def category(request):
    category = list(dict.fromkeys(Listings.objects.exclude(
        active=False).values_list('category', flat=True)))
    paginator = Paginator(category, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        return render(request, "auctions/category.html", {
            "categories": page_obj,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })
    else:
        return render(request, "auctions/category.html", {
            "categories": page_obj
        })

# render a page that shows all listings within category
def get_category(request, category):
    listings = Listings.objects.filter(category=category).exclude(
        active=False).all().order_by("-time")
    paginator = Paginator(listings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        return render(request, "auctions/category_listings.html", {
            "listings": page_obj,
            "category": category,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })
    else:
        return render(request, "auctions/category_listings.html", {
            "listings": page_obj,
            "category": category
        })

# allow user to bid on listing
def bid(request, title):
    # only allow authenticated user to bid
    if request.user.is_authenticated:
        # only allow user reach route via POST as by submitting a form
        if request.method == "POST":
            # get new bid
            if request.POST["bid"] == '':
                return render(request, "auctions/invalid_bids.html", {
                    "title": "invalid bids",
                    "listing": title,
                    "message": "Your bid must not be empty",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })
            else:
                new_bid = float(request.POST["bid"])

            # check if new bids is higher than starting price
            if new_bid < Listings.objects.get(title=title).bid:
                return render(request, "auctions/invalid_bids.html", {
                    "title": "invalid bids",
                    "listing": title,
                    "message": "Your bid is lower than starting price, please try again",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })

            # check if new bids is not greater than any current bids
            bids = Bids.objects.filter(
                listing=title).values_list('bid', flat=True)
            max_bid = max(bids) if bids else 0
            if new_bid <= max_bid:
                return render(request, "auctions/invalid_bids.html", {
                    "title": "invalid bids",
                    "listing": title,
                    "message": "Someone else already bids higher than you",
                    "watchlist_count": request.user.watchlist.count(),
                    "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                    "listing_count": request.user.users_listings.count()
                })

            # otherwise, allow user to bid
            try:
                Bids.objects.create(listing=Listings.objects.get(
                    pk=title), bid=new_bid, user=request.user)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Server can't process your bid. Please try again later."}, status=400)
            return HttpResponseRedirect(reverse("listing", args=(title, )))
    else:
        return HttpResponseRedirect(reverse("login"))

# allow listing owner to close listing
def close(request, title):
    # only allow authenticated user to close
    if request.user.is_authenticated:
        # check if logged in user is owner of listing
        listing = Listings.objects.get(pk=title)
        if request.user != listing.user:
            return HttpResponseRedirect(reverse("listing", args=(title, )))
        # change listing status to close
        else:
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(title, )))
    else:
        return HttpResponseRedirect(reverse("login"))

# allow listing owner to delete listing
def delete(request, title):
    # only allow authenticated user to close
    if request.user.is_authenticated:
        # check if logged in user is owner of listing
        listing = Listings.objects.filter(pk=title)
        if request.user != listing[0].user:
            return HttpResponseRedirect(reverse("listing", args=(title, )))
        # change listing status to close
        else:
            listing.delete()
            return HttpResponseRedirect(reverse("my_listings"))
    else:
        return HttpResponseRedirect(reverse("login"))

# allow users to comment on each listing
def comment(request, title):
    # only allow authenticated user to comment
    if request.user.is_authenticated:
        # only allow user to reach route via POST
        if request.method == "POST":
            comment = request.POST["comment"]
            try:
                Comments.objects.create(listing=Listings.objects.get(
                    title=title), user=request.user, comment=comment)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Server can't process your comment. Please try again later."}, status=400)
            return HttpResponseRedirect(reverse("listing", args=(title, )))
        else:
            return HttpResponseRedirect(reverse("listing", args=(title, )))
    else:
        return HttpResponseRedirect(reverse("login"))

# allow users to delete comment
def delete_comment(request, title, id):
    # only allow authenticated user to delete comment
    if request.user.is_authenticated:
        listing = Listings.objects.get(title=title)
        comment = Comments.objects.get(listing=listing, id=id)

        comment.delete()
        return HttpResponseRedirect(reverse("listing", args=(title, )))
    else:
        return HttpResponseRedirect(reverse("listing", args=(title, )))

# allow users to view their own listings list
def my_listings(request):
    # only allow authenticated user to view their own listing
    if request.user.is_authenticated:
        # get all user's listings
        listings = Listings.objects.filter(
            user=request.user).all().order_by("-time")
        paginator = Paginator(listings, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "auctions/my_listings.html", {
            "title": "Portfolio",
            "listings": page_obj,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })
    else:
        return HttpResponseRedirect(reverse("login"))

# allow users to view listings they bid on
def bid_list(request):
    # only allow authenticated user to view their own listing
    if request.user.is_authenticated:
        # get all user's listings
        listings = Listings.objects.filter(title__in=Bids.objects.filter(
            user=request.user).values_list('listing', flat=True)).all().order_by("-time")
        if not listings:
            message = "You haven't bid on any items"

        paginator = Paginator(listings, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "auctions/my_biddings.html", {
            "title": "My Biddings",
            "listings": page_obj,
            "watchlist_count": request.user.watchlist.count(),
            "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
            "listing_count": request.user.users_listings.count()
        })
    else:
        return HttpResponseRedirect(reverse("login"))

# allow users to search for listing
def search(request):
    # only allow search page via POST
    if request.method == "POST":
        # get all post containing user's input
        title = Listings.objects.filter(
            title__icontains=request.POST["q"]).all()
        category = Listings.objects.filter(
            category__icontains=request.POST["q"]).all()

        # paginate search results
        search_result = []
        for i in title:
            if i not in search_result:
                search_result.append(i)
        for i in category:
            if i not in search_result:
                search_result.append(i)

        paginator = Paginator(search_result, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if request.user.is_authenticated:
            return render(request, "auctions/search_results.html", {
                "title": "Search",
                "listings": page_obj,
                "query": request.POST["q"],
                "watchlist_count": request.user.watchlist.count(),
                "bidding_count": Listings.objects.filter(title__in=Bids.objects.filter(user=request.user).values_list('listing', flat=True)).count(),
                "listing_count": request.user.users_listings.count()
            })
        else:
            return render(request, "auctions/search_results.html", {
                "title": "Search",
                "listings": page_obj,
                "query": request.POST["q"]
            })

# allow users to delete bids
def delete_bids(request, title):
    # only allow authenticated user to delete biddings
    if request.user.is_authenticated:
        listing = Listings.objects.get(title=title)
        bids = Bids.objects.filter(listing=listing, user=request.user)
        bids.delete()

        return HttpResponseRedirect(reverse("listing", args=(title, )))
    else:
        return HttpResponseRedirect(reverse("listing", args=(title, )))

# convert timezone
def utc_to_local(utc_dt):
    tz = pytz.timezone('Australia/Sydney')
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=tz)
