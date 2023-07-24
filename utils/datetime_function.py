from datetime import datetime, timedelta, time


def get_abs_datetime(date_diff: str, abs_time: str, cur_datetime: datetime = datetime.now()) -> bool | datetime:
    # 날짜 차이를 이용하여 절대 시간 계산
    try:
        int(date_diff)
    except ValueError:
        print(date_diff)
        return False
    cur_date = cur_datetime.date()
    res_date = cur_date + timedelta(days=int(date_diff))
    if int(abs_time[:2]) >= 24:  # 24시 이후
        abs_time = str(int(abs_time[:2]) - 24).zfill(2) + abs_time[2:]
        res_date += timedelta(days=1)
    res_time = time.fromisoformat(abs_time)
    res_datetime = datetime.combine(res_date, res_time)
    return res_datetime

