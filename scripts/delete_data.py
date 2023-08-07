import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webserver.config.settings')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps
# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)

from app.models import MetaInfo, ScoreInfo, ReserveInfo

MetaInfo.objects.all().delete()
ScoreInfo.objects.all().delete()
ReserveInfo.objects.all().delete()

from django.db import connection
# id 초기화
with connection.cursor() as cursor:
    cursor.execute("ALTER TABLE app_metainfo AUTO_INCREMENT = 1;")
    cursor.execute("ALTER TABLE app_scoreinfo AUTO_INCREMENT = 1;")
    cursor.execute("ALTER TABLE app_reserveinfo AUTO_INCREMENT = 1;")

