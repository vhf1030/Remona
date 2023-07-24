from data.scrap import Scraper
from data.parsing import Parser

scraper = Scraper(limit=100)
len(scraper.rawdata)
scraper.rawdata[0]

parser = Parser(scraper.rawdata, scraper.res_info)
parser.parse_rawdata_item(scraper.rawdata[7])

parser.parse_all()
len(parser.parsed)
res = parser.parsed
res[0]