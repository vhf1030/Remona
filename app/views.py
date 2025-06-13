from django.shortcuts import render
from django.db.models import Subquery, OuterRef
from .models import MetaInfo, ScoreInfo, ReserveInfo
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from django.db import connection
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 연결 상태 확인 함수
def is_database_available():
    try:
        connection.ensure_connection()
        return True
    except OperationalError:
        return False

# 실시간 API 데이터 가져오기
def get_realtime_data():
    """빠방 API에서 실시간 데이터를 가져옵니다."""
    from settings.data import BB_REQUEST
    from data.scrap import Scraper
    from data.parse import Parser
    
    try:
        scraper = Scraper(limit=2000)
        parser = Parser(scraper.rawdata, scraper.res_info)
        return parser.parsed
    except Exception as e:
        logger.error(f"실시간 데이터 가져오기 실패: {e}")
        return []

# 실시간 데이터를 Django 모델과 유사한 형태로 변환
def convert_to_theme_objects(parsed_data):
    """파싱된 데이터를 템플릿에서 사용할 수 있는 형태로 변환합니다."""
    theme_objects = []
    
    for data in parsed_data:
        if not data.get('popular', True):
            continue
            
        # 객체 형태로 변환
        theme_obj = type('Theme', (), {})()
        
        # 메타 정보
        meta_info = data['meta_info']
        theme_obj.theme_name = meta_info.get('theme_name', '')
        theme_obj.store_name = meta_info.get('store_name', '')
        theme_obj.rsv_url = meta_info.get('rsv_url', '')
        theme_obj.store_url = meta_info.get('store_url', '')
        theme_obj.loc_1 = meta_info.get('loc_1', '')
        theme_obj.loc_2 = meta_info.get('loc_2', '')
        
        # 점수 정보
        score_info = data['score_info']
        theme_obj.total_review = score_info.get('total_review', 0)
        theme_obj.recommend_ratio = score_info.get('recommend_ratio', 0)
        theme_obj.difficulty_score = score_info.get('difficulty_score', 0)
        theme_obj.satisfy_score = score_info.get('satisfy_score', 0)
        theme_obj.fear_score = score_info.get('fear_score', 0)
        theme_obj.story_score = score_info.get('story_score', 0)
        theme_obj.direction_score = score_info.get('direction_score', 0)
        theme_obj.interior_score = score_info.get('interior_score', 0)
        theme_obj.problem_score = score_info.get('problem_score', 0)
        theme_obj.activity_score = score_info.get('activity_score', 0)
        theme_obj.prev_1d_reservation_rate = 0.5  # 기본값
        
        # 예약 정보
        reserve_info = data['reserve_info']
        theme_obj.rsv_datetime = reserve_info.get('datetime', [])
        
        theme_objects.append(theme_obj)
    
    return theme_objects

# 필터링 함수
def apply_filters(theme_list, filters):
    """테마 리스트에 필터를 적용합니다."""
    filtered_list = []
    
    for theme in theme_list:
        # 지역 필터
        if filters.get('location_filter') and filters['location_filter'] != '전체':
            if theme.loc_2 != filters['location_filter']:
                continue
        
        # 평점 필터
        if filters.get('rating_filter') and filters['rating_filter'] != '전체':
            if theme.satisfy_score < float(filters['rating_filter']):
                continue
        
        # 난이도 필터
        if not (filters['difficulty_min'] <= theme.difficulty_score <= filters['difficulty_max']):
            continue
        
        # 공포도 필터
        if not (filters['fear_min'] <= theme.fear_score <= filters['fear_max']):
            continue
        
        # 예약 시간 필터
        if filters.get('reserve_days') and filters.get('time_min') is not None and filters.get('time_max') is not None:
            filtered_times = []
            for rsv_time in theme.rsv_datetime:
                if isinstance(rsv_time, datetime):
                    weekday = rsv_time.isoweekday()  # 1=월요일, 7=일요일
                    hour = rsv_time.hour
                    
                    if (str(weekday) in filters['reserve_days'] and 
                        filters['time_min'] <= hour < filters['time_max']):
                        filtered_times.append(rsv_time)
            
            if filters.get('available_themes_only') and not filtered_times:
                continue
            
            theme.rsv_datetime = filtered_times
        
        filtered_list.append(theme)
    
    return filtered_list

# 정렬 함수
def apply_sorting(theme_list, sort_option):
    """테마 리스트를 정렬합니다."""
    if not sort_option:
        return theme_list
    
    if sort_option == '리뷰수':
        return sorted(theme_list, key=lambda x: x.total_review, reverse=True)
    elif sort_option == '추천비율':
        return sorted(theme_list, key=lambda x: x.recommend_ratio, reverse=True)
    elif sort_option == '난이도':
        return sorted(theme_list, key=lambda x: x.difficulty_score, reverse=True)
    elif sort_option == '평점':
        return sorted(theme_list, key=lambda x: x.satisfy_score, reverse=True)
    elif sort_option == '예약률':
        return sorted(theme_list, key=lambda x: x.prev_1d_reservation_rate, reverse=True)
    
    return theme_list

