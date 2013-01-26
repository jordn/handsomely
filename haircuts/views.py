from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from haircuts.forms import RegisterForm, LoginForm


from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from models import *

def index (request):
    return render_to_response('index.html', {'path': request.path})

def coming_soon (request):
    return render_to_response('coming_soon.html', {'path': request.path})

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
	salon = Salon.objects.get(user_id=djangoUser)
	requestsList = Request.objects.filter(salonID=salonID).filter(Q(status="REQ") | Q(status="HOL"))
	subject = 'Handsomely Notification'
	from_email = 'team@handsome.ly' 
	for req in requestsList:
		req.status = "HOL"
		req.save()
		recipientHandsomelyUser = HandsomelyUser.objects.get(customerID = req.customerID)
		recipientDjangoUser = User.objects.get(id = recipientHandsomelyUser.djangoUserID.id)
		custID = recipientHandsomelyUser.customerID
		notif = Notification(customerID=custID, salonID=salonID, timeSent=datetime.now(), timeReplied=datetime.max, status='PEN')
		notif.save()
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
