from django.contrib import admin

from .models import Reservation, ReservationLog


class ReservationLogInline(admin.TabularInline):
    model = ReservationLog
    extra = 0
    can_delete = False
    readonly_fields = ('status', 'actor', 'changed_at')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('space', 'requester', 'start_at', 'end_at', 'status')
    list_filter = ('status', 'space')
    inlines = (ReservationLogInline,)
    readonly_fields = ('created_at',)


@admin.register(ReservationLog)
class ReservationLogAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'status', 'actor', 'changed_at')
    readonly_fields = ('reservation', 'status', 'actor', 'changed_at')
