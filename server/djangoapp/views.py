from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


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
        # Runs the "get-all-dealers" Function
        url = DEALERSHIP_API_URL
        dealerships = get_dealers_from_cf(url) # should be a list of CarDealer objs.
        get_states = []
        for dealer in dealerships:
            get_states.append(dealer.st)
        just_states = set(get_states) # deletes dupes

        context['dealers'] = dealerships
        context['states'] = sorted(just_states)
        #dealer_names = [].append([dealer.short_name for dealer in dealerships])
        #context['dealers_sn'] = dealer_names
        return render(request, 'djangoapp/index.html', context)

def get_state_dealers(request, state):
    context = {}
    if request.method == "GET":
        # Run get-state-dealers Function
        url = STATE_DEALERS_API_URL
        dealerships = get_dealer_by_state_from_cf(url, state=state)

        context['dealers'] = dealerships
        return render(request, 'djangoapp/state.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id, dealer_sn):
    context = {}
    if request.method == "GET":
        # API link for the "get-dealer-reviews" Function handling GET requests
        # Requires dealerID as kwarg
        url = REVIEW_API_URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)

        context['reviews'] = reviews
        context['dealer_id'] = dealer_id
        context['dealer_sn'] = dealer_sn
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id, dealer_sn):
    url = REVIEW_API_URL
    context = {}

    if request.method == "GET":
        cars = CarModel.objects.filter(dealership=dealer_id)
        context['cars'] = cars
        context['dealer_id'] = dealer_id
        context['dealer_sn'] = dealer_sn
        review_view = render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        # validate user
        if request.user.is_authenticated:
            # get the submitted car from DJ dataabse
            try:
                car = get_object_or_404(CarModel, pk=request.POST.get('car'))

                review = {
                    'id': random.randint(100,200),
                    'name': request.user.first_name + " " + request.user.last_name,
                    'dealership': dealer_id,
                    'review': request.POST.get('review'),
                    'purchase': request.POST.get('purchase', False),
                    'purchase_date': request.POST.get('purchase_date', None),
                    'car_make': car.car_make.name,
                    'car_model': car.name,
                    'car_year': car.car_year.year #car.year.strftime("%Y")
                }
            except Http404: # No car selected in form
                review = {
                    'id': random.randint(100,200),
                    'name': request.user.first_name + " " + request.user.last_name,
                    'dealership': dealer_id,
                    'review': request.POST.get('review'),
                    'purchase': request.POST.get('purchase', False)
                }

            json_payload = {"review": review} # to be used as request body for POST
            
            r = post_request(url, json_payload=json_payload, dealer_id=dealer_id)
            if r == 200:
                # context['status'] = 'Posted successfully!'
                print('Posted successfully!')
            else:
                context['status'] = '[{}] Something went wrong on the server.'.format(r)
        review_view = redirect('djangoapp:dealer_details', dealer_id=dealer_id, dealer_sn=dealer_sn)
    
    return review_view

