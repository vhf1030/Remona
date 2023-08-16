from django.shortcuts import render

# Create your views here.
from django.db.models import Subquery, OuterRef, Q
from .models import MetaInfo, ScoreInfo, ReserveInfo
from datetime import datetime, timedelta
from collections import defaultdict

# def metainfo_list(request):
#     metainfos = MetaInfo.objects.all()
#     context = {'metainfos': metainfos}
#     return render(request, 'theme_info.html', context)


def get_latest_theme_score():
    # 각 테마별로 최신 check_date를 얻는다.
    latest_score_dates = ScoreInfo.objects.filter(
        theme=OuterRef('theme')
    ).order_by('-check_date').values('check_date')[:1]

    # 위에서 얻은 날짜를 이용하여 최신 ScoreInfo 객체를 얻습니다.
    theme_score = ScoreInfo.objects.filter(
        check_date=Subquery(latest_score_dates)
    )

    return theme_score


def get_recent_reserve_time(hours=3):
    hour_ago = datetime.now() - timedelta(hours=hours)
    reserve_info_records = ReserveInfo.objects.filter(date_modified__gte=hour_ago)
    result_dict = defaultdict(list)
    for record in reserve_info_records:
        result_dict[record.theme_id].append(record.rsv_datetime)
    return result_dict


def join_theme_info():
    # ScoreInfo에서 각 테마별로 최신 데이터를 얻어옵니다.
    theme_score = get_latest_theme_score()

    # Subquery 준비
    latest_score_subquery = theme_score.filter(theme=OuterRef('pk'))

    # MetaInfo 모델에 ScoreInfo 모델의 최신 데이터를 결합합니다.
    theme_info = MetaInfo.objects.annotate(
        total_review=Subquery(latest_score_subquery.values('total_review')[:1]),
        recommend_ratio=Subquery(latest_score_subquery.values('recommend_ratio')[:1]),
        difficulty_score=Subquery(latest_score_subquery.values('difficulty_score')[:1]),
        satisfy_score=Subquery(latest_score_subquery.values('satisfy_score')[:1]),
        fear_score=Subquery(latest_score_subquery.values('fear_score')[:1]),
        # 여기에 필요한 다른 필드들을 추가하세요
    )

    return theme_info


def theme_info(request):
    location_filter = request.GET.get('location_filter')  # 지역 필터 출력 유지
    rating_filter = request.GET.get('rating_filter')  # 평점 필터 출력 유지
    sort_option = request.GET.get('sort_option')  # 정렬 옵션

    # join_theme_info()로 최신 ScoreInfo 데이터가 결합된 MetaInfo 객체를 가져옴
    theme_list = join_theme_info()
    # print(vars(theme_list[0]))

    # 필터 적용
    location_list = ['전체'] + list(theme_list.values_list('loc_2', flat=True).distinct())
    rating_choices = ["전체", "3.5", "4", "4.5"]
    difficulty_min = float(request.GET.get('difficulty_min', 0))
    difficulty_max = float(request.GET.get('difficulty_max', 5))
    fear_min = float(request.GET.get('fear_min', 0))
    fear_max = float(request.GET.get('fear_max', 5))
    time_min = int(request.GET.get('time_min', 10))
    time_max = int(request.GET.get('time_max', 24))
    if location_filter != '전체':  # 지역 필터
        theme_list = theme_list.filter(loc_2=location_filter)
    if rating_filter != '전체':  # 평점 필터
        theme_list = theme_list.filter(satisfy_score__gte=rating_filter)
    theme_list = theme_list.filter(difficulty_score__gte=difficulty_min, difficulty_score__lte=difficulty_max)
    theme_list = theme_list.filter(fear_score__gte=fear_min, fear_score__lte=fear_max)

    # todo: 리팩토링 필요
    # theme_list = theme_list.filter(rsv_datetime__hour__range=(time_min, time_max - 1))
    # 예약 가능 시간으로 필터링
    hour_ago = datetime.now() - timedelta(hours=3)
    if time_min != 10 or time_max != 24:
        filtered_reserves = ReserveInfo.objects.filter(
            date_modified__gte=hour_ago,
            rsv_datetime__hour__range=(time_min, time_max - 1)
        )
        filtered_theme_ids = filtered_reserves.values_list('theme_id', flat=True).distinct()
        theme_list = theme_list.filter(pk__in=filtered_theme_ids)

    # 정렬 적용
    sort_option_list = ['평점', '난이도', '리뷰 수', '추천 비율']
    if sort_option:
        if sort_option == '리뷰 수':
            theme_list = theme_list.order_by('-total_review')
        elif sort_option == '추천 비율':
            theme_list = theme_list.order_by('-recommend_ratio')
        elif sort_option == '난이도':
            theme_list = theme_list.order_by('-difficulty_score')
        elif sort_option == '평점':
            theme_list = theme_list.order_by('-satisfy_score')

    # 예약 가능 시간 추가
    reserve_dict = get_recent_reserve_time()
    for theme in theme_list:
        theme.rsv_datetime = reserve_dict.get(theme.pk, [])

    # print(vars(theme_list[0]))
    context = {
        'theme_list': theme_list,
        'location_list': location_list,
        'location_filter': location_filter,  # 지역 선택 출력 유지
        'rating_choices': rating_choices,
        'rating_filter': rating_filter,  # 평점 선택 출력 유지
        'sort_option_list': sort_option_list,
        'sort_option': sort_option,  # 정렬 선택 출력 유지
        'difficulty_min': difficulty_min,
        'difficulty_max': difficulty_max,
        'fear_min': fear_min,
        'fear_max': fear_max,
        'time_min': time_min,
        'time_max': time_max,
    }
    return render(request, 'theme_info.html', context)


def reserve_info(request):
    hour_ago = datetime.now() - timedelta(hours=3)
    reserve_info_list = ReserveInfo.objects.filter(date_modified__gte=hour_ago)
    return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})


