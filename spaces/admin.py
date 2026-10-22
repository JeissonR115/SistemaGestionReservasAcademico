from django.contrib import admin

from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'space_type', 'capacity', 'is_active')
    list_filter = ('space_type', 'is_active')
    search_fields = ('name',)
