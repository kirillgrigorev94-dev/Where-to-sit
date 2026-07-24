from django.contrib import admin
from django.utils import timezone
from .models import Room, Booking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    list_filter = ('capacity',)
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'start', 'end', 'is_active')
    list_filter = ('room', 'user', 'start')
    search_fields = ('room__name', 'user__username')
    date_hierarchy = 'start'

    def is_active(self, obj):
        now = timezone.now()
        return obj.start <= now <= obj.end
    is_active.boolean = True
    is_active.short_description = 'Активно сейчас'