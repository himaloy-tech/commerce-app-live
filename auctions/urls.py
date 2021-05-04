from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("details/<int:id>", views.details, name="details"),
    path('create_listings', views.create_listings, name="create_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_watchlist/<int:pro_id>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:pro_id>", views.remove_watchlist, name="remove_watchlist"),
    path("c/<str:ct>", views.category, name="category"),
    path("PostComment/<int:pro_id>", views.PostComment, name="PostComment"),
    path("PlaceBid/<int:pro_id>", views.PlaceBid, name="PlaceBid"),
    path("CloseListing", views.CloseListing, name="CloseListing")
]