from django.shortcuts import render

# Create your views here.
from .models import MetaInfo, ScoreInfo, ReserveInfo
from datetime import datetime, timedelta

# def metainfo_list(request):
#     metainfos = MetaInfo.objects.all()
#     context = {'metainfos': metainfos}
#     return render(request, 'theme_info.html', context)

def metainfo_list(request):
    loc_2_filter = request.GET.get('loc_2_filter')  # 필터 선택 출력 유지
    loc_2_choices = MetaInfo.objects.values_list('loc_2', flat=True).distinct()

    loc_2_value = request.GET.get('loc_2_filter', None)
    if loc_2_value:
        theme_list = MetaInfo.objects.filter(loc_2=loc_2_value)
    else:
        theme_list = MetaInfo.objects.all()

    # 지금으로부터 10분 이전의 시간을 계산
    hour_ago = datetime.now() - timedelta(hours=1)

    # 각 theme에 대한 최근 ScoreInfo 데이터를 가져오기
    for theme in theme_list:
        theme.latest_score = ScoreInfo.objects.filter(theme=theme).latest('check_date')

        # 지금으로부터 10분 이내에 수정된 ReserveInfo 데이터를 가져오기
        latest_reserve_info = ReserveInfo.objects.filter(
            theme=theme,
            date_modified__gte=hour_ago
        )  # .order_by('-date_modified').first()
        theme.latest_reserve_info = latest_reserve_info

    context = {
        'theme_list': theme_list,
        'loc_2_choices': loc_2_choices,
        'loc_2_filter': loc_2_filter  # 필터 선택 출력 유지
    }
    return render(request, 'theme_info.html', context)


def reserve_info(request):
    reserve_info_list = ReserveInfo.objects.all()
    return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})


