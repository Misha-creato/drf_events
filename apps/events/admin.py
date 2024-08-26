from django.contrib import admin

from events.models import (
    Area,
    Category,
    Event,
    Landing,
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'available',
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


class LandingInline(admin.StackedInline):
    model = Landing
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [
        LandingInline,
    ]
    list_display = [
        'name',
        'canceled',
    ]


