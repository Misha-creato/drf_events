import time

from django.core.management.base import BaseCommand

from tickets.workers import (
    user_event_notification,
    update_ticket_status,
    check_bill_status,
    check_payment_status,
)

from utils.logger import get_logger


logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Запускать воркеры билетов каждую минуту'

    def handle(self, *args, **kwargs):

        while True:
            # user_event_notification(notification_status='day_in_day')
            # user_event_notification(notification_status='3_days')
            # user_event_notification(notification_status='expired')
            # update_ticket_status()
            # check_bill_status()
            check_payment_status()
            time.sleep(60)
