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
    url(r'^get_salons_price_menu/$', get_salons_price_menu),
    url(r'^get_salons_opening_hours/$', get_salons_opening_hours),
    url(r'^register/$', register),
    url(r'^login/$', login_page),
    url(r'^user_login/$', user_login),
    url(r'^logout/$', user_logout),
    url(r'^profile/$', profile),
    url(r'^update_profile/$', update_profile),
    url(r'^salons/$', for_salons), 
    url(r'^get_notified/$', get_notified),
    url(r'^privacypolicy/$', privacy_policy), 
    url(r'^confirm/$', confirm), 
    url(r'^create_user/$', create_user), 
    url(r'^create_notification_request/$', create_notification_request), 
    url(r'^notify/$', big_red_button), # big red button page
    url(r'^notify_customers/$', notify_customers), # page that process the notification
)
	

# # #this is to try and get local static files to be served. might not be needed.
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
