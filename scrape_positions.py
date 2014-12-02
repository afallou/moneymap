import urllib3
from scrapy.selector import Selector
from scrapy.http import HtmlResponse 

url = "http://www.opencongress.org/bill/hr152-113/bill_positions"

http = urllib3.PoolManager()
r = http.request('GET', url)
html_str = r.data.decode('utf-8')
supporting_xpath = "/html/body/div[3]/div[3]/div/div[1]/div/div[1]/ul/li/text()"
org_list = Selector(text=html_str).xpath(supporting_xpath)
supporting_list = [org.extract() for org in org_list]
print "supporting"
for cur_string in supporting_list:
	print cur_string

opposing_xpath = "/html/body/div[3]/div[3]/div/div[1]/div/div[2]/ul/li/text()"
org_list = Selector(text=html_str).xpath(opposing_xpath)
opposing_list = [org.extract() for org in org_list]
print "opposing"
for cur_string in opposing_list:
	print cur_string
#webFile = urllib3.urlopen(url).read()
#print webFile
