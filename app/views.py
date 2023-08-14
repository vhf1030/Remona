from django.shortcuts import render

# Create your views here.
from django.db.models import Subquery, OuterRef
from .models import MetaInfo, ScoreInfo, ReserveInfo
from datetime import datetime, timedelta

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
    # print(location_list)
    if location_filter != '전체':  # 지역 필터
        theme_list = theme_list.filter(loc_2=location_filter)

    rating_choices = ["전체", "3.5", "4", "4.5"]
    if rating_filter != '전체':  # 평점 필터
        theme_list = theme_list.filter(satisfy_score__gte=rating_filter)

    # 정렬 적용
    sort_option_list = ['리뷰 수', '추천 비율', '난이도', '평점']
    if sort_option:
        if sort_option == '리뷰 수':
            theme_list = theme_list.order_by('-total_review')
        elif sort_option == '추천 비율':
            theme_list = theme_list.order_by('-recommend_ratio')
        elif sort_option == '난이도':
            theme_list = theme_list.order_by('-difficulty_score')
        elif sort_option == '평점':
            theme_list = theme_list.order_by('-satisfy_score')


    # 지금으로부터 1시간 이전의 시간을 계산
    hour_ago = datetime.now() - timedelta(hours=1)

    # 각 theme에 대한 최근 ReserveInfo 데이터를 가져옵니다.
    for theme in theme_list:
        # 지금으로부터 1시간 이내에 수정된 ReserveInfo 데이터를 가져오기
        latest_reserve_info = ReserveInfo.objects.filter(
            theme=theme.pk,  # 여기에 .pk를 추가하여 특정 테마의 ID를 참조하도록 함
            date_modified__gte=hour_ago
        )
        theme.latest_reserve_info = latest_reserve_info

    context = {
        'theme_list': theme_list,
        'location_list': location_list,
        'location_filter': location_filter,  # 지역 선택 출력 유지
        'rating_choices': rating_choices,
        'rating_filter': rating_filter,  # 평점 선택 출력 유지
        'sort_option_list': sort_option_list,
        'sort_option': sort_option,  # 정렬 선택 출력 유지
    }
    return render(request, 'theme_info.html', context)



def reserve_info(request):
    reserve_info_list = ReserveInfo.objects.all()
    return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})


