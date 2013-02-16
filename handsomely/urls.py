from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete

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
    
    url(r'^salons/$', 'salons'),

    url(r'^status/$', 'customer_status'),
    url(r'^requests/$', 'requests'),

    url(r'^notify/$', 'notify'), 
    url(r'^success/$', 'success'),
)

#registration etc.
urlpatterns += patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
    
    url(r'^register/$', 'haircuts.views.register'),
    url(r'^register/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'haircuts.views.register_email_confirm',
        name='password_reset_confirm'),

    url(r'^password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),

    url(r'^forgot/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^forgot/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         'django.contrib.auth.views.password_reset_confirm',
         name='password_reset_confirm'),
    
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
)