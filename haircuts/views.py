from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template
from django import forms
from haircuts.forms import RegisterForm, LoginForm
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #Email looks legit. Let's check it's unique.
            email_address = form.clean_username()

            #new user (they still need to confirm email). Send them a confirmation email and send them on to the requests.
            confirmation_code = User.objects.make_random_password()
            new_user = User.objects.create_user(username=email_address, email=email_address, password=confirmation_code)
            new_user.save()

            #Send them an email to confirm their email address.
            message = "Hello! \n\
            This email was just registered to be informed of any discounted haircuts in Cambridge.\n\n\
            Before we can send you notice of any appointments, Please confirm your email address by clicking here: http://www.handsome.ly/confirm?code=" + confirmation_code + "\nThanks,\n\
            Team Handsome.ly"
            send_mail(subject="Confirm your email to get your haircut deals | Handsome.ly",
            message=message, from_email='team@handsome.ly', recipient_list=[email_address], fail_silently=False)


            #Send the team an email to notify them of this momentous occasion.
            send_mail(subject='New customer signup (' + email_address + ') on Handsome.ly' ,
            message='Hey Team,\n\
             Great news! A new customer has signed up, and has been sent a confirmation email to: ' + email_address,
            from_email='team@handsome.ly', recipient_list=['team@handsome.ly'], fail_silently=False)

            return HttpResponseRedirect('/thanks/')
    else:
        form = RegisterForm()
    return render_to_response("registration/register.html", {
        'form': form,
    }, context_instance=RequestContext(request))



def confirm(request): #if this point is reached, the email is genuine. This code is the same as the old handsome.ly project (pretty much)
    confirmation_code = request.GET['code']
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

# def login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = request.POST['email']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#             if user is not None and user.is_active:
#                 # Correct password, and the user is marked "active"
#                 auth.login(request, user)
#                 # Redirect to a success page.
#                 return render_to_response('index.html', {}, context_instance=RequestContext(request))
#             else: 
#                 form = LoginForm(initial={'email': '', 'password': '', 'remember_me': ''})
#         	return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
#     else:
#         form = LoginForm(initial={'email': '', 'password': '', 'remember_me': ''})
#         return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
   
def notify(request):
    form = NotifyForm()
    salon_logged_in = request.user
    hu = HandsomelyUser.objects.get(django_user_id = salon_logged_in)
    salon_desired = Salon.objects.get(handsomely_user_id = hu.id)	
    requesters = Request.objects.filter(salon_id = salon_desired)
    male_requesters = requesters.filter(haircut_type = 'M')
    female_requesters = requesters.filter(haircut_type = 'F')
    number_male = len(male_requesters)
    number_female = len(female_requesters)
    return render_to_response('notify_customers.html', {'form': form, 'number_male': number_male, 'number_female': number_female, 'salon_desired': salon_desired}, context_instance=RequestContext(request))


# What does this function do exactly? 
def success(request):
    if request.method == 'POST':
        submitting_salon = request.user
        hu = HandsomelyUser.objects.get(django_user_id = submitting_salon)
        salon_desired = Salon.objects.get(handsomely_user_id = hu.id)
        #Get date:
        if request.POST['day'] == 'TODAY':
            date = datetime.datetime.now()
        if request.POST['day'] == 'TOMORROW':
            date = datetime.datetime.now() + datetime.timedelta(days=1)
        if request.POST['day'] == 'TDA':
            date = datetime.datetime.now() + datetime.timedelta(days=2)
        #else:
            #should put an error in here
        #Need to add error checking to return if inputs are not valid
        time_of_appointment = request.POST['time']
        extract_hour_and_min = time_of_appointment.partition(':')
        hour = extract_hour_and_min[0]
        minute = extract_hour_and_min[2]
        datetime_of_appointment = date.replace(hour = int(hour), minute=int(minute), second = 0)
        new_notification = Notification(
            salon_id = salon_desired,
            status = 'OPEN',
            appointment_date_time = datetime_of_appointment,
            appointment_price = request.POST['discounted_price'],
            original_price = request.POST['original_price'],
            haircut_type = request.POST['gender'],
            additional_info = request.POST['notes']
            )
        new_notification.save() 
        #Now send out emails
        requests_to_send = Request.objects.filter(salon_id = salon_desired)
        requests_to_send = requests_to_send.filter(status = 'WAIT')
        requests_to_send = requests_to_send.filter(haircut_type = request.POST['gender'])
        for requester in requests_to_send:
            person_to_send_to = HandsomelyUser.objects.get(django_user_id = requester.handsomely_user_id)
            message ='Hello there my friend. ' + str(submitting_salon) + ' has a free appointment at ' + str(datetime_of_appointment) + '. Usual price is ' + str(request.POST['original_price']) + '. Price through handsome.ly is ' + str(request.POST['discounted_price']) + '. The following additional information is given: ' + str(request.POST['notes']) + '. Do you fancy it? Hurry, because it is first-come; first-served!'
            send_mail('Handsomely - Appointment Available', message, 'team@handsome.ly', [person_to_send_to.django_user_id.email], fail_silently=False)
        return render_to_response('success.html', {}, context_instance=RequestContext(request))

