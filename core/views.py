from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Item

# Create your views here.
class HomeView(ListView):
    model = Item
    template = "home-page.html"

def home(request):

    context = {
        'items': Item.objects.all()
    }
    return render(request, 'home-page.html', context)


def checkout(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'checkout-page.html', context)


def product(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'product-page.html', context)