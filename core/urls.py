from django.urls import path,include
from .views import HomeView,checkout,product
app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name= 'home'),
    path('checkout/', checkout, name= 'checkout'),
    path('product/', product, name= 'product')
]