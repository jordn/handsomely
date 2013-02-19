from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django import forms
from haircuts.forms import RegisterForm, LoginForm, RequestForm, NotificationForm, NotifyForm
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

from models import *
import datetime
import time


def coming_soon (request):
    return render_to_response('coming_soon.html', context_instance=RequestContext(request))

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
                 + str(salon) + '</strong> is still waiting. You will be emailed at <strong>' + django_user.email +'</strong> when an appointment becomes available.'))
                return redirect('/status/')

            new_request = Request(
                django_user = django_user,
                salon = salon,
                haircut_type = haircut_type,
                status = 'WAIT',
                )
            new_request.save()
            messages.info(request, ('Your request for a <strong>' + new_request.haircut_type +'</strong> haircut at <strong>'
             + str(new_request.salon) + '</strong> has been added. You will be emailed at <strong>' + django_user.email +'</strong> any available appointments.'))

        return redirect('/status')
    else:
        return redirect('/')


def cancel_haircut_request(request):
    django_user = request.user
    if django_user.is_authenticated():

        if ('reqID' in request.POST and request.POST['reqID']):
            request_id = request.POST['reqID']
            request = Request.objects.get(id=request_id)
            print "POST"
            if request.django_user == django_user: 
                request.status = 'CANC'
                request.save() 
                return HttpResponse(request.id) 

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

            messages.success(request, 'Came from register.')

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
def salon_dashboard(request):
    django_user = request.user
    c = {'user': django_user}
    if django_user.is_authenticated():
        try:
            salon = Salon.objects.get(django_user = django_user)
            c['salon'] = salon
        except (ValueError, Salon.DoesNotExist):
            messages.error(request, 'Please log in as a salon to be able to send requests')
            return redirect('/')

        requests_for_salon = Request.objects.filter(salon=salon, status="WAIT")
        c['requests_for_salon'] = requests_for_salon

        num_male_requests = len(requests_for_salon.filter(haircut_type= 'M'))
        num_female_requests = len(requests_for_salon.filter(haircut_type= 'F'))

        c['num_male_requests'] = num_male_requests
        c['num_female_requests'] = num_female_requests
    
        form = NotificationForm()
        c['form'] = form
        return render_to_response('notifications.html', c, context_instance=RequestContext(request))
    return redirect('/')

def send_notification(request):
    django_user = request.user
    if django_user.is_authenticated():
        salon = Salon.objects.get(django_user = django_user)
        if request.method == 'POST':
            form = NotificationForm(request.POST)
            if form.is_valid():
                cd = form.clean()
                # print cd {'original_price': None, 'discounted_price': 21.0, 'notes': u'', 'time': datetime.time(12, 12), 'day': u'TODAY', 'haircut_type': u'M'}

                new_notification = Notification(
                salon = salon,
                status = 'OPEN',
                appointment_datetime = datetime.datetime.now() + datetime.timedelta(days=1),
                appointment_price = cd['discounted_price'],
                original_price = cd['original_price'],
                haircut_type = cd['haircut_type'],
                additional_info = cd['notes']
                )
                new_notification.save() 
                print "callabunga"
                print form
                return redirect('/notifications/')

            print "poop"
            print form


        return redirect('/notifications/')
    else:
        return redirect('/')




def notify(request):
    form = NotifyForm()
    salon_logged_in = request.user
    hu = HandsomelyUser.objects.get(django_user = salon_logged_in)
    salon_desired = Salon.objects.get(django_user = salon_logged_in)	
    requesters = Request.objects.filter(salon = salon_desired)
    male_requesters = requesters.filter(haircut_type = 'M')
    female_requesters = requesters.filter(haircut_type = 'F')
    number_male = len(male_requesters)
    number_female = len(female_requesters)
    return render_to_response('notify_customers.html', {'form': form, 'number_male': number_male, 'number_female': number_female, 'salon_desired': salon_desired}, context_instance=RequestContext(request))


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
            person_to_send_to = HandsomelyUser.objects.get(django_user = requester.django_user)
            message ='Hello there my friend. ' + str(submitting_salon) + ' has a free appointment at ' + str(datetime_of_appointment) + '. Usual price is ' + str(request.POST['original_price']) + '. Price through handsome.ly is ' + str(request.POST['discounted_price']) + '. The following additional information is given: ' + str(request.POST['notes']) + '. Do you fancy it? Hurry, because it is first-come; first-served!'
            send_mail('Handsomely - Appointment Available', message, 'team@handsome.ly', [person_to_send_to.django_user.email], fail_silently=False)
        return render_to_response('success.html', {}, context_instance=RequestContext(request))

		
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

