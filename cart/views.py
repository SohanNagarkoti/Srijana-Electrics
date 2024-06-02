import json
import uuid
import requests
from django.shortcuts import render,get_object_or_404, redirect
from cart.cart import Cart
from User.models import Product
from django.http import JsonResponse
from django.contrib import messages
# Create your views here.
def cart_summary(request):
	# Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    cart_total = cart.cart_total()  
    totals = cart_total["total"]
    product_total = cart_total["product_total"]
    uid = uuid.uuid4()
    return render(request, "Users\cart_summary.html", {"cart_products":cart_products,"quantities":quantities, "totals": totals, "product_total": product_total, "uid": uid})


def cart_add(request):
    # Get the cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # Look product in DB
        product = get_object_or_404(Product, id=product_id)
        # Save to session
        cart.add(product=product, quantity = product_qty )

        cart_quantity = cart.__len__()
        # response = JsonResponse({'Product Name ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart."))
        return response

def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		# Call delete Function in Cart
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		#return redirect('cart_summary')
		messages.success(request, ("Item Deleted From Shopping Cart."))
		return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # Save to session
        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty':product_qty})
        # return redirect('cart_summary')
        messages.success(request, ("Your Cart Has Been Updated."))
        return response


def khalti(request):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"

    return_url = request.POST.get("return_url")
    purchase_order_id = request.POST.get("purchase_order_id")
    amount = request.POST.get("amount")
    user = request.user
    payload = json.dumps(
        {
            "return_url": return_url,
            "website_url": return_url,
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            "customer_info": {
                "name": "Ram",
                "email": "abc@gmail.com",
                "phone": "9800000001",
            },
        }
    )
    headers = {
        "Authorization": "key 41ad9931c2f34162988ad7d922a45854",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        new_response = response.json()
        payment_url = new_response["payment_url"]
        return redirect(payment_url)
    except KeyError:
        # Handle the case where 'payment_url' is not in the response
        messages.error(request, "Failed to initiate payment. Please try again.")
        return redirect("billing_info")  # Redirect to an appropriate view
    except json.JSONDecodeError:
        # Handle the case where the response is not valid JSON
        messages.error(
            request, "Invalid response from payment gateway. Please try again."
        )
        return redirect("billing_info")  # Redirect to an appropriate view
    except Exception as e:
        # Handle any other exceptions
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("billing_info")  # Redirect to an appropriate view


def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == "GET":
        headers = {
            "Authorization": "key 41ad9931c2f34162988ad7d922a45854",
            "Content-Type": "application/json",
        }
        pidx = request.GET.get("pidx")
        data = json.dumps({"pidx": pidx})
        response = requests.request("POST", url, headers=headers, data=data)
        new_resposne = json.loads(response.text)

        if new_resposne["status"] == "Completed":
            messages.success(request, "Payment successful")
        else:
            messages.error(request, "Payment failed")
        return redirect("home")
