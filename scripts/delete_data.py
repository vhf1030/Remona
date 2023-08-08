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


from datetime import datetime
# 특정 날짜 삭제
records_to_delete = ScoreInfo.objects.filter(check_date="2023-08-08")
# 필터링된 레코드들을 삭제
records_to_delete.delete()
