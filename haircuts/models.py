from django.db import models
from django_localflavor_gb.forms import GBPostcodeField

class HandsomelyUser(User): 
	django_user_id = models.OneToOneField(User) 
	gender_choices = ( ('M', 'Male'), ('F','Female') )
	gender = models.CharField(max_length=1, choices=gender_choices)
	is_salon = models.BooleanField(default=False)
	confirmed = Models.BooleanField(default=False)
	
class Salon(models.Model):
	handsomely_user_id = models.ForeignKey('HandsomelyUser')
	salon_name = models.CharField(max_length=50)
	address_line_1 = models.CharField(max_length=100)
	address_line_2 = models.CharField(max_length=100)
	city = models.CharField(max_length=30)
	postcode = GBPostcodeField()
	phone_number = models.CharField(max_length=20)
	website = models.URLField()
	mens_standard_price = models.DecimalField(max_digits=4, decimal_places=2)
	mens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2)
	womens_standard_price = models.DecimalField(max_digits=4, decimal_places=2)
	womens_handsomely_price = models.DecimalField(max_digits=4, decimal_places=2) 
	
class Request(models.Model):
	handsomely_user_id = models.ForeignKey('HandsomelyUser')
	salon_id = models.ForeignKey('Salon')
	haircut_choices = ( ('M', 'Male'), ('F', 'Female') )
	haircut_type = models.CharField(max_length=1, choices=haircut_choices) 
	status_choices =  ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = models.CharField(max_length=4, choices=status_choices) 
	start_date_time = models.DateTimeField(default=datetime.now) 
	
class Notification(models.Model):
	issue_date_time = models.DateTimeField(default=datetime.now)
	salon_id = models.ForeignKey('Salon')
	request_ids = models.ManyToManyField(Request)
	filled_by = models.ForeignKey('HandsomelyUser')
	status_choices = ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = models.CharField(max_length=4, choices=haircut_choices) 
	appointment_date_time = models.DateTimeField()
	appointment_price = models.DecimalField(max_digits=4, decimal_places=2)
	original_price = models.DecimalField(max_digits=4, decimal_places=2)
	haircut_choices = (( ('M', 'Male'), ('F', 'Female') )
	haircut_type = (max_length=1, choices=haircut_choices) 
	additional_info = models.TextField()
		
