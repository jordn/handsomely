from django.db import models
from django import forms
from django_localflavor_gb.forms import GBPostcodeField
from django.contrib.auth.models import User
import datetime

class HandsomelyUser(User): 
	django_user_id = models.OneToOneField(User) 
	gender_choices = ( ('M', 'Male'), ('F','Female'), ('U', 'Unspecified') )
	gender = models.CharField(max_length=1, choices=gender_choices)
	is_salon = models.BooleanField(default=False)
	confirmed = models.BooleanField(default=False)
	
class Salon(models.Model):
	handsomely_user_id = models.ForeignKey('HandsomelyUser')
	salon_name = models.CharField(max_length=50)
	address_line_1 = models.CharField(max_length=100, blank = True)
	address_line_2 = models.CharField(max_length=100, blank = True)
	city = models.CharField(max_length=30, blank = True)
	postcode = GBPostcodeField(blank = True)
	phone_number = models.CharField(max_length=20, blank = True)
	website = models.URLField(blank = True)
	mens_standard_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True)
	mens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True)
	womens_standard_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True)
	womens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True) 
	
class Request(models.Model):
	handsomely_user_id = models.ForeignKey('HandsomelyUser')
	salon_id = models.ForeignKey('Salon')
	haircut_choices = ( ('M', 'Male'), ('F', 'Female'), ('U', 'Unspecified') )
	haircut_type = models.CharField(max_length=1, choices=haircut_choices) 
	status_choices =  ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = models.CharField(max_length=4, choices=status_choices) 
	start_date_time = models.DateTimeField(default=datetime.datetime.now) 
	
class Notification(models.Model):
	issue_date_time = models.DateTimeField(default=datetime.datetime.now)
	salon_id = models.ForeignKey('Salon')
	request_ids = models.ManyToManyField(Request)
	filled_by = models.ForeignKey('HandsomelyUser')
	status_choices = ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = models.CharField(max_length=4, choices=status_choices) 
	appointment_date_time = models.DateTimeField()
	appointment_price = models.DecimalField(max_digits=4, decimal_places=2)
	original_price = models.DecimalField(max_digits=4, decimal_places=2, blank = True)
	haircut_choices = ( ('M', 'Male'), ('F', 'Female'), ('U', 'Unspecified') )
	haircut_type = models.CharField(max_length=1, choices=haircut_choices) 
	additional_info = models.TextField(blank = True)
		
