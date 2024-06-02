from django.urls  import path
from User.views import *

urlpatterns = [
    path("loginpage/", loginpage, name="loginpage"),
    path("logout/", logoutpage, name="logoutpage"),
    path("signuppage/", signuppage, name="signuppage"),
    path("", home, name="home"),
    path("product/<int:pk>", product, name="product"),
    path("update_password/", update_password, name="update_password"),
    path("update_user/", update_user, name="update_user"),
    path("update_info/", update_info, name="update_info"),
    path("aboutus/", aboutus, name="aboutus"),
    path("category/<str:name>", category, name="category"),
    path("products/", products, name="products"),
    path("search/", search, name="search"),
    path("userprofile/", userprofile, name="userprofile"),
    path("check_email/", check_email, name="check_email"),
    path("forgot_password/<int:id>/", forgot_password, name="forgot_password"),
    # path("update_user/", update_user, name="update_user"),
]
