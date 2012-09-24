
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
from django.http import HttpResponse

def index(request):
    return render_to_response('index.html', {})

def about(request):
    return render_to_response('about.html', {})

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

def get_salons_opening_hours(request):
        if queryCity:
                results = SalonOpeningHours.objects.all()
        else:
                results = []
        response = HttpResponse()
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(results, ensure_ascii=False, stream=response)
        return response

def get_salons_price_menu(request):
        if queryCity:
                results = PriceMenu.objects.all()
        else:
                results = []
        response = HttpResponse()
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(results, ensure_ascii=False, stream=response)
        return response

def profile(request):
     if request.method == 'POST':
	user = request.user
	email = request.POST['email']
	user.email = email
	user.save()
     	firstName = request.POST['firstName']
     	Customer.firstName = email
     	lastName = request.POST['lastName']
     	Customer.lastName = lastName
     	defaultCity = request.POST['defaultCity']
     	Customer.defaultCity = defaultCity
     	mobile = request.POST['mobile']
     	Customer.mobile = mobile
     	notification_preferences = request.POST['notification_preferences']
     	Customer.notification_preferences = notification_preferences
     	Customer.save()
	return render_to_response('profile.html', {'firstName' : firstName, 'lastName' : lastName, 'email' : email, 'defaultCity' : defaultCity, 'mobile' : mobile, 'notification_preferences' : notification_preferences}, context_instance=RequestContext(request))
     else:
	return render_to_response('profile.html', {}, context_instance=RequestContext(request)) 

def login(request):
	return render_to_response('login.html', {})

def user_login(request):
	if request.method == 'POST':
	    username = request.POST['username']
	    password = request.POST['password']
	    user = authenticate(username=username, password=password)
	    if user is not None:
		if user.is_active:
		    login(request, user)
		    return render_to_response('profile.html', {'user': user}, context_instance=RequestContext(request))
		else:
		    pass# Return a 'disabled account' error message, added a PASS to not break the program ~jab
	    else:
		return render_to_response('login.html', {'user': user}, context_instance=RequestContext(request))
	else:
		return render_to_response('login.html', {})

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
    try: 
    	findUser = User(password == confCode)
    	email = findUser.email
    	djangoUserID = findUser.id
    	return render_to_response("account_confirmation.html", {"djangoUserID" : djangoUserID, "email" : email}, context_instance=RequestContext(request))
    except User.DoesNotExist:
	return render_to_response("invalid_confirmation.html", {}, context_instance=RequestContext(request))


def create_user(request):
    newPassword = request.POST['newPassword']
    email = request.POST['email']
    djangoUserID = request.POST['djangoUserID']
    newCustomer = Customer(firstName=" ", lastName=" ", defaultCity=" ", mobile=" ", notification_preferences="EMA")
    newCustomer.save()
    newHandsomelyUser = HandsomelyUser(djangoUserID=djangoUserID, customerID=newCustomer.id, salonID=0)
    newHandsomelyUser.save()
    return render_to_response("thank_you.html", {"name" : name}, context_instance=RequestContext(request))

# not sure what this view does...?
def notify_users(request):
	djangoUserID = request.user.id
	return render_to_response('notify_users.html', {'djangoUserID' : djangoUserID}, context_instance=RequestContext(request))

def get_notified(request):
	djangoUserID = request.user.id
	salonID = request.POST['salonID']
	return render_to_response('get_notified.html', {'djangoUserID' : djangoUserID}, context_instance=RequestContext(request))

def create_notification_request(request):
	djangoUserID = request.POST.get('userID', '')
	djangoUser = User.objects.get(id=userID) # look up salon in db to get id
	handsomelyUser = HandsomelyUser.objects.get(email=djangoUser.email) # look up handsomelyuser in db
	salonID = request.POST['salonID']
	salon = Salon.objects.get(id=salonID) # look up handsomelyuser in db
	admin_mail = 'team@handsome.ly'
	email = djangoUser.email
	newNotifReq = Request(customerID=handsomelyUser.customerID, salonID=salonID, startDate="null", status="REQ", noSoonerThan="null") # add new notification request
	newNotifReq.save()
	message = 'Thanks for using Handsomely, this is confirmation of your Handsome.ly request for'+salon.salonName
	#email user and us
	send_mail('Handsomely submission confirmation', message, admin_mail, [email, admin_mail], fail_silently=False)
	return render_to_response("thank_you.html", {"name" : name, "email" : email})

def notify_customers(request):
	djangoUser = User.objects.get(username=request.user)
	handsomelyUser = HandsomelyUser.objects.get(djangoUserID = djangoUser.id)
	salonID = handsomelyUser.salonID
	salonName = Salon.objects.get(id=salonID).salonName
	requestsList = Request.objects.get(salonID=salonID)
	admin_mail = 'team@handsome.ly'
	for request in requestsList:
		request.status = "FUL"
		request.save()
		message = 'Hi! ' + salonName
		message += ' is now free, why not head down now to avoid a queue?\n'
		message += ' Your response: <a href=\"http://www.handsome.ly/response?ans=YES\">YES</a> <a href=\"http://www.handsome.ly/response?ans=NO\">NO</a> <a href=\"http://www.handsome.ly/response?ans=CANCEL\">CANCEL</a>'
		#email user
		send_mail('Handsomely Notification', message, admin_mail, [email], fail_silently=False)
	return render_to_response("thank_you.html", {})

def for_salons(request):
	return render_to_response('for_salons.html', {}, context_instance=RequestContext(request))

def emailtest(request):
	admin_mail = 'team@handsome.ly'
	email = 'mansour@handsome.ly'
	salonName = 'Jim SoleTraders'
	message = '<html><head>Hi! </head><body>\n' + salonName
	message += ' is now free, why not head down now to avoid a queue?\n'
	message += 'Your response: \n   <a href=\"http://www.handsome.ly/response?ans=YES\">YES</a> \n   <a href=\"http://www.handsome.ly/response?ans=NO\">NO</a> \n   <a href=\"http://www.handsome.ly/response?ans=CANCEL\">CANCEL</a> <br/>'
	message += '\nThanks, \nthe Handsome.ly team</body></html>'
	send_mail('Handsomely Notification', message, admin_mail, [email], fail_silently=False)
	return render_to_response('index.html', {})

def salon_signup(request):
   	email = request.POST['email']
	message = "New salon. Their contact email: " + email
	admin_mail = 'team@handsome.ly'
	#email us
	send_mail('Handsomely - New Salon', message, admin_mail, [ admin_mail], fail_silently=False)
	return render_to_response('thank_you.html', {})

def privacy_policy(request):
    return render_to_response('privacy_policy.html', {})
