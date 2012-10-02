
from django.shortcuts import render_to_response
from datetime import datetime
from models import *
from django.db.models import Q
from django.core import serializers
from django.utils import simplejson
from django.template import RequestContext
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

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
	salonID = request.GET['salonID']
        results = SalonOpeningHours.objects.filter(salonID=salonID)
        response = HttpResponse()
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(results, ensure_ascii=False, stream=response)
        return response

def get_salons_price_menu(request):
	salonID = request.GET['salonID']
        results = PriceMenu.objects.get(salonID=salonID)
        results = PriceMenu.objects.all()
        response = HttpResponse()
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(results, ensure_ascii=False, stream=response)
        return response

def profile(request):
	user = request.user
	djangoUserID = user.id
	handUser = HandsomelyUser.objects.get(djangoUserID = user)
	salonID = handUser.salonID
	cust = Customer.objects.get(id=handUser.customerID)
	return render_to_response('profile.html', {'djangoUserID' : djangoUserID, 'salonID' : salonID, 'cust' : cust, 'handUser' : handUser}, context_instance=RequestContext(request))
	
def update_profile(request):
	user = request.user
	handUser = HandsomelyUser.objects.get(id=user.id)
	cust = Customer.objects.get(id=handUser.customerID)
	salonID = handUser.salonID
	email = request.POST['email']
	user.email = email
	user.save()
	firstName = request.POST['firstName']
	cust.firstName = firstName
	lastName = request.POST['lastName']
	cust.lastName = lastName
	defaultCity = request.POST['defaultCity']
	cust.defaultCity = defaultCity
	mobile = request.POST['mobile']
	cust.mobile = mobile
	notification_preferences = request.POST['notification_preferences']
	cust.notification_preferences = notification_preferences
	cust.save()
	return render_to_response('profile.html', {'user': user, 'handUser' : handUser, 'cust' : cust, 'salonID' : salonID}, context_instance=RequestContext(request))

def login_page(request):
	return render_to_response('login.html', {})

def user_login(request):
	if request.method == 'POST':
	    email = request.POST['email']
	    password = request.POST['password']
	    user = authenticate(username=email, password=password)
	    if user is not None:
		if user.is_active:
		    login(request, user)
		    handUser = HandsomelyUser.objects.get(djangoUserID=user.id)
		    salonID = handUser.salonID
		    cust = Customer.objects.get(id=handUser.customerID)
		    return render_to_response('profile.html', {'user': user, 'handUser' : handUser, 'cust' : cust, 'salonID' : salonID}, context_instance=RequestContext(request))
		else:
		    pass# Return a 'disabled account' error message, added a PASS to not break the program ~jab
	    else:
	    	errorMessage = "Wrong username or password"
		return render_to_response('login.html', {'emailAdd': email, 'message' : errorMessage}, context_instance=RequestContext(request))
	else:
		return render_to_response('login.html', {}, context_instance=RequestContext(request))

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
     	newUser = User.objects.create_user(email, email, confCode)
	newUser.first_name = confCode
     	newUser.save()
	send_mail('Handsomely - Confirmation - Action Required', message, 'team@handsome.ly', [email], fail_silently=False)
	return render_to_response('index.html', {}, context_instance=RequestContext(request))
     else:
	return render_to_response('register.html', {}, context_instance=RequestContext(request)) 