# 메인 테마 정보 뷰 (데이터베이스 의존성 제거)
def theme_info_realtime(request):
    """실시간 API 데이터를 사용하는 테마 정보 뷰"""
    try:
        # 실시간 데이터 가져오기
        parsed_data = get_realtime_data()
        if not parsed_data:
            return render(request, 'theme_info.html', {
                'error_message': 'API에서 데이터를 가져올 수 없습니다.',
                'theme_list': [],
                'location_list': ['전체'],
                'rating_choices': ["전체", "3.5", "4", "4.5"],
                'sort_option_list': ['평점', '난이도', '리뷰수', '추천비율', '예약률'],
            })
        
        # 테마 객체로 변환
        theme_list = convert_to_theme_objects(parsed_data)
        
        # 필터 파라미터 가져오기
        filters = {
            'location_filter': request.GET.get('location_filter', '전체'),
            'rating_filter': request.GET.get('rating_filter', '전체'),
            'difficulty_min': float(request.GET.get('difficulty_min', 0)),
            'difficulty_max': float(request.GET.get('difficulty_max', 5)),
            'fear_min': float(request.GET.get('fear_min', 0)),
            'fear_max': float(request.GET.get('fear_max', 5)),
            'reserve_days': request.GET.getlist('days') or ['1', '2', '3', '4', '5', '6', '7'],
            'time_min': int(request.GET.get('time_min', 10)),
            'time_max': int(request.GET.get('time_max', 24)),
            'available_themes_only': request.GET.get('available_themes_only'),
        }
        
        # 필터 적용
        theme_list = apply_filters(theme_list, filters)
        
        # 정렬 적용
        sort_option = request.GET.get('sort_option')
        theme_list = apply_sorting(theme_list, sort_option)
        
        # 지역 목록 생성
        location_list = ['전체'] + list(set(theme.loc_2 for theme in theme_list if theme.loc_2))
        
        context = {
            'theme_list': theme_list,
            'location_list': location_list,
            'rating_choices': ["전체", "3.5", "4", "4.5"],
            'sort_option_list': ['평점', '난이도', '리뷰수', '추천비율', '예약률'],
            'difficulty_min': filters['difficulty_min'],
            'difficulty_max': filters['difficulty_max'],
            'fear_min': filters['fear_min'],
            'fear_max': filters['fear_max'],
            'reserve_days': filters['reserve_days'],
            'time_min': filters['time_min'],
            'time_max': filters['time_max'],
            'data_source': 'realtime'
        }
        
        return render(request, 'theme_info.html', context)
        
    except Exception as e:
        logger.error(f"실시간 테마 정보 조회 실패: {e}")
        return render(request, 'theme_info.html', {
            'error_message': f'데이터 조회 중 오류가 발생했습니다: {str(e)}',
            'theme_list': [],
            'location_list': ['전체'],
            'rating_choices': ["전체", "3.5", "4", "4.5"],
            'sort_option_list': ['평점', '난이도', '리뷰수', '추천비율', '예약률'],
        })

# 기존 데이터베이스 기반 함수들 (백업용)
def get_latest_theme_score():
    # 각 테마별 최신 check_date 확인
    latest_score_dates = ScoreInfo.objects.filter(
        theme=OuterRef('theme')
    ).order_by('-check_date').values('check_date')[:1]

    # 최신 ScoreInfo 객체
    theme_score = ScoreInfo.objects.filter(
        check_date=Subquery(latest_score_dates)
    )
    return theme_score

def get_latest_reserve_info():
    # 최신 check_date_hour 확인
    latest_reserve_date_hours = ReserveInfo.objects.last().check_date_hour

    # 최신 reserveInfo 객체
    reserve_info = ReserveInfo.objects.filter(
        check_date_hour=latest_reserve_date_hours
    )
    return reserve_info

def join_theme_info():
    # ScoreInfo 테마별 최신 데이터
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
        prev_1d_reservation_rate=Subquery(latest_score_subquery.values('prev_1d_reservation_rate')[:1]),
        # 여기에 필요한 다른 필드들을 추가하세요
    )

    return theme_info

# 통합 테마 정보 뷰 (데이터베이스 우선, 실패 시 실시간)
def theme_info(request):
    """데이터베이스가 사용 가능하면 DB를, 아니면 실시간 API를 사용합니다."""
    
    if is_database_available():
        try:
            return theme_info_database(request)
        except Exception as e:
            logger.warning(f"데이터베이스 조회 실패, 실시간 모드로 전환: {e}")
            return theme_info_realtime(request)
    else:
        logger.info("데이터베이스 연결 불가, 실시간 모드 사용")
        return theme_info_realtime(request)

