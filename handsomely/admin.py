from django.contrib import admin
from handsomely.models import *

admin.site.register(Salon)
admin.site.register(SalonDetails)
admin.site.register(PriceMenu)
admin.site.register(SalonOpeningHours)
admin.site.register(HandsomelyUser)
admin.site.register(Customer)
admin.site.register(Request)
class NotificationAdmin(admin.ModelAdmin):
	date_hierarchy = 'timeSent'
admin.site.register(Notification, NotificationAdmin)

