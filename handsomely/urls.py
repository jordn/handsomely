from django.conf.urls import patterns, include, url
from handsomely.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^about/$', about),
    url(r'^get_salons/$', get_salons),
    url(r'^register/$', register),
    url(r'^login/$', user_login),
    url(r'^logout/$', user_logout),
    url(r'^profile/$', profile),
    url(r'^for_salons/$', for_salons), 
    url(r'^notify/$', notify_users), 
)
	

# # #this is to try and get local static files to be served. might not be needed.
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
