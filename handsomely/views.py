
from django.shortcuts import render_to_response
from datetime import datetime
from models import Salon, Customer, HandsomelyUser, Request, Notification
from django.db.models import Q
from django.core import serializers
from django.utils import simplejson
from django.template import RequestContext
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import UserCreateForm

def index(request):
    return render_to_response('index.html', {})

def about(request):
    return render_to_response('about.html', {})

def for_salons(request):
    return render_to_response('salon_registration.html', {}, context_instance=RequestContext(request))

def get_salons(request):
	queryCity = request.GET.get('city', '')
	if queryCity:
		qset = ( Q(city__icontains=queryCity))
		results = Salon.objects.filter(qset).distinct()
	else:
		results = []
	response = HttpResponse()
	json_serializer = serializers.get_serializer("json")()
	json_serializer.serialize(results, ensure_ascii=False, stream=response)
	return response

def request_appointment(request):
	reqSalons = '; '.join(request.GET.getlist('salon')) # semicolon separated list of salon IDs
	return render_to_response("request_appointment.html", {"reqSalons" : reqSalons}, context_instance=RequestContext(request))

def profile(request):
    return render_to_response('profile.html', {}, context_instance=RequestContext(request))

def user_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
	    return render_to_response('auth.html', {'user': user}, context_instance=RequestContext(request))
        else:
            pass# Return a 'disabled account' error message, added a PASS to not break the program ~jab
    else:
        pass# Return an 'invalid login' error message.

def user_logout(request):
    logout(request)
    return render_to_response('index.html', context_instance=RequestContext(request)) 
	#template breaks when context_instance... isnt included?
	#...every page imports navigation.html, which has a POST form for the login
	#...any page with a POST form needs this context_instance... supplied
	#...otherwise the template engine wont run correctly, and so the page doesnt display right ...?

def register(request):
     if request.method == 'POST':
     	email = request.POST['email']
     	confCode = User.objects.make_random_password()
	message = "Hi! Please confirm your email address by clicking here: http://www.handsome.ly/confirm?code="
	message += confCode
	message += " \nThanks, the Handsome.ly team"
     	newUser = User.objects.create_user(email, email, random_pass)
     	newUser.save()
	send_mail('Handsomely - Confirmation - Action Required', message, 'team@handsome.ly', [email], fail_silently=False)
	return render_to_response('index.html', {}, context_instance=RequestContext(request))
     else:
	return render_to_response('register.html', {}, context_instance=RequestContext(request)) 

def confirm(request): #if this point is reached, the email is real
    confCode = request.GET['code']
    findUser = User(password == confCode)
    email = findUser.email
    djangoUserID = findUser.id
    return render_to_response("confirmation.html", {"djangoUserID" : djangoUserID, "email" : email}, context_instance=RequestContext(request))

def create_user(request):
    newPassword = request.POST['newPassword']
    email = request.POST['email']
    djangoUserID = request.POST['djangoUserID']
    newCustomer = Customer(firstName=" ", lastName=" ", defaultCity=" ", mobile=" ", notification_preferences="EMA")
    newCustomer.save()
    newHandsomelyUser = HandsomelyUser(djangoUserID=djangoUserID, customerID=newCustomer.id, salonID=0)
    newHandsomelyUser.save()
    return render_to_response("thank_you.html", {"name" : name}, context_instance=RequestContext(request))

def create_notification_request(request):
	djangoUserID = request.POST.get('userID', '')
	djangoUser = User.objects.get(id=userID) # look up salon in db to get id
	handsomelyUser = Salon.objects.get(email=djangoUser.email) # look up handsomelyuser in db
	salonIDList = (request.POST.get('salonIDs', '')).split('; ') # list of IDs
	admin_mail = 'team@handsome.ly'
	email = djangoUser.email
	for salonID in salonIDList:
		newNotifReq = Request(customerID=handsomelyUser.customerID, salonID=salonID, startDate="null", status="REQ", noSoonerThan="null") # add new notification request
		newNotifReq.save()
	#email user and us
		send_mail('Handsomely submission confirmation', ' Thanks for using Handsomely, this is confirmation of your Handsome.ly request for _SALON_NAME_', admin_mail, [email, admin_mail], fail_silently=False)
	return render_to_response("thank_you.html", {"name" : name, "email" : email})

def notify_customers(request):
	djangoUser = User.objects.get(username=request.user)
	handsomelyUser = HandsomelyUser.objects.get(djangoUserID = djangoUser.id)
	salonID = handsomelyUser.salonID
	requestsList = Request.objects.get(salonID=salonID)
	for request in requestsList:
		request.status = "FUL"
		request.save()
		#email user
		send_mail('Handsomely Notification', 'Hi! _SALON_NAME_ is now free, why not head down now to avoid a queue?\n', admin_mail, [email], fail_silently=False)
	return render_to_response("thank_you.html", {})
