from typing import List, Dict, Union
from copy import deepcopy
from datetime import datetime, time, timedelta
from settings.data import BB_NAMESPACE
from utils.datetime_function import get_abs_datetime


class Parser:
    def __init__(
            self,
            rawdata: List[Dict[str, Union[bool, int, float, str, dict, list]]],
            res_info: Dict[str, Union[bool, int, str, datetime]]
    ):
        self.rawdata = rawdata
        self.res_info = res_info
        self.parsed: List[Dict[str, Dict[str, Union[float, str, List]]]] = []
        self.parse_all()

    def parse_all(self):
        for r in self.rawdata:
            print(r['title'])
            self.parsed.append(self.parse_rawdata_item(r))

    def parse_rawdata_item(self, rawdata_item: Dict[str, Union[bool, int, float, str, dict, list]]):
        rawdata_item = deepcopy(rawdata_item)
        parsed_item = {
            'meta_info': {},
            'score_info': {},
            'reserve_info': {}
        }

        # 필드명 변경
        parsed_tmp = {BB_NAMESPACE[cn]: rawdata_item.get(cn) for cn in BB_NAMESPACE}

        # metadata info
        for info_field in ['store_name', 'store_url', 'loc_1', 'loc_2', 'theme_name']:
            parsed_item['meta_info'][info_field] = parsed_tmp[info_field]

        # score info
        score_prefix = [
            'difficulty', 'satisfy', 'story', 'direction', 'interior', 'problem', 'activity', 'fear'
        ]
        rec, tot = parsed_tmp['total_recommend'], parsed_tmp['total_review']
        parsed_item['score_info']['recommend_ratio'] = round(rec / tot, 2) if tot else 0
        for sp in score_prefix:
            tot = parsed_tmp['rt_' + sp]
            cnt = parsed_tmp['rc_' + sp]
            parsed_item['score_info'][sp + '_score'] = round(tot / cnt, 2) if cnt else 0

        # reserve info
        reserve_time_info = []
        reserve_date_fields = [f for f in rawdata_item if 'reserve_times_d' in f]  # reserve_times_d0~6
        for rdf in reserve_date_fields:
            date_diff = rdf.split('reserve_times_d')[1]
            for abs_time in rawdata_item[rdf]:
                res_datetime = get_abs_datetime(date_diff, abs_time, self.res_info['datetime'])
                if res_datetime:
                    reserve_time_info.append(res_datetime)
        parsed_item['reserve_info']['datetime'] = sorted(reserve_time_info)
        url_fields = [f for f in rawdata_item if 'reserve_url' in f]
        url = [rawdata_item[f] for f in url_fields if rawdata_item[f] is not None]
        url = list(set(url))
        if len(url) > 1:
            print(url)
        parsed_item['reserve_info']['url'] = url[0] if url else ''
        return parsed_item



