import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webserver.config.settings')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import pymysql
pymysql.install_as_MySQLdb()

from django.conf import settings
from django.apps import apps

# Load the Django settings and applications.
apps.populate(settings.INSTALLED_APPS)

from app.models import MetaInfo, ScoreInfo, ReserveInfo


def insert_parsed_data(parser_instance):
    parsed_data = parser_instance.parsed
    check_datetime = parser_instance.res_info['datetime']
    check_date_hour = check_datetime.replace(minute=0, second=0)
    # # Make check_datetime timezone aware
    # check_datetime = timezone.make_aware(check_datetime)

    for data in parsed_data:
        meta_info_data = data['meta_info']
        score_info_data = data['score_info']
        reserve_info_data = data['reserve_info']

        # MetaInfo model에 데이터 삽입
        theme_name = meta_info_data['theme_name']
        store_name = meta_info_data['store_name']
        loc_1 = meta_info_data['loc_1']
        loc_2 = meta_info_data['loc_2']

        meta_info, created = MetaInfo.objects.update_or_create(
            theme_name=theme_name,
            store_name=store_name,
            loc_1=loc_1,
            loc_2=loc_2,
            defaults={
                'rsv_url': meta_info_data['rsv_url'],
                'store_url': meta_info_data['store_url']
            }
        )

        # ScoreInfo model에 데이터 삽입
        ScoreInfo.objects.update_or_create(
            theme=meta_info,
            check_date=check_datetime,
            # defaults={
            #     'total_review': score_info_data['total_review'],
            #     'recommend_ratio': score_info_data['recommend_ratio'],
            #     'difficulty_score': score_info_data['difficulty_score'],
            #     'satisfy_score': score_info_data['satisfy_score'],
            #     'story_score': score_info_data['story_score'],
            #     'direction_score': score_info_data['direction_score'],
            #     'interior_score': score_info_data['interior_score'],
            #     'problem_score': score_info_data['problem_score'],
            #     'activity_score': score_info_data['activity_score'],
            #     'fear_score': score_info_data['fear_score']
            # }
            defaults={k: score_info_data[k] for k in score_info_data}
        )

        # ReserveInfo model에 데이터 삽입
        for res_datetime in reserve_info_data['datetime']:
            ReserveInfo.objects.update_or_create(
                theme=meta_info,
                check_date_hour=check_date_hour,
                rsv_datetime=res_datetime
            )


# def insert_data(parsed_data):
#     for data in parsed_data:
#         meta_info = data['meta_info']
#         score_info = data['score_info']
#         reserve_info = data['reserve_info']
#
#         # MetaInfo model instance 생성
#         meta = MetaInfo(
#             theme_name=meta_info['theme_name'],
#             rsv_url=meta_info['rsv_url'],
#             store_name=meta_info['store_name'],
#             store_url=meta_info['store_url'],
#             loc_1=meta_info['loc_1'],
#             loc_2=meta_info['loc_2']
#         )
#         meta.save()
#
#         # ScoreInfo model instance 생성
#         score = ScoreInfo(
#             theme_id=meta,
#             check_datetime=timezone.now(),
#             recommend_ratio=score_info['recommend_ratio'],
#             difficulty_score=score_info['difficulty_score'],
#             satisfy_score=score_info['satisfy_score'],
#             story_score=score_info['story_score'],
#             direction_score=score_info['direction_score'],
#             interior_score=score_info['interior_score'],
#             problem_score=score_info['problem_score'],
#             activity_score=score_info['activity_score'],
#             fear_score=score_info['fear_score']
#         )
#         score.save()
#
#         # ReserveInfo model instance 생성
#         for datetime in reserve_info['datetime']:
#             reserve = ReserveInfo(
#                 theme_id=meta,
#                 check_datetime=timezone.now(),
#                 rsv_datetime=datetime
#             )
#             reserve.save()