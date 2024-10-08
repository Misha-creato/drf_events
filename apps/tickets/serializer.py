from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            'uuid',
            'event_name',
            'section',
            'row',
            'seat',
            'status',
            'bought_at',
        ]


class TicketQRSerializer(serializers.Serializer):
    uuid = serializers.CharField()


class SeatDataSerializer(serializers.Serializer):
    section = serializers.CharField(
        allow_null=True,
    )
    row = serializers.CharField(
        allow_null=True
    )
    seat = serializers.CharField()


class TicketBuySerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    seat_data = SeatDataSerializer()
    price = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
        min_value=1,
    )
