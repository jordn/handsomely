from django.contrib import admin
from handsomely.models import *

admin.site.register(Salon)
admin.site.register(SalonDetails)
admin.site.register(PriceMenu)
admin.site.register(SalonOpeningHours)
admin.site.register(HandsomelyUser)
admin.site.register(Customer)
# the following models don't display the datetime fields in the admin
# this is a known problem in django (auto_now feature :| )
admin.site.register(Request)
admin.site.register(Notification, NotificationAdmin)

