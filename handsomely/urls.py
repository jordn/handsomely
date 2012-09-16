from django.conf.urls import patterns, include, url
from handsomely.views import index, about, register, for_salons, user_login, user_logout, profile

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
    url(r'^login/$', user_login),
    url(r'^logout/$', user_logout),
    url(r'^register/$', register),
    url(r'^profile/$', profile),
    url(r'^for_salons/$', for_salons), 
)
	
