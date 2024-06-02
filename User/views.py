from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from User.models import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import  messages
from cart.cart import Cart
from User.models import Product
from django.http import JsonResponse
import json
from cart.cart import Cart
from .forms import UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
import re


# Create your views here.
def validate_password(password):
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    if re.match(pattern, password):
        return True
    else:
        return False


def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password=password)
        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop thru the cart and add the items from the database
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request, 'You are Logged In')
            return redirect('home')
        else:
            messages.success(request, 'Invalid username or password')
            return redirect('loginpage')
    return render(request, 'Users/login.html')

def logoutpage(request):
    logout(request)
    messages.success(request, 'You are Logged out')
    return redirect('home')


def signuppage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if validate_password(password):
            if password == confirm_password:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()
                customer = Customers(
                    user=user,
                    email=email,
                    password=password,
                    phone=phone,
                    first_name=first_name,
                    last_name=last_name,
                )
                customer.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(
                    request, ("Username Created - Please Fill Out Your User Info Below...")
                )
                return redirect("update_info")
            else:
                messages.error(
                    request,
                    "Password do not match",
                )
            return redirect("signuppage")
        else:
            messages.error(
                request,
                "Password must contain at least 8 characters with numeric value",
            )
            return redirect("signuppage")
    return render(request, "users/signup.html")


def category(request, name):
    # Replace Hyphens with Spaces
	# foo = foo.replace('-', ' ')
	# Grab the category from the url
    try:
        category = Category.objects.get(name=name)
        products = Product.objects.filter(category=category)
        return render(request, 'Users/category.html', {'products': products, 'category': category })
    except Category.DoesNotExist:
        messages.success(request, ("That Category Doesn't Exist..."))
        return redirect('home')


def  home(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        # Look product in DB
        product = get_object_or_404(Product, id=product_id)
        # Save to session
        cart.add(product=product)
        
        cart_quantity = cart.__len__()
        # response = JsonResponse({'Product Name ': product.name})
        products = Product.objects.all()
        return render(request, 'Users/home.html', {'products': products})
    else:
        products = Product.objects.all()
        return render(request, 'Users/home.html', {'products': products})

def  aboutus(request):
    return render(request, 'Users/aboutus.html')

def  product(request, pk):
    # product = Product.objects.get(id = pk)
    # return render(request, 'Users/product.html', { 'product' : product })
    product = get_object_or_404(Product, id=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, 'Users/product.html', {'product': product, 'related_products': related_products})


def search(request):
    if request.method == "POST":
        searchData = request.POST.get("search_product")
        if searchData != "":
            products = Product.objects.filter(name__icontains=searchData)
            if len(products) == 0:
                messages.warning(request, "Products Not Found")
                return redirect("home")
            else:
                return render(request, "Users/search.html", {"products": products})

def products(request):
    products = Product.objects.all()
    return render(request, 'Users/products.html', {'products': products})

def userprofile(request):
    customer = Customers.objects.get(user=request.user)
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    return render(
        request, "Users/userprofile.html", {"profile": profile, "customer": customer}
    )


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated!!")
            return redirect("update_user")
        return render(request, "Users/update_user.html", {"user_form": user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect("home")


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == "POST":
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect("update_user")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect("update_password")
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "Users/update_password.html", {"form": form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect("home")

def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()

            messages.success(request, "Your Info Has Been Updated!!")
            return redirect("home")
        return render(
            request,
            "Users/update_info.html",
            {"form": form, "shipping_form": shipping_form},
        )
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect("home")


def check_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            user_id = user.id
            return redirect("forgot_password", id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Email does not exist")
            return redirect("check_email")
    else:
        return render(request, "Users/check_email.html")


def forgot_password(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if validate_password(password):
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect("login_page")
            else:
                messages.error(request, "Passwords do not match")
                return redirect("forgot_password", id=id)
        else:
            messages.error(
                request,
                "Password must contain at least 8 characters with numeric value",
            )
            return redirect("forgot_password", id=id)
    else:
        return render(request, "Users/forgot_password.html")
