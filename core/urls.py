from django.urls import path,include
from .views import CheckoutView,ItemDetailView,HomeView,add_to_cart,AddCouponView,remove_from_cart,OderSummaryView,remove_single_item_from_cart,PaymentView
app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(),name="home"),
    path('checkout/', CheckoutView.as_view(), name= 'checkout'),
    path('order-summary/', OderSummaryView.as_view(), name= 'order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name= 'product'),
    path('add-to-cart/<slug>/', add_to_cart, name= 'add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name= 'add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name= 'remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name= 'remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(),name= 'payment')
]