from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_request, get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
# from .models import related models
# from .models import CarModel
# from .restapis import related methods
# from .restapis import get_dealer_by_state_from_cf, get_dealer_reviews_from_cf, get_dealers_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    context = {}
    return render(request, 'djangoapp/index.html', context)

# Create an `about` view to render a static about page
def about(request):
    """ About View"""
    context = {}
    if request.method == "GET":
        about_view = render(request, 'djangoapp/about.html', context)
    return about_view


# Create a `contact` view to return a static contact page
def contact(request):
    """ Contact View """
    context = {}
    if request.method == "GET":
        contact_view = render(request, 'djangoapp/contact.html', context)
    return contact_view

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, 'djangoapp/index.html', context)

def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://292ac818.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://292ac818.us-south.apigw.appdomain.cloud/api/review"
        
        reviews_list = get_dealer_reviews_from_cf(url, dealer_id)
        #reviews_all = ' '.join([review.review for review in reviews_list])
        context["reviews_list"] = reviews_list
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

def show_review(request, dealer_id):
    context = {}
    return render(request, 'djangoapp/add_review.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    user = request.user 
    if user.is_authenticated:
        if request.method == "GET":
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            print(cars)
            context["cars"] = cars
            context["dealer_id"] = dealer_id
            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == "POST":
            url = "https://292ac818.us-south.apigw.appdomain.cloud/api/review"
            review = {}
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            carselect = request.POST["car"]
            carsel = CarModel.objects.filter(CarName=carselect)
            review["car_make"] = carsel[0].CarMake.Name
            review["car_model"] = carsel[0].CarName
            review["car_year"] = "2021"
            review["id"] = "30"
            review["name"] = request.user.first_name
            review["purchase"] = "true"
            review["purchase_date"] = request.POST["purchasedate"]
            #payload = {}
            #payload["review"] = review
            json_payload = {}
            json_payload["review"] = review
            response = post_request(url, json_payload, dealerId=dealer_id) 
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id) 