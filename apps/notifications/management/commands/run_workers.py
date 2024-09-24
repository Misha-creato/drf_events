import time
from django.core.management.base import BaseCommand

from notifications.workers import check_notification
from utils.logger import get_logger


logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Запускать воркеры каждую минуту'

    def handle(self, *args, **kwargs):

        while True:
            check_notification(notification_status='day_in_day')
            check_notification(notification_status='3_days')
            check_notification(notification_status='expired')
            time.sleep(60)
