from django.db.models.signals import (
    post_delete,
)
from django.dispatch import receiver
from django.utils import timezone

from events.models import Event

from tickets.models import Ticket

from utils import constants


@receiver(signal=post_delete, sender=Event)
def refund_tickets(sender, instance, **kwargs):
    tickets = instance.tickets.filter(
        status=constants.active,
    )
    for ticket in tickets:
        ticket.status = constants.need_refund
        ticket.status_updated = timezone.now()
        ticket.check_count = 0

    Ticket.objects.bulk_update(tickets, [
        'status', 'status_updated', 'check_count',
    ])
