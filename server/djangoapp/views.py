from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, post_review
import json

# Create your views here.

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        data = {"userName": username}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "User is not authenticated"}, status=400)

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = User.objects.filter(username=username).exists()
    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
    else :
        data = {"userName":username,"error":"Already Registered"}
    return JsonResponse(data)

def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200, "message": "Review added successfully"})
        except:
            return JsonResponse({"status": 500, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
    return JsonResponse({"CarModels": cars})

def dealers_view(request):
    return JsonResponse({"status": 200, "message": "This is the dealers view."})
