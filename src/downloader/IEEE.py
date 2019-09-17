import sys
sys.path.append('../')

from lxml import etree
import time
import random
from selenium.webdriver.common.keys import Keys
import tools

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}
references_baseURL = 'https://ieeexplore.ieee.org/xpl/dwnldReferences?arnumber='

def getAbstract(MyWebdriver, logPath='', warningPath=''):
	abstract = ''
	try:
		#确保abstractTag元素加载出来
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//xpl-document-abstract/section/div[2]/div[1]/div/div/div'))
		abstractTag = MyWebdriver.find_element_by_xpath('//xpl-document-abstract/section/div[2]/div[1]/div/div/div')
	except Exception as e:
		warningInfo = 'Can not find abstract element from this page\n		    	Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		abstract = abstractTag.text
		successInfo = 'Successfully get the abstract from this page'
		if abstract == '':
			successInfo = '!!!Successfully get the abstract, but abstract is None'
		tools.log(successInfo, logPath)

	return abstract

def getReferences(MyWebdriver, logPath='', warningPath=''):
	references = []

	#获取referencesBtn这个按钮元素，若元素存在，可点击滚动到references区域；若不存在，该页面无references
	referencesBtn = None
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="document-tabs"]/div/a'))
		btns = MyWebdriver.find_elements_by_xpath('//*[@id="document-tabs"]/div/a')
	except Exception as e:
		warningInfo = 'Can not get the references from this page\n		    	Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
		return references
	else:
		for btn in btns:
			if btn.text == 'References':
				referencesBtn = btn
				break

	#无referencesBtn这个元素
	if referencesBtn == None:
		warningInfo = 'Can not get references from this page, for this page has no references'
		tools.warning(warningInfo, warningPath)
		return references

	#referencesBtn元素存在
	try:
		referencesBtn.send_keys(Keys.ENTER)
	except Exception as e:
		warningInfo = 'Can not get the references from this page\n		    	Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		try:
			referencesTag = MyWebdriver.find_elements_by_xpath('//*[@id="references-section-container"]/div/div/xpl-reference-item-migr/div/div/span[2]')
		except Exception as e:
			warningInfo = 'Can not get the references from this page\n		    	Failed info: {0}'.format(repr(e))
			tools.warning(warningInfo, warningPath)
		else:
			length = len(referencesTag)
			if length == 0:
				logInfo = '!!!Successfully get the references, but the references is None'
				tools.log(logInfo, logPath)
			else:
				referencesTag = referencesTag[int(length/2) : ]
				for referenceTag in referencesTag:
					#可能会出现‘element can not attach’的错误
					try:
						references.append(referenceTag.text)
					except Exception as e:
						warningInfo = 'Can not get the {0}th reference from this page\n             Failed info: {1}'.format(referencesTag.index(referenceTag), repr(e))
						tools.warning(warningInfo, warningPath)

				logInfo = 'Successfully get the references from this page'
				tools.log(logInfo, logPath)

	return references

