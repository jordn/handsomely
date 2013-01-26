from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from haircuts.forms import RegisterForm, LoginForm
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from models import *
import datetime

def index (request):
    return render_to_response('index.html', {'path': request.path})

def coming_soon (request):
    return render_to_response('coming_soon.html', {'path': request.path})

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
	
def request_haircut(request):
	if request.method == 'POST':
		gender = request.POST['gender']
		salon_to_be_requested = request.POST['salon']
		#NOTE THAT THIS LINE BELOW NEEDS FIXING AS ONLY TAKING FIRST WORD OF SALON NAME
		salon_for_request = Salon.objects.get(salon_name__contains = salon_to_be_requested)
		requester = request.user #THIS DETERMINES THE ID OF WHO IS ASKING FOR A REQUEST
		new_request = Request(
			handsomely_user_id = requester.id,
			salon_id = salon_for_request,
			haircut_type = gender,
			status = 'WAIT',
			)
		new_request.save()
		return render_to_response('index.html', {}, context_instance=RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('requests/')
    else:
        form = RegisterForm(
            initial={'email': ''}
            )
    return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('requests/')
    else:
        form = LoginForm(initial={'email': '', 'password': '', 'remember_me': ''})
    return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))


		
def notify_customers(request):
	userIDFromForm = request.GET['duid']
	additionalInfoFromForm = request.GET['addinfo']
	djangoUser = User.objects.get(id=userIDFromForm)
	handsomely_user = HandsomelyUser.objects.get(django_user_id=djangoUser)
	salon = Salon.objects.get(handsomely_user_id=djangoUser)
	requestsList = Request.objects.filter(salon_id=salon.id).filter(Q(status="REQ") | Q(status="HOL"))
	subject = 'Handsomely Notification'
	from_email = 'team@handsome.ly' 
	reqIds = []
	for req in requestsList:
		reqIds.append(req.id)
	notif = Notification(request_ids=reqIds, salon_id=salon, issue_date_time=datetime.datetime.now, timeReplied=datetime.datetime.max, status='OPEN', appointment_date_time=datetime.datetime.now, appointment_price=10.5, original_price=11, haircut_type="M", additionalInfo="testing")
	notif.save()
	for req in requestsList:
		req.status = "HOL"
		req.save()
		recipientHandsomelyUser = HandsomelyUser.objects.get(id = req.handsomely_user_id)
		recipientDjangoUser = User.objects.get(id = recipientHandsomelyUser.django_user_id.id)
		custID = recipientHandsomelyUser.customerID
		to_email = recipientDjangoUser.email
		# content
		contextMap = Context({ "users_first_name" : recipientDjangoUser.first_name, 
				       "salon_name" : salon.salonName, 
				       "additional_info_from_salon" : additionalInfoFromForm, 
				       "notification_id" : str(notif.id)
				     })
		text = get_template('template/emails/notify.txt')
		html = get_template('templates/emails/notify.html')
		text_content = notification_email_text
		html_content = notification_email_html
		# send email
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		text_content += "\n - Customer email: " + to_email
		html_content += "<br> - Customer email: " + to_email
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

