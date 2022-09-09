from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
    
    return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)
    

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/rubensollie%40gmail.com_djangoserver-space/capstone/get_dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = { "dealerships": dealerships }
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/rubensollie%40gmail.com_djangoserver-space/capstone/get_reviews"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context = { "reviews": reviews, "dealer_id": dealer_id }
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):    
    if request.method == "GET":
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context = {}
        context["cars"] = cars
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            review = {}
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["review"] = request.POST.get("content")
            review["purchase"] = "true" if request.POST.get("purchasecheck")== "on" else "false"
            car = CarModel.objects.get(pk=request.POST.get("car"))
            review["purchase_date"] = request.POST.get("purchasedate")
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            review["id"] = uuid.uuid4().hex[:5].upper()
            json_payload = {"review": review}
            response = post_request("https://eu-gb.functions.appdomain.cloud/api/v1/web/rubensollie%40gmail.com_djangoserver-space/capstone/add_review", json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return HttpResponse("User is not logged")
