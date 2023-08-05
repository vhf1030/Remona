import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webserver.config.settings')

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps
from django.utils import timezone
# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)

from webserver.app.models import ReserveInfo

reserve_info = ReserveInfo(check_datetime=timezone.now(), rsv_datetime=timezone.now())
print(reserve_info.date_created)  # Check the value here

