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
    url(r'^$', index),
    #url(r'^about/$', about),
    #url(r'^salons/$', salons),
    #url(r'^get_salons/$', get_salons),
    #url(r'^get_salons_price_menu/$', get_salons_price_menu),
    #url(r'^get_salons_opening_hours/$', get_salons_opening_hours),
    #url(r'^get_salon_latlng/$', get_salon_latlng),
    #url(r'^register/$', register),
    #url(r'^login/$', login_page),
    #url(r'^user_login/$', user_login),
    #url(r'^logout/$', user_logout),
    #url(r'^ajax_user_login/$', ajax_user_login),
    #url(r'^profile/$', profile),
    #url(r'^update_profile/$', update_profile),
    #url(r'^get_notified/$', get_notified),
    #url(r'^response/$', response),
    #url(r'^privacy/$', privacy_policy), 
    #url(r'^confirm/$', confirm), 
    #url(r'^create_user/$', create_user), 
    #url(r'^create_notification_request/$', create_notification_request), 
    #url(r'^notify/$', big_red_button), # big red button page
    #url(r'^notify_customers/$', notify_customers), # page that process the notification
    #url(r'^test/$', test), #sandbox to try out tings 
    #url(r'^cancel_request/$', cancel_request_ajax),
    #url(r'^salon_signup/$', salon_signup),
    #url(r'^response_yes_after_providing_details/$', response_yes_after_providing_details),
    #url(r'^logged_in_response/$', logged_in_response),
    url(r'^register/$', register),
    url(r'^hackathon_index/$', hackathon_index),
    )
	

# # #this is to try and get local static files to be served. might not be needed.
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
