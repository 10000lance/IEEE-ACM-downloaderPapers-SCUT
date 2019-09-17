import os
print(os.path.abspath('.'))

from urllib.parse import urlencode
import tools
from lxml import etree
import time
from MyWebdriver import MyWebdriver

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

def test_acm():
	url = 'https://dl.acm.org/citation.cfm?doid=3092627.3092632'
	response = tools.requestsGet(url, headers=headers)
	# print(response.content)
	# print(response.text)
	# with open('test.html', 'w', encoding='utf-8') as f:
	# 	f.write(response.text)
	# 	f.close()
	html = etree.HTML(response.text)
	# aTags = html.xpath('//a')
	# for aTag in aTags:
	# 	print(aTag.text)

	aTag = html.xpath('//a[contains(@title, "FullText PDF")]')[0]
	print(aTag.xpath('./text()'))
	imgTag = html.xpath('//a[contains(@title, "FullText PDF")]/img')[0]
	print(imgTag.tail)
	# aTag = html.xpath('//a[contains(@title, "Author Profile Page")]')[0]
	# print(aTag.text)
	# aTag.text = 'lance'
	# print(aTag.text)

def test_ieee():
	url = 'https://ieeexplore.ieee.org/document/915037'
	response = tools.requestsGet(url, headers=headers)
	print(response.text)
	html = etree.HTML(response.text)
	pdfTag = html.xpath('//*[@id="LayoutWrapper"]/div/div/div/div[5]/div[2]/xpl-root/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[3]/div[2]/div[2]/xpl-document-toolbar/div/div/ul/li[1]/a')
	print(pdfTag)


if __name__ == '__main__':
	# test_acm()
	test_ieee()
