# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from haircuts.forms import RegisterForm

def index (request):
    return render_to_response('index.html', {'path': request.path})

def coming_soon (request):
    return render_to_response('coming_soon.html', {'path': request.path})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = RegisterForm(
            initial={'email': ''}
            )
    return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))