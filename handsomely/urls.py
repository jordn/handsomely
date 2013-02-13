from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset


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
    
    url(r'^register/$', 'register'),
    url(r'^confirm/$', 'confirm'),

    url(r'^status/$', 'customer_status'),
    url(r'^thanks/$', 'thanks'),

    url(r'^create_user/$', 'create_user'), 
    url(r'^notify/$', 'notify'), 
    url(r'^success/$', 'success'),
)

urlpatterns += patterns('',
    #  user accounts
    (r'^login/$',  login),
    (r'^logout/$', logout),
    (r'^passwordreset/$', password_reset, {'template_name': 'registration/password_reset_form.html', 'post_reset_redirect': '/index'}),
)