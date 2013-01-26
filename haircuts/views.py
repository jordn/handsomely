# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def index (request):
    return render_to_response('index.html', {'path': request.path})

def hackathon_index (request):
    return render_to_response('hackathon_index.html', {'path': request.path})

def coming_soon (request):
    return render_to_response('coming_soon.html', {'path': request.path})

def register(request):
	if request.method == 'GET':
		sex = request.GET['sex']
	if request.method == 'GET':
		sex = request.GET['sex']
		womens_salons = []

		salons = Salon.objects.all()
		for salon in salons:
			if salon.womens_standard_price:
				womens_salons.append(salon)
		return render_to_response('salon_list.html', {'sex' : sex, 'womens_salons' : womens_salons}, context_instance=RequestContext(request))
