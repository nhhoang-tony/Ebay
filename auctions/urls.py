from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"), # homepage
    path("login", views.login_view, name="login"), # login page
    path("logout", views.logout_view, name="logout"), # logout page
    path("register", views.register, name="register"), # register page
    path("create", views.create_listings, name="create"), # create a new listing page
    path("listing/<str:title>", views.view_listings, name="listing"), # lead users to detail listings
    path("addwatchlist/<str:title>/<str:user>", views.add_watchlist, name="add_watchlist"),
    path("watchlist/<str:user>", views.view_watchlist, name="watchlist"), # add listing to user's watchlist
    path("category", views.category, name="category"), # show a list of categories
    path("category/<str:category>", views.get_category, name="get_category"), # get a list of items within category
    path("bid/<str:title>", views.bid, name="bid"), # allow user to bid on listing
    path("close/<str:title>", views.close, name="close"), # allow listing owner to close listing
    path("delete/<str:title>", views.delete, name="delete"), # allow listing owner to delete listing after close
    path("comment/<str:title>", views.comment, name="comment"), # allow users to comment on each listing
    path("my_listings", views.my_listings, name="my_listings"), # allow users to see their listings portfolio
    path("bid_list", views.bid_list, name="bid_list"), # allow users to see listings they bid on
    path("change_password", views.change_password, name="change_password"), # allow users to change password
    path("delete_comment/<str:title>/<int:id>", views.delete_comment, name="delete_comment"), # allow users to delete comment
    path("search", views.search, name="search"), # allow users to search for listings
    path("delete_bids/<str:title>", views.delete_bids, name="delete_bids") # allow users to delete biddings
]
