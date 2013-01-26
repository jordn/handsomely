from django.contrib import admin
from handsomely.models import *

admin.site.register(Salon)
admin.site.register(SalonDetails)
admin.site.register(PriceMenu)
class SalonOpeningHoursAdmin(admin.ModelAdmin):
	list_display = ('salonID', 'dayOfTheWeek')
	#raw_id_fields = ('salonID',) #doesn't work because salonID isn't actually a foreign key!!!
admin.site.register(SalonOpeningHours, SalonOpeningHoursAdmin)
admin.site.register(HandsomelyUser)
admin.site.register(Customer)
# the following models don't display the datetime fields in the admin
# this is a known problem in django (auto_now feature :| )
admin.site.register(Request)
admin.site.register(Notification)