def getCitedInPapers(MyWebdriver, logPath='', warningPath=''):
	citedInPapers = []

	#citedInPapersBtn，若元素存在，citedInPapers；若不存在，该页面无citedInPapers
	citedInPapersBtn = None
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="document-tabs"]/div/a'))
		btns = MyWebdriver.find_elements_by_xpath('//*[@id="document-tabs"]/div/a')
	except Exception as e:
		warningInfo = 'Can not get the citedInPapers from this page\n		    	Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
		return citedInPapers
	else:
		for btn in btns:
			if btn.text == 'Citations':
				citedInPapersBtn = btn

	#citedInPapersBtn不存在
	if citedInPapersBtn == None:
		warningInfo = 'Can not get citedInPapers from this page, for this page has no citedInPapers'
		tools.warning(warningInfo, warningPath)
		return citedInPapers

	#获取citedInPapers
	#ieee中引用分为两类 citedInPapers-IEEE 和 citedInPapers-otherPublishers
	try:
		citedInPapersBtn.send_keys(Keys.ENTER)
	except Exception as e:
		warningInfo = 'Can not get citedInPapers from this page\n               Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		#第一类citedInPapers
		try:
			MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="anchor-paper-citations-ieee"]/div/div/div/span[2]'))
			citedInPapersTag = MyWebdriver.find_elements_by_xpath('//*[@id="anchor-paper-citations-ieee"]/div/div/div/span[2]')
		except Exception as e:
			warningInfo = 'Can not get the citedInPapers-IEEE from this page\n              Failed Info: {0}'.format(repr(e))
			tools.warning(warningInfo, warningPath)
		else:
			length = len(citedInPapersTag)
			if length != 0:
				for citedInPaperTag in citedInPapersTag[int(length/2) : ]:
					#可能会出项‘element can not attach’的错误
					try:
						citedInPapers.append(citedInPaperTag.text)
					except Exception as e:
						warningInfo = 'Can not get the {0}th citedInPaper-IEEE from this page\n             Failed info: {1}'.format(citedInPapersTag.index(citedInPaperTag), repr(e))
						tools.warning(warningInfo, warningPath)

		time.sleep(3)
		#第二类citedInPapers
		try:
			MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="anchor-paper-citations-nonieee"]/div/div/div/span[2]'))
			citedInPapersTag2 = MyWebdriver.find_elements_by_xpath('//*[@id="anchor-paper-citations-nonieee"]/div/div/div/span[2]')
		except Exception as e:
			warningInfo = 'Can not get the citedInPapers-other publishers from this page\n              Failed info: {0}'.format(repr(e))
			tools.warning(warningInfo, warningPath)
		else:
			for citedInPaperTag2 in citedInPapersTag2:
				#可能会出项‘element can not attach’的错误
				try:
					citedInPapers.append(citedInPaperTag2.text)
				except Exception as e:
					warningInfo = 'Can not get the {0}th citedInPaper-other publishers from this page\n             Failed info: {1}'.format(citedInPapersTag2.index(citedInPaperTag2), repr(e))
					tools.warning(warningInfo, warningPath)

		if len(citedInPapers) == 0:
			warningInfo = 'Can not get the citedInPapers from this page, for this page has no citedInPapers'
			tools.warning(warningInfo, warningPath)
		else:
			successInfo = 'Successfully get the citedInPapers from this page'
			tools.log(successInfo, logPath)

	return citedInPapers

