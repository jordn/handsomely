from django.contrib import admin
from haircuts.models import HandsomelyUser, Salon, Request, Notification

admin.site.register(HandsomelyUser)
admin.site.register(Salon)
admin.site.register(Request)
admin.site.register(Notification)