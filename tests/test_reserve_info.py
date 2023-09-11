import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps
# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)

from app.models import MetaInfo, ReserveInfo

from app.views import join_theme_info, get_latest_reserve_info

from django.forms.models import model_to_dict

theme_info = join_theme_info()
print(theme_info.values()[0])

MetaInfo.objects.get(theme_id=1)
reserve_info = get_latest_reserve_info()
len(reserve_info)
reserve_info.filter(theme__theme_id=1)
check_date_hours = reserve_info.filter(theme__theme_id=1).values_list('check_date_hour', flat=True)
date_hours_list = list(check_date_hours)
print(date_hours_list)

reserve_tmp = ReserveInfo.objects.filter(theme__theme_id=1)
print(reserve_tmp.values()[0])
print(model_to_dict(reserve_tmp.first()))
print(model_to_dict(reserve_tmp.last()))

latest_record = reserve_tmp.latest('check_date_hour')
print(model_to_dict(latest_record))

# todo: 테마별 score info, reserve info 마지막 기준 시간 추출
latest_check_date_hour = latest_record.check_date_hour

reserve_tmp.order_by('-check_date_hour').values('check_date_hour')
reserve_tmp.order_by('-check_date_hour').values_list('check_date_hour')

# 1. 메타 필터 적용된 테마 쿼리셋
# 2. 예약 시간 필터링

difficulty_max = float(4.0)
rating_filter = float(4.0)
from app.views import join_theme_info
theme_list = join_theme_info()
theme_list = theme_list.filter(difficulty_score__lte=difficulty_max)
theme_list = theme_list.filter(satisfy_score__gte=rating_filter)
len(theme_list)

latest_reserve_info = ReserveInfo.objects.filter(check_date_hour=latest_check_date_hour)
test = latest_reserve_info.filter(theme_id=theme_list[0])
[model_to_dict(t) for t in test]

filtered_reserve_info = latest_reserve_info.filter(
    rsv_datetime__week_day__in=[1, 2, 3],
    rsv_datetime__hour__range=(15, 20)
)
test = filtered_reserve_info.filter(theme_id=theme_list[0])
[model_to_dict(t) for t in test]



latest_reserve_info = ReserveInfo.objects.latest('check_date_hour')
model_to_dict(latest_reserve_info)
