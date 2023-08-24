from datetime import timedelta
from app.models import ReserveInfo


def check_reservation_rate(theme):
    theme_reservations = ReserveInfo.objects.filter(theme=theme)
    # theme_id = 1
    # theme_reservations = ReserveInfo.objects.filter(theme_id=theme_id)
    # print(len(theme_reservations), MetaInfo.objects.filter(theme_id=theme_id)[0].theme_name)
    grouped_data = {}
    available_cnt = 0
    for reservation in theme_reservations:
        check_date_hour = reservation.check_date_hour
        if check_date_hour not in grouped_data:
            grouped_data[check_date_hour] = []
        if check_date_hour.date() + timedelta(days=1) == reservation.rsv_datetime.date():
            grouped_data[check_date_hour].append(reservation.rsv_datetime)
            available_cnt += 1
    day_reservation = max([len(grouped_data[k]) for k in grouped_data] + [8])  # 임시로 지정  # todo: 로직 보강
    available_rate = available_cnt / (len(grouped_data) * day_reservation) if grouped_data else 0
    reserve_rate = round(1 - available_rate, 2)
    return reserve_rate