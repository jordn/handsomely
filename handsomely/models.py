from django.db import models
from django.contrib.auth.models import User, UserManager

# Django user does fancy stuff like join date

class HandsomelyUser(User): # Extends User model
	djangoUserID = models.OneToOneField(User) # Inherit from User model
	customerID = models.IntegerField() #FK
	salonID = models.IntegerField() # if 0, then Customer, otherwise Salon

class Customer(models.Model):
	firstName = models.CharField(max_length=50)
	lastName = models.CharField(max_length=50)
	defaultCity = models.CharField(max_length=50)
	mobile = models.CharField(max_length=20)
	NOTIFICATION_CHOICES = ( 
		('EMA', 'e-mail'),
	)
	notification_preferences = models.CharField(max_length=3, choices=NOTIFICATION_CHOICES)

class Salon(models.Model):
	salonName = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	city = models.CharField(max_length=50)
	phone = models.CharField(max_length=50)
	webAddress = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	openingHoursID = models.IntegerField()
	review = models.CharField(max_length=50)

class SalonOpeningHours(models.Model):
	salonID = models.IntegerField() #FK
	DAYS = ( 
		('MON', 'Monday'),
		('TUE', 'Tuesday'),
		('WED', 'Wednesday'),
		('THU', 'Thursday'),
		('FRI', 'Friday'),
		('SAT', 'Saturday'),
		('SUN', 'Sunday'),
	)
	dayOfTheWeek = models.CharField(max_length=3, choices=DAYS)
	openingTime = models.CharField(max_length=5)
	closingTime = models.CharField(max_length=5)

class SalonDetails(models.Model):
	salonID = models.IntegerField() #FK
	contactName = models.CharField(max_length=50)
	contactNumber = models.CharField(max_length=50)
	contactEmail = models.EmailField()

class PriceMenu(models.Model):
	salonID = models.IntegerField() #FK
	serviceName = models.CharField(max_length=50)
	servicePrice = models.CharField(max_length=50)

class Request(models.Model):
	customerID = models.IntegerField() #FK
	salonID = models.IntegerField() #FK
	startDate = DateField(_("Date"), auto_now_add=True)
	STATUSES = ( 
		('REQ', 'Requesting'), # Pending a response
		('FUL', 'Fulfilled'), # i.e. they get a push notification from the salon
		('CAN', 'Cancelled'),
		('HOL', 'OnHold'),
	)
	status = models.CharField(max_length=3, choices=STATUSES)
	noSoonerThan = DateTimeField(_("Date"), auto_now_add=True)

class Notifications(models.Model):
	customerID = models.IntegerField() #FK
	salonID = models.IntegerField() #FK
	timeSent = DateField(_("Date"), auto_now_add=True)
	timeReplied = DateField(_("Date"), auto_now_add=True)
	STATUSES = ( 
		('PEN', 'Pending'),
		('ACC', 'Accepted'),
		('CAN', 'Cancelled'),
		('POS', 'Postponed'),
	)
	status = models.CharField(max_length=3, choices=STATUSES)
