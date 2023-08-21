import pprint
from data.scrap import Scraper
from data.parse import Parser
from data.insert import insert_parsed_data

scraper = Scraper(limit=2000)
print(len(scraper.rawdata))
# scraper.rawdata[1]
# for i, r in enumerate(scraper.rawdata):
#     if str(r['title'])[:4] == 'FILM':
#         print(i, r)

parser = Parser(scraper.rawdata, scraper.res_info)
parser.parse_rawdata_item(scraper.rawdata[1])

parser.parse_all()
len(parser.parsed)
# cnt = 0
# for i, p in enumerate(parser.parsed):
#     if p['popular'] is False:
#         print(i, p['score_info']['recommend_ratio'], p['score_info']['satisfy_score'])
#         pprint.pp(p['meta_info'])
#         cnt += 1
#
# print(cnt)

res = parser.parsed
for r in res:
    print(r['meta_info']['theme_name'])
    print(r['score_info'])
# res[897]['meta_info']
# insert_parsed_data 함수 실행
# parser.parsed = parser.parsed[:10]
insert_parsed_data(parser)
