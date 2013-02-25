from django.db import models
from django import forms
from django.contrib.auth.models import User
import datetime

class HandsomelyUser(models.Model): 
	django_user = models.OneToOneField(User, related_name='profile') 
	gender_choices = ( ('M', 'Male'), ('F','Female'), ('U', 'Unspecified') )
	gender = models.CharField(max_length=1, choices=gender_choices)
	# is_salon = models.BooleanField(default=False) #Should probably remove this and just check salons that they have this Django_user instead. Much less error prone.
	confirmed = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.django_user.email
	
class Salon(models.Model):
	django_user = models.ForeignKey(User)
	salon_name = models.CharField(max_length=50)
	address_line_1 = models.CharField(max_length=100, blank = True, null = True)
	address_line_2 = models.CharField(max_length=100, blank = True, null = True)
	city = models.CharField(max_length=30, blank = True, null = True)
	postcode = models.CharField(max_length=8, blank = True, null = True)
	phone_number = models.CharField(max_length=20, blank = True, null = True)
	website = models.URLField(blank = True, null = True)
	mens_standard_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True, null = True)
	mens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True, null = True)
	womens_standard_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True, null = True)
	womens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True, null = True) 
	
	def __unicode__(self):
		return self.salon_name
	
class Request(models.Model):
	django_user = models.ForeignKey(User)
	salon = models.ForeignKey('Salon')
	haircut_choices = ( ('M', 'Male'), ('F', 'Female'), ('U', 'Unspecified') )
	haircut_type = models.CharField(max_length=1, choices=haircut_choices) 
	status_choices =  ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = models.CharField(max_length=4, choices=status_choices) 
	start_date_time = models.DateTimeField(default=datetime.datetime.now) 
	
	def __unicode__(self):
		return str(self.id) + ' ' + str(self.django_user) + ' for ' + self.haircut_type + ' @ ' + str(self.salon)

class Notification(models.Model):
	issue_date_time = models.DateTimeField(default=datetime.datetime.now)
	salon = models.ForeignKey('Salon')
	offered_to = models.ManyToManyField(Request, related_name='notification+')
	status_choices = ( ('FILL', 'Filled'), ('OPEN', 'Open'), ('CANC', 'Cancelled') )
	status = models.CharField(max_length=4, choices=status_choices) 
	filled_by = models.ForeignKey('Request', blank=True, null=True) #which request took the booking
	appointment_datetime = models.DateTimeField()
	appointment_price = models.DecimalField(max_digits=4, decimal_places=2)
	original_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True, null = True)
	haircut_choices = ( ('M', 'Male'), ('F', 'Female'), ('U', 'Unspecified') )
	haircut_type = models.CharField(max_length=1, choices=haircut_choices) 
	additional_info = models.TextField(blank = True, null = True)
		
