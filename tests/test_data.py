from data.scrap import Scraper
from data.parse import Parser
from data.insert import insert_parsed_data

scraper = Scraper(limit=1000)
print(len(scraper.rawdata))
scraper.rawdata[1]

parser = Parser(scraper.rawdata, scraper.res_info)
parser.parse_rawdata_item(scraper.rawdata[1])

parser.parse_all()
len(parser.parsed)
res = parser.parsed

# res[897]['meta_info']
# insert_parsed_data 함수 실행
# parser.parsed = parser.parsed[:10]
insert_parsed_data(parser)