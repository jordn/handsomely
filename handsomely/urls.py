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
    url(r'^index/$', 'index'),
    url(r'^salon_list/$', 'salon_list'),
    url(r'^request_haircut/$', 'request_haircut'),
    url(r'^register/$', 'register'),
    url(r'^login/$', 'login'),
    url(r'^notify/$', 'notify_customers'),
)
