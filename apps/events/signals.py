from django.db.models import Min
from django.dispatch import receiver
from django.db.models.signals import post_save

from events.models import Landing


@receiver(signal=post_save, sender=Landing)
def update_min_price(sender, instance, **kwargs):
    event = instance.event
    min_price = event.landings.aggregate(Min('price', default=0))['price__min']
    event.min_price = min_price
    event.save()
