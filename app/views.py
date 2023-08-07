from django.shortcuts import render

# Create your views here.
from .models import MetaInfo, ScoreInfo, ReserveInfo


def metainfo_list(request):
    metainfos = MetaInfo.objects.all()
    context = {'metainfos': metainfos}
    return render(request, 'theme_info.html', context)

def reserve_info(request):
    reserve_info_list = ReserveInfo.objects.all()
    return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})


