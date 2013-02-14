from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from haircuts.views import index

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

# urlpatterns += patterns('',
#     #  user accounts
#     (r'^index/$',  index),
# )

# urlpatterns += patterns('django.contrib.auth.views',
#     #  user accounts
#     url(r'^login/$',  'login'),
#     url(r'^logout/$', 'logout'),

#     url(r'^passwordreset/$', 'password_reset', {'template_name': 'registration/password_reset_form.html'}),
#     url(r'^passwordresetdone/$', 'password_reset_done', {'template_name': 'registration/password_reset_done.html'}),
#     url(r'^passwordresetconfirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#         'password_reset_confirm',
#         name='password_reset_confirm'),
#     (r'^passwordresetcomplete/$', 'password_reset_complete', {'template_name': 'registration/password_reset_complete.html'}),

# )

urlpatterns += patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
)