from django.contrib import admin

from .models import Room, Message

class RoomAdmin(admin.ModelAdmin):
    search_fields = ['room_name', 'host',]
    list_filter = [
        'room_name',
        'host',
    ]
    list_display = ['pk', 'room_name', 'host', 'status']

admin.site.register(Room, RoomAdmin)
admin.site.register(Message)
