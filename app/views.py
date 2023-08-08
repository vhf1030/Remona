from django.shortcuts import render

# Create your views here.
from .models import MetaInfo, ScoreInfo, ReserveInfo


# def metainfo_list(request):
#     metainfos = MetaInfo.objects.all()
#     context = {'metainfos': metainfos}
#     return render(request, 'theme_info.html', context)

def metainfo_list(request):
    loc_2_filter = request.GET.get('loc_2_filter')  # 필터 선택 출력 유지
    loc_2_choices = MetaInfo.objects.values_list('loc_2', flat=True).distinct()

    loc_2_value = request.GET.get('loc_2_filter', None)
    if loc_2_value:
        filtered_data = MetaInfo.objects.filter(loc_2=loc_2_value)
    else:
        filtered_data = MetaInfo.objects.all()

    context = {
        'metainfos': filtered_data,
        'loc_2_choices': loc_2_choices,
        'loc_2_filter': loc_2_filter  # 필터 선택 출력 유지
    }
    return render(request, 'theme_info.html', context)


def reserve_info(request):
    reserve_info_list = ReserveInfo.objects.all()
    return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})


