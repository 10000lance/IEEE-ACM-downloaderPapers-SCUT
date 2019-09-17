import sys
sys.path.append('../')

from lxml import etree
from selenium.webdriver.common.keys import Keys
import tools

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

def getAbstract(MyWebdriver, logPath='', warningPath=''):
	#获取abstract
	abstract = ''
	try:
		#等待abstractBtn加载出来
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="tab-1011-btnEl"]'))
		abstractBtn = MyWebdriver.find_element_by_xpath('//*[@id="tab-1011-btnEl"]')
		abstractBtn.send_keys(Keys.ENTER)
		#等待abstract加载出来
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="cf_layoutareaabstract"]/div/div'))
	except Exception as e:
		warningInfo = 'Can not find the abstract element from this page\n			Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		abstract = MyWebdriver.find_element_by_xpath('//*[@id="cf_layoutareaabstract"]/div/div')
		abstract = abstract.text
		logInfo = 'Successfully get the abstract from this page'
		if abstract == 'An abstract is not available.':
			abstract = ''
			logInfo = '!!!Successfully get the abstract, but abstract is None'
		# print(abstract)
		tools.log(logInfo, logPath)

	return abstract

def getReferences(MyWebdriver, logPath='', warningPath=''):
	#获取references
	references = []
	try:
		referencesBtn = MyWebdriver.find_element_by_xpath('//*[@id="tab-1015-btnEl"]')
		referencesBtn.send_keys(Keys.ENTER)
		#等待referencesTable加载出来
		#有些页面无abstract和references，需进行处理
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="cf_layoutareareferences"]/div/table'))
	except Exception as e:
		#无references情况，获取到‘loading' 或 ’References are not available‘
		warningInfo = 'Can not get the references from this page\n			Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		#成功加载了references
		#处理references原始数据
		referencesTable = MyWebdriver.find_element_by_xpath('//*[@id="cf_layoutareareferences"]/div/table')
		referencesTable = referencesTable.text.split('\n')
		i = 1
		while i < len(referencesTable):
			references.append(referencesTable[i].strip(' '))
			i += 2
			# print(references[-1])
		logInfo = 'Successfully get the references from this page'
		if len(references) == 0:
			logInfo = '!!!Successfully get the references, but references is None'
		tools.log(logInfo, logPath)

	return references

def getCitedInPapers(MyWebdriver, logPath='', warningPath=''):
	#获取citedInPapers
	citedInPapers = []
	try:
		citedInPapersBtn = MyWebdriver.find_element_by_xpath('//*[@id="tab-1016-btnInnerEl"]')
		citedInPapersBtn.click()
		#等待referencesTable加载出来
		#有些页面无abstract和references，需进行处理
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="cf_layoutareacitedby"]/div/table'))
	except Exception as e:
		#无citedInPapers情况，获取到’Citings are not available‘获取’loading‘
		warningInfo = 'Can not get citings from this papers\n			Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		#成功加载了citedInPapers
		citedInPapersTable = MyWebdriver.find_element_by_xpath('//*[@id="cf_layoutareacitedby"]/div/table')
		citedInPapersTable = citedInPapersTable.text.split('\n')
		i = 0
		while i < len(citedInPapersTable):
			citedInPapers.append(citedInPapersTable[i].strip(' '))
			i += 1
		logInfo = 'Successfully get the citings from this page'
		if len(citedInPapers) == 0:
			logInfo = '!!!Successfully get the citings, but the citings in None'
		tools.log(logInfo, logPath)

	return citedInPapers

def getPdfURL(MyWebdriver, logPath='', warningPath=''):
	#获取pdfURL
	pdfURL = ''
	try:
		downloadTag = MyWebdriver.find_element_by_xpath('//*[@id="divmain"]/table[1]/tbody/tr/td[1]/table[1]/tbody/tr/td[2]/a')
	except Exception as e:
		warningInfo = 'Can not get the pdfURL from this page\n			Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		pdfURL = downloadTag.get_attribute('href')
		logInfo = 'Successfully get the pdfURL from this page'
		if pdfURL == '':
			logInfo = '!!!Successfully get the pdfURL, but pdfURL is None'
		tools.log(logInfo, logPath)

	return pdfURL

#ACM中使用Ajax动态加载abstract和reference等数据
def getPaperInfo(MyWebdriver, logPath='', warningPath=''):
	return {
		'pdfURL': getPdfURL(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'abstract': getAbstract(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'references': getReferences(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'citedInPapers': getCitedInPapers(MyWebdriver, logPath=logPath, warningPath=warningPath),
	}

#在ACM中查找论文，返回论文所在页面地址
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
	baseSearchUrl = 'https://dl.acm.org/results.cfm'
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
		'referer': 'https://dl.acm.org/results.cfm?',
		'upgrade-insecure-requests': '1',
	}
	data = {
		'query': title,
	}
	newURL = ''

	response = tools.requestsGet(baseSearchUrl, headers=headers, params=data, times=2, logPath=logPath, warningPath=warningPath)
	#请求搜索页面失败
	if response == '':
		warningInfo = 'Failed search <{0}> in ACM, For can not open the search page'.format(title)
		tools.warning(warningInfo, warningPath)
		return newURL

	#请求搜索页面成功
	html = etree.HTML(response.content)
	resultTitles = html.xpath('//*[@id="results"]/div[5]/div[1]/a/text()')
	#有对应正确结果
	if (len(resultTitles) > 0) and compareTitle(title, resultTitles[0]):
		newURL = html.xpath('//*[@id="results"]/div[5]/div[1]/a')[0].get('href')
		newURL = 'https://dl.acm.org/' + newURL
		logInfo = 'Successfully find <{0}> in ACM,and newURL is {1}'.format(title, newURL)
		tools.log(logInfo, logPath)
	#无对应正确结果
	else:
		warningInfo = 'Failed to find <{0}> in ACM, For none matched result'.format(title)
		tools.log(warningInfo, warningPath)

	return newURL


if __name__ == '__main__':
	from MyWebdriver import MyWebdriver

	def test_getPaperInfo():
		import json

		# url = 'https://dl.acm.org/citation.cfm?id=367109'
		url = 'https://dl.acm.org/citation.cfm?doid=3092627.3092632'
		# url = 'https://dl.acm.org/citation.cfm?doid=378239.379025'
		# url = 'https://dl.acm.org/citation.cfm?doid=2463209.2488896'

		myWebdriver = MyWebdriver()
		myWebdriver.get(url)
		infos = getPaperInfo(myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
		print(json.dumps(infos, indent=4, separators=(',', ': ')))

	def test_search():
		title = 'Optimizing Stresses for Testing DRAM Cell Defects Using Electrical Simulation'
		# title = 'Bubble Budgeting: Throughput Optimization for Dynamic Workloads by Exploiting Dark Cores in Many Core Systems'
		# title = 'SPIN - A Scalable, Packet Switched, On-Chip Micro-Network'
		newURL = search(title, logPath='TestLog.txt', warningPath='TestWarning.txt')
		print(newURL)

	# test_getPaperInfo()
	test_search()