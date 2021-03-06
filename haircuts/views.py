from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django import forms
from haircuts.forms import RegisterForm, LoginForm, RequestForm, NotificationForm, NotifyForm
from haircuts.models import *
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import auth, messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import base36_to_int

import datetime
import time

def test (request):
    return render_to_response('appointments/appointment_offer_email.html', context_instance=RequestContext(request))


#front page and haircut type selection
def index (request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def about (request):
    return render_to_response('about.html', context_instance=RequestContext(request))

#After choosing haircut type. Choose which salons you'd like to hear form.
def salons(request):
    if 'haircut' in request.GET and request.GET['haircut']:
        haircut = request.GET['haircut']
    else:
        haircut = None

    #Crmmy workaround to show the right prices
    if haircut=='lady':
        is_womens = True
    elif haircut=='gent':
        is_womens = False
    else:
        #send them a form to choose their haircut type.
        is_womens = False
        haircut="please select your haircut"
        return redirect('/', context_instance=RequestContext(request))

    list_of_salons = [] #Salons to show
    salons = Salon.objects.all()

    # In the future haircuts may be a seperate table, but at the moment male and female cuts are hardcoded into the salon table (KISS)
    for salon in salons:
        if haircut == 'lady' and salon.womens_standard_price:
            list_of_salons.append(salon)
        elif haircut == 'gent' and salon.mens_standard_price:
            list_of_salons.append(salon)

    if list_of_salons == []:
        #No salons foudn :(
        pass

    return render_to_response('salon_list.html', {'haircut' : haircut, 'is_womens' : is_womens, 'list_of_salons' : list_of_salons}, context_instance=RequestContext(request))


def add_haircut_request(request):
    django_user = request.user
    if django_user.is_authenticated():
        if ('haircut_type' in request.POST and request.POST['haircut_type']
            and 'salon' in request.POST and request.POST['salon']):

            salon = request.POST['salon']
            haircut_type = request.POST['haircut_type'] # M or F
            try:
                salon = Salon.objects.get(id = salon)
                assert haircut_type in ('M', 'F')
            except (ValueError, Salon.DoesNotExist):
                messages.error(request, "Salon doesnt exist")
                return redirect('/status/')
            except(AssertionError):
                messages.error(request, "Haircut doesnt exist")
                return redirect('/status/')

            active_similar_requests = Request.objects.filter(django_user=django_user, salon=salon, haircut_type=haircut_type, status='WAIT')

            if active_similar_requests:
                messages.info(request, ('Your request for a <strong>' + haircut_type +'</strong> haircut at <strong>'
                 + str(salon) + '</strong> is still waiting. Any available appointments will be sent to you at <strong>' + django_user.email +'</strong>.'))
                return redirect('/status/')

            new_request = Request(
                django_user = django_user,
                salon = salon,
                haircut_type = haircut_type,
                status = 'WAIT',
                )
            new_request.save()
            messages.info(request, ('Your request for a <strong>' + new_request.haircut_type +'</strong> haircut at <strong>'
             + str(new_request.salon) + '</strong> has been added.  Any available appointments will be sent to you at <strong>' + django_user.email +'</strong>.'))

        return redirect('/status')
    else:
        return redirect('/')


def cancel_haircut_request(request):
    django_user = request.user
    if django_user.is_authenticated():

        if ('reqID' in request.POST and request.POST['reqID']):
            haircut_request_id = request.POST['reqID']
            haircut_request = Request.objects.get(id=haircut_request_id)
            print "POST"
            if haircut_request.django_user == django_user: 
                haircut_request.status = 'CANC'
                haircut_request.save() 
                return HttpResponse(haircut_request.id) 

        return redirect('/status')
    else:
        return redirect('/')


# Page to show current status of requests
def customer_status(request):
    django_user = request.user
    c = {'needs_confirming': False}
    c['user_details'] = django_user
    if django_user.is_authenticated():
        try:
            handsomely_user = HandsomelyUser.objects.get(django_user=django_user)
            if not handsomely_user.confirmed:
                messages.error(request, 'You need to <strong>confirm your email ('+ django_user.email +')</strong> before you receive notifications. Please check your inbox.')
        except (ValueError, HandsomelyUser.DoesNotExist):
            user = None
            return redirect('/admin') #Most likely an admin account!

        haircut_requests = Request.objects.filter(django_user = django_user).order_by('-start_date_time')[:10]
        c['haircut_requests'] = haircut_requests
        return render_to_response('status.html', c, context_instance=RequestContext(request))
    else:
        return redirect('/login/', context_instance=RequestContext(request))


# Registration form.
# Username is email, password is random and confirmation email comes from the 'forgot password' default with different templates.
def register(request):
    #form gets submitted by email. If it's new a new user is created (with random password) and a password reset form is sent to the user's email.
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #Email looks legit and unique. New user! (they still need to confirm email). Send them a confirmation email and send them on to the requests.
            email_address = form.clean_email()
            random_password = User.objects.make_random_password()

            # Create new user. This gets auto added to the DB
            new_user = User.objects.create_user(username=email_address, email=email_address, password=random_password)

            #Create a handsomely profile for them. Is_confirmed set to FALSE.
            create_handsomely_user(new_user, email_confirmed=False)

            #log them in (they won't get notified of appointments until email is confirmed hopefully. NB. log in BEFORE password reset as password reset code uses last login date)
            login_user = authenticate(username=email_address, password=random_password)
            login(request, login_user)

            # Send the team an email to notify them of this momentous occasion.
            c = {
                'email_address': email_address,
                'request': request,
                'user': new_user,
            }
            team_email = loader.render_to_string('registration/new_user_handsomely_team_email.html', c)
            send_mail(subject='Handsome.ly team: New customer signup (' + email_address + ')',
                message=team_email,
                from_email='team@handsome.ly',
                recipient_list=['team@handsome.ly']
                )

            #Send the new user an email to confirm and set a password! This uses the django auth reset password stuff
            password_reset(request, 
                email_template_name='registration/new_user_confirm_email.html',
                 subject_template_name='registration/new_user_confirm_email_subject.txt'
                 )

            #If they've come with a haircut request add it.
            if ('haircut_type' in request.POST and request.POST['haircut_type']
                and 'salon' in request.POST and request.POST['salon']):
                add_haircut_request(request)

            messages.debug(request, 'Came from register.')

            #Push them on their way. They can go anywhere they just need to be notified that they need to confirm their email.
            return redirect('/status', context_instance=RequestContext(request))

    else:
        form = RegisterForm()

    #If we've got haircut detaisl we've got a slightly different form.
    if ('haircut_type' in request.GET and request.GET['haircut_type']
        and 'salon' in request.GET and request.GET['salon']):
        haircut_type, salon = request.GET['haircut_type'], request.GET['salon']

        return render_to_response("registration/register_and_request.html", {
        'form': form, 'haircut_type':haircut_type, 'salon':salon
        }, context_instance=RequestContext(request))

    return render_to_response("registration/register.html", {
        'form': form,
    }, context_instance=RequestContext(request))


# Once registered, emails link through to this, which sends them on to the defaut django password reset thing.
def register_email_confirm(request, uidb36=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    # Mostly copied from django auth views
    assert uidb36 is not None and token is not None # checked by URLconf
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        # valid link. confirm the email.
        handsomely_user = HandsomelyUser.objects.get(django_user=user)
        handsomely_user.confirmed = True
        handsomely_user.save()

    # Go to the set password page to let it handle the rest (even if link is invalid)
    return password_reset_confirm(request, uidb36, token, template_name="registration/register_password.html", post_reset_redirect="/status")


# Function that is used to extend the user table to have some handsomely required fields. django_user is a User Object
def create_handsomely_user(django_user, gender='U', email_confirmed=False):
    handsomely_user = HandsomelyUser(
        django_user = django_user,
        gender = gender,
        confirmed = email_confirmed,
        )
    handsomely_user.save()
    return handsomely_user


# Salon dashboard
def salon_dashboard(request, form=NotificationForm()):
    django_user = request.user
    c = {'user': django_user}
    if django_user.is_authenticated():
        try:
            salon = Salon.objects.get(django_user = django_user)
            c['salon'] = salon
        except (ValueError, Salon.DoesNotExist):
            # messages.error(request, 'Please log in as a salon to be able to send requests')
            return redirect('/')

        requests_for_salon = Request.objects.filter(salon=salon, status="WAIT")
        valid_requests = requests_for_salon #init
        #Removing any requests from unconfirmed users 
        for haircut_request in requests_for_salon:
            handsomely_requesting_user = HandsomelyUser.objects.get(django_user = haircut_request.django_user)
            if handsomely_requesting_user.confirmed == False:
                #May be very bad practice to remove from the list it's iterating over.
                valid_requests = valid_requests.exclude(django_user = haircut_request.django_user)

        c['requests_for_salon'] = valid_requests

        num_male_requests = len(valid_requests.filter(haircut_type= 'M'))
        num_female_requests = len(valid_requests.filter(haircut_type= 'F'))

        c['num_male_requests'] = num_male_requests
        c['num_female_requests'] = num_female_requests

        notifications = Notification.objects.filter(salon = salon).order_by('-issue_date_time')
        c['notifications'] = notifications

        c['form'] = form
        return render_to_response('notifications.html', c, context_instance=RequestContext(request))
    return redirect('/')


#SEnd out offers to emails
def send_notification(request):
    django_user = request.user
    if django_user.is_authenticated():
        salon = Salon.objects.get(django_user = django_user)
        if request.method == 'POST':
            form = NotificationForm(request.POST)
            print request.POST

            if form.is_valid():
                cd = form.clean()
                day = cd['day']
                if day == 'TODAY':
                    date = datetime.datetime.now()
                elif day == 'TOMORROW':
                    date = datetime.datetime.now() + datetime.timedelta(days=1)
                elif day == 'TDA':
                    date = datetime.datetime.now() + datetime.timedelta(days=2)

                time = str(cd['time'])
                hour, minute, seconds = time.split(':')

                datetime_of_appointment = date.replace(hour = int(hour), minute=int(minute), second = 0)


                haircut_type = cd['haircut_type']
                haircut_requests = Request.objects.filter(salon_id = salon, status = 'WAIT', haircut_type = haircut_type)
                print haircut_requests
                offered_to = haircut_requests
                #Removing any notifications to unconfirmed users 
                for haircut_request in haircut_requests:
                    handsomely_requesting_user = HandsomelyUser.objects.get(django_user = haircut_request.django_user)
                    if handsomely_requesting_user.confirmed == False:
                        offered_to = offered_to.exclude(django_user = haircut_request.django_user)
                print "O/T: ", offered_to, "H/R:", haircut_requests

                new_notification = Notification(
                    salon = salon,
                    status = 'OPEN',
                    appointment_datetime = datetime_of_appointment,
                    appointment_price = cd['discounted_price'],
                    original_price = cd['original_price'],
                    haircut_type = cd['haircut_type'],
                    additional_info = cd['notes'],
                )
                new_notification.save()

                for haircut_request in offered_to:
                    new_notification.offered_to.add(haircut_request.id) #keep account of who it gets sent to

                    # load content
                    contextMap = Context({ "users_email" : haircut_request.django_user.email, 
                                    "salon_name" : salon.salon_name, 
                                    "notification" : new_notification, 
                                    "user_id" : haircut_request.django_user.id,
                                    "offered_to_number" : len(offered_to)
                                 }) 
                    text_content = get_template('emails/notify.txt').render(contextMap)
                    html_content = get_template('appointments/appointment_offer_email.html').render(contextMap)
                    from_email = 'team@handsome.ly'

                    msg = EmailMultiAlternatives('Appointment available at ' + salon.salon_name + ' | Handsome.ly',
                        text_content,
                        from_email,
                        [haircut_request.django_user.email],
                        bcc=[from_email]
                        )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                return redirect('/dashboard/')

        return salon_dashboard(request, form)
    else:
        return redirect('/')

# TO BE DONE
def cancel_notification(request):
    django_user = request.user
    if django_user.is_authenticated():
        salon = Salon.objects.get(django_user = django_user)
        if ('notID' in request.POST and request.POST['notID']):
            # print "good to go"
            notification_id = request.POST['notID']
            notification = Notification.objects.get(id=notification_id)
            if notification.salon.django_user == django_user: 
                print "going"
                notification.status = 'CANC'
                notification.save() 
                return HttpResponse(request) 

        return redirect('/dashboard/')
    else:
        return redirect('/')


# What does this function do exactly? 
def success(request):
    if request.method == 'POST':
        submitting_salon = request.user
        hu = HandsomelyUser.objects.get(django_user = submitting_salon)
        salon_desired = Salon.objects.get(django_user = submitting_salon)
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
            salon_id = salon_desired.id,
            status = 'OPEN',
            appointment_datetime = datetime_of_appointment,
            appointment_price = request.POST['discounted_price'],
            original_price = request.POST['original_price'],
            haircut_type = request.POST['gender'],
            additional_info = request.POST['notes']
            )
        new_notification.save() 
        #Now send out emails
        requests_to_send = Request.objects.filter(salon_id = salon_desired).filter(status = 'WAIT').filter(haircut_type = request.POST['gender'])
	from_email = 'team@handsome.ly'
        for requester in requests_to_send:
            #person_to_send_to = HandsomelyUser.objects.get(django_user = requester.django_user)
          #  message ='Hello there my friend. ' + str(submitting_salon) + ' has a free appointment at ' + str(datetime_of_appointment) + '. Usual price is ' + str(request.POST['original_price']) + '. Price through handsome.ly is ' + str(request.POST['discounted_price']) + '. The following additional information is given: ' + str(request.POST['notes']) + '. Do you fancy it? Hurry, because it is first-come; first-served!'
           # send_mail('Handsomely - Appointment Available', message, 'team@handsome.ly', [person_to_send_to.django_user.email], fail_silently=False)
        
		# load content
			contextMap = Context({ "users_email" : requester.django_user.email, 
						   "salon_name" : salon_desired.salon_name, 
						   "additional_info_from_salon" : new_notification.additional_info, 
						   "notification_id" : new_notification.id,
						   "appointment_date_time" : new_notification.appointment_datetime,
						   "appointment_price" : new_notification.appointment_price,
						   "original_price" : new_notification.original_price,
						   "haircut_type" : new_notification.get_haircut_type_display,
						   "user_id" : requester.django_user.id
						 }) 
			text_content = get_template('emails/notify.txt').render(contextMap)
			html_content = get_template('emails/notify.html').render(contextMap)
			# send email
			msg = EmailMultiAlternatives('Handsome.ly - Appointment Available', text_content, from_email, [requester.django_user.email], bcc=[from_email])
			msg.attach_alternative(html_content, "text/html")
			msg.send()
	return render_to_response('success.html', {}, context_instance=RequestContext(request))

#note
def respond_to_notification(request):
    djangoUser = request.user
    answer = request.GET['ans']
    notifID = request.GET['notifID']
    userID = request.GET['userID']
    if djangoUser.is_anonymous():
        # Change this so user logs in then responds!!! Jordan 26 Feb
        return render_to_response('registration/login_to_respond.html', {'answer':  answer, 'notifID' : notifID, 'userID' : userID}, context_instance=RequestContext(request))
    else: 
        notif = Notification.objects.get(id=notifID)
	django_user = User.objects.get(id=userID)
        handsomelyUserFromNotification = HandsomelyUser.objects.get(django_user=django_user)
        if (django_user.id == djangoUser.id):
            notif = Notification.objects.get(id=notifID)
            salonID = notif.salon
            salonEmail = Salon.objects.get(id = salonID.id).django_user.email
            customerEmail = User.objects.get(id=userID).email
            detailsNeeded = False
            if answer == "NO":
            #    notif.status = 'POS' 
            #    notif.save()
                return render_to_response('thank_you_response.html', { 'answer' : answer }, context_instance=RequestContext(request))
            if answer == "CANCEL":
            #    notif.status = 'CAN'
            #    notif.save()
                return render_to_response('thank_you_response.html', { 'answer' : answer }, context_instance=RequestContext(request))
            if answer == "YES":
                if notif.status == "FILL" or notif.status == "CANC":
                    return render_to_response('sorry.html', {}, context_instance=RequestContext(request))
                else: 
                    #if ( (len(customerPhone) == 0) or (len(customerName) == 0) or ("a" in customerName) ):
                    #    return render_to_response('details_needed.html', { 'number' : customerPhone, 'name' : customerName, 'answer' : answer, 'notifID' : notifID, 'message' : message }, context_instance=RequestContext(request))
                    #else:
                    #notificationsList = Notification.objects.filter(salonID=salonID).filter(status="PEN")
                    #for notification in notificationsList:
                    #    notification.status = "FILL"
                    #    notification.save()
                    notif.status = "FILL"
                    req = Request.objects.filter(django_user=django_user).filter(salon=salonID).filter(haircut_type=notif.haircut_type).filter(status='WAIT')[0]
                    notif.filled_by = req
                    notif.save()
                    req.status = "FULF"
                    req.save()
                    message = "Hi! \n\nA customer has responded to your notification and accepted the appointment."
                    message += "\n\nCustomer: " + customerEmail
                    message += "\n\nAppointment time: " + str(notif.appointment_datetime.strftime("%A, %d. %B %Y %I:%M%p")) 
		    message += "\n\nAppointment price: GBP" + str(notif.appointment_price) 
		    message += "\n\nAppointment type: " + notif.get_haircut_type_display() 
                    message += "\n\nthanks,\nthe Handsome.ly team"
                    send_mail('Handsomely - Customer Responded', message, 'team@handsome.ly', [salonEmail, 'team@handsome.ly'], fail_silently=False)

                    messages.success(request, "Thank you. You've accepted the haircut. Go to " + salonID.salon_name + " at your appointment time.")
                    return redirect("/status/")
                    # return render_to_response('thank_you_response.html', { 'answer' : answer, 'name' : customerEmail }, context_instance=RequestContext(request))
        else:
            return render_to_response('incorrect_user.html', {'answer' : answer, 'notifID' : notifID, 'djuid' : djangoUser.id, 'handsomelyUserFromNotification' :  handsomelyUserFromNotification}, context_instance=RequestContext(request))

def logged_in_response(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		notifID = request.POST['notifID']
		answer = request.POST['answer']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return render_to_response('registration/logged_in_response.html', {'notifID': notifID, 'answer' : answer, 'userID' : user}, context_instance=RequestContext(request))
			else:
				pass# Return a 'disabled account' error message, added a PASS to not break the program ~jab
		else:
			errorMessage = "Wrong username or password"
		return render_to_response('login.html', {'emailAdd': email, 'message' : errorMessage}, context_instance=RequestContext(request))
	else:
		return render_to_response('login.html', {}, context_instance=RequestContext(request))