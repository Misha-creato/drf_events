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