def getPdfURL(MyWebdriver, logPath='', warningPath=''):

	pdfBaseURL = 'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='
	#获取当前页面url（因为会跳转），所以在此取得实际url
	current_url = MyWebdriver.current_url()
	#获取论文的number，用于拼接pdf页面的url
	paperNumber = current_url.split('/')[-1].split('?')[0]
	pdfHtmlURL = pdfBaseURL + paperNumber
	# print('pdfHtmlURL: ' + pdfHtmlURL)

	pdfURL = ''

	#无法打开pdfHtml页面
	response = tools.requestsGet(pdfHtmlURL, headers=headers, times=2, logPath=logPath, warningPath=warningPath)
	if response == '':
		warningInfo = 'Can not get the pdfURL from this page, for failed to get the pdfHtml {0}'.format(pdfHtmlURL)
		tools.warning(warningInfo, warningPath)
		return pdfURL

	#获取pdfURL
	try:
		pdfHtml = etree.HTML(response.content)
		iframe = pdfHtml.xpath('//iframe')[0]
	except Exception as e:
		warningInfo = 'Can not get the pdfURL from this page {0}\n              Failed info: {1}'.format(pdfHtmlURL, repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		pdfURL = iframe.get('src').split('?')[0]
		successInfo = 'Successfully get the pdfURL from this page'
		if pdfURL == '':
			successInfo = '!!!Successfully get the pdfURL from this page, but the pdfURL is None'
		tools.log(successInfo, logPath)
		# print(pdfURL)

	return pdfURL

def getPaperInfo(MyWebdriver, logPath='', warningPath=''):
	return {
		#先获取pdfURL，若后面再获取pdfURL，还需要再对url进行处理
		'pdfURL': getPdfURL(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'abstract': getAbstract(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'references': getReferences(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'citedInPapers': getCitedInPapers(MyWebdriver, logPath=logPath, warningPath=warningPath),
	}

#在IEEE中查找论文，返回论文地址
def search(title, logPath='', warningPath=''):
	def compareTitle(title, resultTitle):
		title, resultTitle = [ x.replace(' ', '')\
		                        .replace('-', '')\
		                        .replace(',', '')\
		                        .replace(':', '')\
		                        .replace('.', '')\
		                        .lower()
		                       for x in [title, resultTitle]
		                    ]
		return resultTitle.find(title) == 0

	title = title.strip('.')
	baseURL = 'https://ieeexplore.ieee.org'
	baseSearchUrl = 'https://ieeexplore.ieee.org/rest/search'
	headers = {
		'Host': 'ieeexplore.ieee.org',
		'Origin': 'https://ieeexplore.ieee.org',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
	}
	jsonData = {
		'highline': True,
		'newsearch': True,
		'queryText': title,
		'returnType': 'SEARCH',
		'returnFacets': ['ALL'],
	}

	newURL = ''

	response = tools.requestsPost(baseSearchUrl, json=jsonData, headers=headers, times=2, logPath=logPath, warningPath=warningPath)
	#请求搜索页面失败
	if response == '':
		warningInfo = 'Failed search <{0}> in IEEE, For can not open the search page'.format(title)
		tools.warning(warningInfo, warningPath)
		return newURL

	#返回不是json结果
	try:
		response = response.json()
	except Exception as e:
		warningInfo = 'Failed search <{0}> in IEEE, For can not get the search result'.format(title)
		tools.warning(warningInfo, warningPath)
		return newURL

	#搜索成功
	if (response.__contains__('records')) and (len(response['records']) > 0):
		resultJson = response['records'][0]
		# print(resultJson)
		articleTitle = resultJson['articleTitle']
		# print(articleTitle)
		#有对应的正确结果
		if compareTitle(title, articleTitle) and 'htmlLink' in resultJson.keys():
			# print(type(resultJson))
			newURL = baseURL + resultJson['htmlLink']
			logInfo = 'Successfully find <{0}> in IEEE,and newURL is {1}'.format(title, newURL)
			tools.log(logInfo, logPath)
			return newURL
	#无对应正确结果
	warningInfo = 'Failed to find <{0}> in IEEE, For none matched result'.format(title)
	tools.log(warningInfo, warningPath)

	return newURL

if __name__ == '__main__':
	from MyWebdriver import MyWebdriver

	def test_getPaperInfo():
		import json

		myWebdriver = MyWebdriver()

		urls = [
			# 'https://doi.org/10.1109/DATE.2001.915037',
			# 'https://doi.org/10.1109/DATE.2001.915090',
			# 'https://doi.org/10.1109/DATE.2001.915001',
			# 'https://doi.org/10.1109/DATE.2001.915008',
			# 'https://doi.org/10.1109/DATE.2001.915171',
			# 'https://doi.org/10.1109/DATE.2001.915016',
			# 'https://doi.org/10.1109/DATE.2001.915024',
			# 'https://doi.org/10.1109/DATE.2001.915028',
			# 'https://doi.org/10.1109/DATE.2009.5090865',
			# 'https://doi.org/10.1109/DATE.2001.915083',
			# 'https://doi.org/10.1109/DATE.2001.915050',
			# 'https://ieeexplore.ieee.org/document/998473',
			# 'https://ieeexplore.ieee.org/document/998470',
			# 'https://dl.acm.org/citation.cfm?id=367109'
			'https://doi.org/10.1109/DATE.2009.5090799',
		]
		for url in urls:
			print(url)
			myWebdriver.get(url)
			infos = getPaperInfo(myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
			with open('./json.txt', 'a', encoding='utf-8') as f:
				f.write(json.dumps(infos, indent=4, separators=(',', ': ')))
				f.write('\n')
				f.close()
			# print(json.dumps(infos, indent=4, separators=(',', ': ')))
			time.sleep(random.randint(60, 70))

	def test_search():
		# title = 'Methods and tools for systems engineering of automotive electronic architectures'
		# title = 'Minimizing the number of floating bias voltage sources with integer linear programming'
		title = 'Implications of Technology Trends on System Dependability.'
		newURL = search(title, logPath='TestLog.txt', warningPath='TestWarning.txt')
		print(newURL)

	test_search()
	# test_getPaperInfo()