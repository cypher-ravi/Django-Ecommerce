from django.conf import settings
from django.shortcuts import render, get_object_or_404,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView,View
from django.utils import timezone
from .models import Item,Order,OrderItem,BillingAddress,Payment,Coupen
from .forms import CheckoutForm, CouponForm
from django.contrib import messages
import stripe

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


# Create your views here.
class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


class OderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object':order
            }
            return render(self.request, 'order-summary.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order")
            return redirect("/")



class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user , ordered = False) 
            # form
            form = CheckoutForm()
            context = {
                'form':form,
                'couponform':CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
            }
            return render(self.request, 'checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request,'You do not have an active order')
            return redirect("core:checkout")
        
        
       
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address =  form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                # TODO: add functionality to this fields 
                # same_Shipping_address = form.cleaned_data.get('same_Shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip_code=zip_code
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                     return redirect('core:payment', payment_option='paypal')
                else:
                    messages.error(self.request, 'Invalid payment option select!')
                    return redirect('core:checkout')

                
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order")
            return redirect("core:order-summary")

      


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "You have not added A billing adddress")
            return redirect("core:checkout")
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount= int(order.get_total() * 100)

        try:
            # Use Stripe's library to make requests...
            # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
            charge = stripe.Charge.create(
                amount= amount, #cents 
                currency="usd",
                source= token
            )
             # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            #assign payment to order
            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()

            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful!")
            return redirect("/")

      
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
            # print('Status is: %s' % e.http_status)
            # print('Type is: %s' % e.error.type)
            # print('Code is: %s' % e.error.code)
            # # param is '' in this case
            # print('Param is: %s' % e.error.param)
            # print('Message is: %s' % e.error.message)
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit Error")
            return redirect("/")
            
        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, f"{e} Invalid Parameters")
            print(e)
            return redirect("/")
            
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authenticated")
            return redirect("/")
            
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.error(self.request, " Network Error")
            return redirect("/")
        
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            messages.error(self.request,"Something went wrong! Your were not charged.Please Try again.")
            return redirect("/")
   
        except Exception as e:
        # send an email, completely unrelated to Stripe
            messages.error(self.request,"A serious error occured .we have been notified!")
            return redirect("/")    

   


def product(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'product-page.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created  = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False 
        )
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,'This item quantity was updated in your cart')
            return redirect("core:order-summary")
        else:
            messages.info(request,'This item was added to your cart')
            order.items.add(order_item)
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,'This item was added to your cart')
        return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug  =item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False 
                )[0]
            order.items.remove(order_item)
            messages.info(request,'This item was remove from your cart')
            return redirect("core:order-summary")
        else:
            messages.info(request,'This item was not in your cart')
            return redirect("core:product",slug=slug)
    else:
        messages.info(request,'You do not have an active order')
        return redirect("core:product",slug=slug)



@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False 
                )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
                # messages.info(request,'This item was remove from your cart') 
            messages.info(request,'This item quantity was updated')
            return redirect("core:order-summary")
        else:
            messages.info(request,'This item was not in your cart')
            return redirect("core:product",slug=slug)
    else:
        messages.info(request,'You do not have an active order')
        return redirect("core:product",slug=slug)
    return redirect("core:product",slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupen.objects.get(code=code) 
        return coupon
    except ObjectDoesNotExist:
        messages.info(request,'This coupon does not exist')
        return redirect("core:checkout")
       

    

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user = self.request.user , ordered = False) 
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request,'Successfully! applied coupon.')
                return redirect("core:checkout")
            
            
            except ObjectDoesNotExist:
                messages.info(self.request,'You do not have an active order')
                return redirect("core:checkout")
   