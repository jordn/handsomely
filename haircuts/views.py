# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import HandsomelyUser, Salon, Request, Notification

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
