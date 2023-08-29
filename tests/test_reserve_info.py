import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps
# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)

from app.models import MetaInfo, ReserveInfo

from app.views import join_theme_info

from django.forms.models import model_to_dict

theme_info = join_theme_info()
print(theme_info.values()[0])

MetaInfo.objects.get(theme_id=1)
reserve_tmp = ReserveInfo.objects.filter(theme__theme_id=1)
print(reserve_tmp.values()[0])
print(model_to_dict(reserve_tmp.first()))

latest_record = reserve_tmp.latest('check_date_hour')
print(model_to_dict(latest_record))

# todo: 테마별 score info, reserve info 마지막 기준 시간 추출
latest_check_date_hour = latest_record.check_date_hour

reserve_tmp.order_by('-check_date_hour').values('check_date_hour')
reserve_tmp.order_by('-check_date_hour').values_list('check_date_hour')

# 1. 메타 필터 적용된 테마 쿼리셋
# 2. 예약 시간 필터링

