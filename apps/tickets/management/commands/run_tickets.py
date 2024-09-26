import time

from django.core.management.base import BaseCommand

from tickets.workers import (
    notification,
    update_ticket_status,
)

from utils.logger import get_logger


logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Запускать воркеры каждую минуту'

    def handle(self, *args, **kwargs):

        while True:
            notification(notification_status='day_in_day')
            notification(notification_status='3_days')
            notification(notification_status='expired')
            update_ticket_status()
            time.sleep(60)
