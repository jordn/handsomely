from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from haircuts.forms import RegisterForm, LoginForm
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from models import *
from forms import NotifyForm
import datetime
import time

def index (request):
    return render_to_response('index.html', {'path': request.path})

def coming_soon (request):
    return render_to_response('coming_soon.html', {'path': request.path})

def thanks(request):
    return render_to_response('thanks.html', {}, context_instance=RequestContext(request))

def salon_list(request):
    if request.method == 'GET':
        sex = request.GET['sex']
        list_of_salons = []
        salons = Salon.objects.all()
    if sex == 'lady':
        for salon in salons:
            if salon.womens_standard_price:
                list_of_salons.append(salon)
        if list_of_salons == []:
            list_of_salons = 'No salons were found :('
        return render_to_response('salon_list.html', {'sex' : sex, 'list_of_salons' : list_of_salons}, context_instance=RequestContext(request))
    else:
        for salon in salons:
            if salon.mens_standard_price:
                list_of_salons.append(salon)
        if list_of_salons == []:
            list_of_salons = 'No salons were found :('
        return render_to_response('salon_list.html', {'sex' : sex, 'list_of_salons' : list_of_salons}, context_instance=RequestContext(request))
    
def register(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        if request.method == 'POST':
            email_address = request.POST['email']
            confCode = User.objects.make_random_password()
            message = "Hi! Please confirm your email address by clicking here: http://www.handsome.ly/confirm?code="
            message += confCode
            message += " \nThanks, the Handsome.ly team"
            newUser = User.objects.create_user(email_address, email_address, confCode)
            newUser.first_name = confCode
            newUser.save()
            send_mail('Handsomely - Confirmation - Action Required', message, 'team@handsome.ly', [email_address], fail_silently=False)
            send_mail('Handsomely - User signup', 'Hi. A user has signed up, and has been sent a confirmation email to: ' + email_address, 'team@handsome.ly', ['team@handsome.ly'], fail_silently=False)
            return HttpResponseRedirect('/thanks/')
    else:
        form = RegisterForm(
            initial={'email': ''}
            )
    return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))


def confirm(request): #if this point is reached, the email is real. This code is the same as the old handsome.ly project (pretty much)
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
    djangoUser.username = email
    djangoUser.set_password(newPassword)
    djangoUser.save()
    findUser = User.objects.get(id = request.POST['djangoUserID'])
    new_handsomely_user = HandsomelyUser(
        django_user_id = findUser, #wtf should this be?
        gender = 'U',
        is_salon = False,
        confirmed = True
        )
    new_handsomely_user.save()
    return render_to_response("index.html", {"name" : email}, context_instance=RequestContext(request))

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # Correct password, and the user is marked "active"
                auth.login(request, user)
                # Redirect to a success page.
                return render_to_response('index.html', {}, context_instance=RequestContext(request))
    else:
        form = LoginForm(initial={'email': '', 'password': '', 'remember_me': ''})
        return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
   
def notify_customers(request):
    form = NotifyForm()
    return render_to_response('notify_customers.html', {'form': form}, context_instance=RequestContext(request))

def success(request):
    #THIS STILL NEEDS PLENTY OF WORK! need to sort out dattime objects
    #just submitting now as the appointment date and time
    #need to send emails
    #need to determine appropriate recipients
    if request.method == 'POST':
        submitting_salon = request.user
        hu = HandsomelyUser.objects.get(django_user_id = submitting_salon)
        salon_desired = Salon.objects.get(handsomely_user_id = hu.id)
        new_notification = Notification(
            salon_id = salon_desired,
            status = 'OPEN',
            appointment_date_time = datetime.datetime.now(),
            appointment_price = request.POST['discounted_price'],
            original_price = request.POST['original_price'],
            haircut_type = request.POST['gender']
            )
        new_notification.save()   
        return render_to_response('success.html', {'hu': hu}, context_instance=RequestContext(request))

		