def confirm(request): #if this point is reached, the email is real
    confCode = request.GET['code']
    try: 
    	findUser = User.objects.get(first_name = confCode)
	findUser.first_name = " "
    	email = findUser.email
    	djangoUserID = findUser.id
	findUser.save()
    	return render_to_response("account_confirmation.html", {"djangoUserID" : djangoUserID, "email" : email}, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
	return render_to_response("invalid_confirmation.html", {"confCode" : confCode}, context_instance=RequestContext(request))


def create_user(request):
    newPassword = request.POST['newPassword']
    email = request.POST['email']
    djangoUserID = request.POST['djangoUserID']
    djangoUser = User.objects.get(id = djangoUserID)
    newCustomer = Customer(firstName=email, lastName=" ", defaultCity=" ", mobile=" ", notification_preferences="EMA")
    newCustomer.save()
    newHandsomelyUser = HandsomelyUser(djangoUserID=djangoUser, customerID=newCustomer.id, salonID=0)
    newHandsomelyUser.save()
    djangoUser.username = email
    djangoUser.set_password(newPassword)
    djangoUser.save()
    return render_to_response("thank_you.html", {"name" : email}, context_instance=RequestContext(request))

def big_red_button(request):
	djangoUserID = request.user.id
	return render_to_response('notify_users.html', {'djangoUserID' : djangoUserID}, context_instance=RequestContext(request))

def get_notified(request):
	djangoUserID = request.user.id
	salonID = request.POST['salonID']
	return render_to_response('get_notified.html', {'djangoUserID' : djangoUserID}, context_instance=RequestContext(request))

def create_notification_request(request):
	djangoUserID = request.GET.get('djangoUserID', '')
	djangoUser = User.objects.get(id=djangoUserID) # look up salon in db to get id
	handsomelyUser = HandsomelyUser.objects.get(email=djangoUser.email) # look up handsomelyuser in db
	salonID = request.GET.get('salonID', '')
	salon = Salon.objects.get(id=salonID) # look up handsomelyuser in db
	admin_mail = 'team@handsome.ly'
	email = djangoUser.email
	# add new notification request
	newNotifReq = Request(customerID=handsomelyUser.customerID, salonID=salonID, startDate="null", status="REQ", noSoonerThan="null") 
	newNotifReq.save()
	message = 'Thanks for using Handsomely, this is confirmation of your Handsome.ly request for '+salon.salonName
	#email user and us
	send_mail('Handsomely submission confirmation', message, admin_mail, [email, admin_mail], fail_silently=False)
	return render_to_response("thank_you.html", {"name" : djangoUser.email})

def notify_customers(request):
	userIDFromForm = request.POST['djangoUserID']
	djangoUser = User.objects.get(id=userIDFromForm)
	handsomelyUser = HandsomelyUser.objects.get(djangoUserID = djangoUser)
	salonID = handsomelyUser.salonID
	salon = Salon.objects.get(id=salonID)
	requestsList = Request.objects.filter(salonID=salonID).filter(status="REQ")
	subject = 'Handsomely Notification'
	from_email = 'team@handsome.ly' 
	for req in requestsList:
		req.status = "FUL"
		req.save()
		recipientHandsomelyUser = HandsomelyUser.objects.get(customerID = req.customerID)
		recipientDjangoUser = User.objects.get(id = recipientHandsomelyUser.djangoUserID.id)
		custID = recipientHandsomelyUser.customerID
		notif = Notification(customerID = custID, salonID = salonID, timeSent = datetime.now(), timeReplied = date.max, status = 'PEN')
		notif.save()
		#email user
		to_email = recipientDjangoUser.email
		text_content = 'Hi! ' + recipientDjangoUser.first_name
		text_content += 'The salon ' + salon.salonName + ' is now free, why not head down now to avoid a queue?\n'
		text_content += ' Your response: Yes: http://www.handsome.ly/response?ans=YES&notifID=' + str(notif.id) 
		text_content += ' -- No: http://www.handsome.ly/response?ans=NO&notifID=' + str(notif.id) 
		text_content += ' -- Cancel: http://www.handsome.ly/response?ans=CANCEL&notifID=' + str(notif.id)
		# html email
		html_content = 'Hi ' + recipientDjangoUser.first_name
		html_content += '!<br/>'
		html_content += 'The salon <b>' + salon.salonName 
		html_content += '</b> is now free, why not head down now to avoid a queue?<br/>'
		html_content += ' Your response: <a href=\"http://www.handsome.ly/response/?ans=YES&notifID=' + str(notif.id) 
		html_content += '\">YES</a> <a href=\"http://www.handsome.ly/response/?ans=NO&notifID=' + str(notif.id) 
		html_content += '\">NO</a> <a href=\"http://www.handsome.ly/response/?ans=CANCEL&notifID=' + str(notif.id) 
		html_content += '\">CANCEL</a> <br/>'
		html_content += '<br/>Thanks, <br/>the Handsomely team.'
		# send email
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
	return render_to_response("thank_you.html", {'name' : djangoUser.email})

def response(request):
	answer = request.GET['ans']
	notifID = request.GET['notifID']
	notif = Notification.objects.get(id=notifID)
	if answer == "YES":
		notif.status = 'ACC'
	if answer == "NO":
		notif.status = 'POS' 
	if answer == "CANCEL":
		notif.status = 'CAN'
	notif.save()
	return render_to_response('thank_you.html', {}, context_instance=RequestContext(request))

def for_salons(request):
	return render_to_response('for_salons.html', {}, context_instance=RequestContext(request))

def salon_signup(request):
   	email = request.POST['email']
	message = "New salon. Their contact email: " + email
	admin_mail = 'team@handsome.ly'
	#email us
	send_mail('Handsomely - New Salon', message, admin_mail, [ admin_mail], fail_silently=False)
	return render_to_response('thank_you.html', {})

def privacy_policy(request):
    return render_to_response('privacy_policy.html', {})