# 기존 데이터베이스 기반 뷰
def theme_info_database(request):
    """기존 데이터베이스 기반 테마 정보 뷰"""
    location_filter = request.GET.get('location_filter')  # 지역 필터 출력 유지
    rating_filter = request.GET.get('rating_filter')  # 평점 필터 출력 유지
    if not rating_filter:
        rating_filter = '전체'
    sort_option = request.GET.get('sort_option')  # 정렬 옵션

    # join_theme_info()로 최신 ScoreInfo 데이터가 결합된 MetaInfo 객체를 가져옴
    theme_list = join_theme_info()

    # 필터 적용
    location_list = ['전체'] + list(theme_list.values_list('loc_2', flat=True).distinct())
    rating_choices = ["전체", "3.5", "4", "4.5"]
    difficulty_min = float(request.GET.get('difficulty_min', 0))
    difficulty_max = float(request.GET.get('difficulty_max', 5))
    fear_min = float(request.GET.get('fear_min', 0))
    fear_max = float(request.GET.get('fear_max', 5))

    if location_filter != '전체':  # 지역 필터
        theme_list = theme_list.filter(loc_2=location_filter)
    if rating_filter != '전체':  # 평점 필터
        theme_list = theme_list.filter(satisfy_score__gte=rating_filter)
    theme_list = theme_list.filter(difficulty_score__gte=difficulty_min, difficulty_score__lte=difficulty_max)
    theme_list = theme_list.filter(fear_score__gte=fear_min, fear_score__lte=fear_max)

    # 정렬 적용
    sort_option_list = ['평점', '난이도', '리뷰수', '추천비율', '예약률']
    if sort_option:
        if sort_option == '리뷰수':
            theme_list = theme_list.order_by('-total_review')
        elif sort_option == '추천비율':
            theme_list = theme_list.order_by('-recommend_ratio')
        elif sort_option == '난이도':
            theme_list = theme_list.order_by('-difficulty_score')
        elif sort_option == '평점':
            theme_list = theme_list.order_by('-satisfy_score')
        elif sort_option == '예약률':
            theme_list = theme_list.order_by('-prev_1d_reservation_rate')

    reserve_days = request.GET.getlist('days')  # 예약 요일
    if not reserve_days:
        reserve_days = ['1', '2', '3', '4', '5', '6', '7']
    time_min = int(request.GET.get('time_min', 10))
    time_max = int(request.GET.get('time_max', 24))
    available_themes_only = request.GET.get('available_themes_only')

    reserve_info = get_latest_reserve_info()

    reserve_info = reserve_info.filter(
        rsv_datetime__week_day__in=reserve_days,
        rsv_datetime__hour__range=(time_min, time_max - 1)
    )
    if available_themes_only:
        filtered_theme_ids = reserve_info.values_list('theme_id', flat=True).distinct()
        theme_list = theme_list.filter(pk__in=filtered_theme_ids)

    # 예약 가능 시간 추가
    for theme in theme_list:
        theme.rsv_datetime = reserve_info.filter(theme=theme).values_list('rsv_datetime', flat=True)

    context = {
        'theme_list': theme_list,
        'location_list': location_list,
        'rating_choices': rating_choices,
        'sort_option_list': sort_option_list,
        'difficulty_min': difficulty_min,
        'difficulty_max': difficulty_max,
        'fear_min': fear_min,
        'fear_max': fear_max,
        'reserve_days': reserve_days,
        'time_min': time_min,
        'time_max': time_max,
        'data_source': 'database'
    }
    return render(request, 'theme_info.html', context)

def reserve_info(request):
    """예약 정보 뷰 (데이터베이스 의존성 제거)"""
    if is_database_available():
        try:
            hour_ago = datetime.now() - timedelta(hours=3)
            reserve_info_list = ReserveInfo.objects.filter(date_modified__gte=hour_ago)
            return render(request, 'reserve_info.html', {'reserve_info_list': reserve_info_list})
        except Exception as e:
            logger.error(f"예약 정보 조회 실패: {e}")
    
    # 데이터베이스 사용 불가 시 실시간 데이터 사용
    try:
        parsed_data = get_realtime_data()
        reserve_info_list = []
        
        for data in parsed_data:
            if data.get('popular', True):
                reserve_times = data.get('reserve_info', {}).get('datetime', [])
                for rsv_time in reserve_times:
                    reserve_obj = type('ReserveInfo', (), {})()
                    reserve_obj.theme_name = data['meta_info'].get('theme_name', '')
                    reserve_obj.rsv_datetime = rsv_time
                    reserve_info_list.append(reserve_obj)
        
        return render(request, 'reserve_info.html', {
            'reserve_info_list': reserve_info_list,
            'data_source': 'realtime'
        })
    except Exception as e:
        logger.error(f"실시간 예약 정보 조회 실패: {e}")
        return render(request, 'reserve_info.html', {
            'reserve_info_list': [],
            'error_message': '예약 정보를 가져올 수 없습니다.'
        })


