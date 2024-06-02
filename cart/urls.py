from django.urls  import path
from cart.views import *

urlpatterns = [
    path('', cart_summary, name='cart_summary'),
    path('add/', cart_add, name='cart_add'),
    path('delete/', cart_delete, name='cart_delete'),
    path('update/', cart_update, name='cart_update'),
    path('khalti/', khalti, name="khalti"),
    path('verify/', verifyKhalti, name="verify")
]