def respond_to_notification(request):
    djangoUser = request.user
    answer = request.GET['ans']
    notifID = request.GET['notifID']
    salonMessage = request.GET['message']
    if djangoUser.is_anonymous():
        return render_to_response('login_response.html', {'answer':  answer, 'notifID' : notifID, 'message' : salonMessage}, context_instance=RequestContext(request))
    else: 
        notif = Notification.objects.get(id=notifID)
        handsomelyUserFromNotification = HandsomelyUser.objects.get(customerID=notif.customerID)
        if (handsomelyUserFromNotification.djangoUserID.id == djangoUser.id):
            notif = Notification.objects.get(id=notifID)
            salonID = notif.salonID
            salonEmail = SalonDetails.objects.get(salonID = salonID).contactEmail
            customerName = Customer.objects.get(id=notif.customerID).firstName
            customerPhone = Customer.objects.get(id=notif.customerID).mobile
            detailsNeeded = False
            if answer == "NO":
                notif.status = 'POS' 
                notif.save()
                return render_to_response('thank_you_response.html', { 'answer' : answer }, context_instance=RequestContext(request))
            if answer == "CANCEL":
                notif.status = 'CAN'
                notif.save()
                return render_to_response('thank_you_response.html', { 'answer' : answer }, context_instance=RequestContext(request))
            if answer == "YES":
                if notif.status == "POS":
                    return render_to_response('sorry.html', {}, context_instance=RequestContext(request))
                else: 
                    if ( (len(customerPhone) == 0) or (len(customerName) == 0) or ("a" in customerName) ):
                        return render_to_response('details_needed.html', { 'number' : customerPhone, 'name' : customerName, 'answer' : answer, 'notifID' : notifID, 'message' : message }, context_instance=RequestContext(request))
                    else:
                        notificationsList = Notification.objects.filter(salonID=salonID).filter(status="PEN")
                        for notification in notificationsList:
                            notification.status = "POS"
                            notification.save()
                        message = "Hi! \n\n A customer has responded to your notification and accepted the appointment."
                        message += "\n\nCustomer name: " + customerName
                        message += "\n\nCustomer number: " + customerPhone
                        message += "\n\nDetails of the appointment: " + salonMessage
                        message += "\n\nthanks,\nthe Handsome.ly team"
                        send_mail('Handsomely - Customer Responded', message, 'team@handsome.ly', [salonEmail, 'team@handsome.ly'], fail_silently=False)
                        notif.status = 'ACC'
                        notif.save()
                        requests = Request.objects.filter(customerID = notif.customerID)
                        for req in requests:
                            req.status = 'FUL'
                            req.save()
                        return render_to_response('thank_you_response.html', { 'answer' : answer, 'name' : customerName }, context_instance=RequestContext(request))
        else:
            return render_to_response('incorrect_user.html', {'answer' : answer, 'notifID' : notifID, 'message' : salonMessage, 'djuid' : djangoUser.id, 'handsomelyUserFromNotification' :  handsomelyUserFromNotification}, context_instance=RequestContext(request))

def customer_status(request):
    if request.method == 'POST':
        gender = request.POST['gender']
        salon_to_be_requested = request.POST['salon']
        #NOTE THAT THIS LINE BELOW NEEDS FIXING AS ONLY TAKING FIRST WORD OF SALON NAME
        salon_for_request = Salon.objects.get(salon_name__contains = salon_to_be_requested)
        requester = request.user #THIS DETERMINES THE ID OF WHO IS ASKING FOR A REQUEST
        try:
            hu = HandsomelyUser.objects.get(django_user_id = requester)
            new_request = Request(
                handsomely_user_id = hu,
                salon_id = salon_for_request,
                haircut_type = gender,
                status = 'WAIT',
                )
            new_request.save()
            user_details = request.user
            requests = Request.objects.filter(handsomely_user_id = hu).order_by('-start_date_time')[:10]
            return render_to_response('status.html', {'user_details' : user_details, 'requests': requests, 'salon_for_request': salon_for_request}, context_instance=RequestContext(request))
        except:
            message = 'Please log in or register to continue :)'
            return render_to_response('login.html', {'message': message}, context_instance=RequestContext(request))


def cancel_request_ajax(request):
    requestID = request.POST['reqID']
    req = Request.objects.get(id=requestID)
    req.delete()
    result = req.id
    response = HttpResponse(result)
    return response
