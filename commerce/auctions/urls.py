from django.urls import path

from . import views
app_name="auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create, name ="create"),
    path("<int:auction_id>", views.active, name="detail"),
    path("watchlist",views.watchlist, name="watchlist"),
    path("categories",views.categories, name="categories")
]
