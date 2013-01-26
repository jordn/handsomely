# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def index (request):
    return render_to_response('index.html', {'path': request.path})