def notify_customers(request):
    #DO NOT USE THIS- USE NOTIFY ABOVE AS IT WORKS fa 02.02.13
    # ?? ma 02.02.13
    #I mean success, not notify
	userIDFromForm = request.GET['duid']
	gender = request.GET['gender']
	day = request.GET['day']
	time = request.GET['time']
	original_price_fromForm = request.GET['original_price']
	discounted_price = request.GET['discounted_price']
	additionalInfoFromForm = request.GET['notes']
	djangoUser = User.objects.get(id=userIDFromForm)
	handsomely_user = HandsomelyUser.objects.get(django_user_id=djangoUser)
	salon = Salon.objects.get(handsomely_user_id=djangoUser)
	requestsList = Request.objects.filter(salon_id=salon.id).filter(Q(status="WAIT"))
	subject = 'Handsomely Notification'
	from_email = 'team@handsome.ly' 
	date_and_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
	date_and_time.replace(hour = time.hour)
	date_and_time.replace(hour = time.minute)
	if day == "TOMORROW":
		date_and_time += datetime.timedelta(days=1)
	elif day == "TDA": 
		date_and_time += datetime.timedelta(days=2)
	notif = Notification(salon_id=salon, status='OPEN', appointment_date_time=date_and_time, appointment_price=discounted_price, original_price=original_price_fromForm, haircut_type=gender, additional_info=additionalInfoFromForm)
	notif.save()	
	for req in requestsList:
		notif.request_ids.add(req.id)
	notif.save()
	for req in requestsList:
		req.status = "HOL"
		req.save()
		recipientHandsomelyUser = HandsomelyUser.objects.get(id = req.handsomely_user_id.id)
		recipientDjangoUser = User.objects.get(id = recipientHandsomelyUser.django_user_id.id)
		to_email = recipientDjangoUser.email
		# content
		contextMap = Context({ "users_first_name" : recipientDjangoUser.first_name, 
				       "salon_name" : salon.salon_name, 
				       "additional_info_from_salon" : additionalInfoFromForm, 
				       "notification_id" : str(notif.id),
				       "user_email" : to_email
				     })
		notification_email_text = get_template('emails/notify.txt')
		notification_email_html = get_template('emails/notify.html')
		text_content = notification_email_text
		html_content = notification_email_html
		# send email
		msg = EmailMultiAlternatives (subject, text_content, from_email, [to_email])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		msg = EmailMultiAlternatives(subject, text_content, 'team@handsome.ly', ['team@handsome.ly'])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
	result = 'done'
	response = HttpResponse(result)
	return response
		
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
            return render_to_response('status_requested.html', {'user_details' : user_details, 'requests': requests, 'salon_for_request': salon_for_request}, context_instance=RequestContext(request))
        except:
            message = 'Please log in or register to continue :)'
            return render_to_response('login.html', {'message': message}, context_instance=RequestContext(request))
    else:
      	    requester = request.user #THIS DETERMINES THE ID OF WHO IS ASKING FOR A REQUEST
      	    hu = HandsomelyUser.objects.get(django_user_id = requester)
      	    requests = Request.objects.filter(handsomely_user_id = hu).order_by('-start_date_time')[:10]
            return render_to_response('status.html', {'user_details' : requester, 'requests': requests}, context_instance=RequestContext(request))


def cancel_request_ajax(request):
    requestID = request.POST['reqID']
    req = Request.objects.get(id=requestID)
    req.delete()
    result = req.id
    response = HttpResponse(result)
    return response
