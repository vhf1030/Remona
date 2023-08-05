from typing import List, Dict, Union
import requests
from copy import deepcopy
from datetime import datetime
from settings.data import BB_REQUEST


class Scraper:
    def __init__(self, limit: int = 2000):
        self.limit = limit
        self.rawdata: List[Dict[str, Union[bool, int, float, str, dict, list]]] = []
        self.res_info: Dict[str, Union[bool, int, str, datetime]] = {}
        self.get_data()

    def get_data(self):
        req = deepcopy(BB_REQUEST)
        req['json']['limit'] = self.limit
        req_time = datetime.now()
        res = requests.post(**req).json()
        self.rawdata = res.pop('hits')
        self.res_info = res
        self.res_info['datetime'] = req_time.replace(microsecond=0)
