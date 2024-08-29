from django.contrib import admin

from events.models import (
    Area,
    Category,
    Event,
    Landing,
    SpecialSeat,
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


class SpecialSeatInline(admin.StackedInline):
    model = SpecialSeat
    extra = 1


@admin.register(Landing)
class LandingAdmin(admin.ModelAdmin):
    inlines = [
        SpecialSeatInline,
    ]


class LandingInline(admin.StackedInline):
    model = Landing
    extra = 1
    show_change_link = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [
        LandingInline,
    ]
    list_display = [
        'name',
        'canceled',
    ]


