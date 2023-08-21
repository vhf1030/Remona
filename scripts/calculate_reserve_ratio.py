import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webserver.config.settings')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps
# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)


from datetime import timedelta
from django.db.models.functions import TruncHour
from app.models import ReserveInfo

# check_date_hour 필드에서 날짜와 시간을 포함한 고유한 값들을 추출합니다.
distinct_date_hours = ReserveInfo.objects.annotate(
    date_hour_only=TruncHour('check_date_hour')
).values('date_hour_only').distinct()
print(len(distinct_date_hours))

for date_hour_entry in distinct_date_hours:
    date_hour = date_hour_entry['date_hour_only']
    # 바로 다음날의 날짜와 시간을 계산합니다.
    next_day = date_hour + timedelta(days=1)

    # 특정 테마 (id=1)에 대한 바로 다음날의 예약 가능한 시간 정보를 가져옵니다.
    next_day_availabilities = ReserveInfo.objects.filter(
        theme_id=3,
        check_date_hour=date_hour,
        rsv_datetime__date=next_day.date()
    )

    rsv_all = len(distinct_date_hours) * 10
    rsv_cnt = 0
    print(f"check_time {date_hour}:")
    for availability in next_day_availabilities:
        print(f"Available time: {availability.rsv_datetime}")



from datetime import datetime, timedelta
from app.models import ReserveInfo, MetaInfo

# 해당 테마에 대한 모든 예약 정보를 가져옵니다.
# theme_reservations = ReserveInfo.objects.filter(theme=meta_info)
theme_id = 600
theme_reservations = ReserveInfo.objects.filter(theme_id=theme_id)
print(len(theme_reservations), MetaInfo.objects.filter(theme_id=theme_id)[0].theme_name)
grouped_data = {}
available_cnt = 0
for reservation in theme_reservations:
    check_date_hour = reservation.check_date_hour
    if check_date_hour not in grouped_data:
        grouped_data[check_date_hour] = []
    if check_date_hour.date() + timedelta(days=1) == reservation.rsv_datetime.date():
        grouped_data[check_date_hour].append(reservation.rsv_datetime)
        available_cnt += 1

day_reservation = max([len(grouped_data[k]) for k in grouped_data] + [10])  # 임시로 지정
available_rate = available_cnt / (len(grouped_data) * day_reservation)
reserve_rate = round(1 - available_rate, 2)

# 각 check_date_hour에 대한 바로 다음날의 예약 가능한 시간 정보를 저장하기 위한 딕셔너리
next_day_availabilities = {}

for reservation in theme_reservations:
    check_date_hour = reservation.check_date_hour
    next_day = check_date_hour + timedelta(days=1)

    # 바로 다음날의 예약 가능한 시간 정보를 가져옵니다.
    available_times = theme_reservations.filter(rsv_datetime__date=next_day.date()).values_list('rsv_datetime', flat=True)

    # 결과를 딕셔너리에 저장합니다.
    next_day_availabilities[check_date_hour] = list(available_times)

# 결과를 출력합니다.
for check_time, available_times in next_day_availabilities.items():
    print(f"For check date and hour {check_time}:")
    for time in available_times:
        print(f"Available time: {time}")