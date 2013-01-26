from django.db import models

class HandsomelyUser(User): # Extends User model
	django_user_id = models.OneToOneField(User) # Inherit from User model
	gender_choices = ( ('M', 'Male'), ('F','Female') )
	gender = models.CharField(max_length=1, choices=gender_choices)
	is_salon = models.BooleanField()
	confirmed = Models.BooleanField(default=False)
	
class Salon(models.Model):
	handsomely_user_id = models.ForeignKey('HandsomelyUser')
	salon_name = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
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
	haircut_type = (max_length=1, choices=haircut_choices) 
	status_choices =  ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = (max_length=4, choices=status_choices) 
	start_date_time = models.DateTimeField()
	
class Notification(models.Model):
	issue_date_time = models.DateTimeField()
	salon_id = models.ForeignKey('Salon')
	request_ids = models.ManyToManyField()
	filled_by = models.ForeignKey('HandsomelyUser')
	status_choices = ( ('FULF', 'Fulfilled'), ('CANC', 'Cancelled'), ('WAIT', 'Waiting') )
	status = (max_length=4, choices=haircut_choices) 
	appointment_date_time = models.DateTimeField()
	appointment_price = models.DecimalField(max_digits=4, decimal_places=2)
	original_price = models.DecimalField(max_digits=4, decimal_places=2)
	haircut_choices = (( ('M', 'Male'), ('F', 'Female') )
	haircut_type = (max_length=1, choices=haircut_choices) 
	additional_info = models.TextField()
		
