from django.conf.urls import patterns, include, url
from haircuts.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    )

urlpatterns += patterns('haircuts.views',
    url(r'^$', 'coming_soon'),
    url(r'index/$', 'index'),
    url(r'salon_list/$', 'salon_list'),
    url(r'request_haircut/$', 'request_haircut'),

)
	

# # #this is to try and get local static files to be served. might not be needed.
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
