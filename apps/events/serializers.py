from rest_framework import serializers

from events.models import Event


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
