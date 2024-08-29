from rest_framework import serializers

from events.models import (
    Event,
    SpecialSeat,
    Landing,
)


class SpecialSeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecialSeat
        fields = [
            'seat',
            'price',
            'seat_type'
        ]


class LandingSerializer(serializers.ModelSerializer):
    special_seats = SpecialSeatSerializer(
        many=True,
    )

    class Meta:
        model = Landing
        fields = [
            'section',
            'row',
            'quantity',
            'price',
            'special_seats',
        ]


class EventSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    place = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_city(self, obj):
        return obj.area.city

    def get_place(self, obj):
        return obj.area.name

    def get_address(self, obj):
        return obj.area.address

    def get_category(selfs, obj):
        return obj.category.name

    class Meta:
        model = Event
        fields = [
            'name',
            'slug',
            'city',
            'place',
            'address',
            'start_at',
            'end_at',
            'age_limit',
            'category',
            'min_price',
            'quantity',
            'available_tickets',
            'description',
        ]


class EventLandingSerializer(EventSerializer):
    landings = LandingSerializer(
        many=True,
    )

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['landings']

