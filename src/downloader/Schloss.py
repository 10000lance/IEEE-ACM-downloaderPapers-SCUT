import sys
sys.path.append('../')

import tools

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

def getAbstract(MyWebdriver, logPath='', warningPath=''):
	abstract = ''
	#获取abstract
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('/html/body/font/div/font[2]/div'))
		abstractTag = MyWebdriver.find_element_by_xpath('/html/body/font/div/font[2]/div')
	except Exception as e:
		warningInfo = 'Can not get the abstract from this page\n                Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		abstracts = (abstractTag.text.split('\n')[1 : ]) if len(abstractTag.text.split('\n')) > 0 else []
		for abs in abstracts:
			abstract += abs
		successInfo = 'Successfully get the abstract from this page'
		if abstract == '':
			successInfo = '!!!Successfully get the abstract from this page, but the abstract is None'
		tools.log(successInfo, logPath)
		# print(abstract)

	return abstract

def getReferences(MyWebdriver, logPath='', warningPath=''):
	references = []
	warningInfo = 'Can not get the references from this page, for the page has no references'
	tools.warning(warningInfo, warningPath)

	return references

def getCitedInPapers(MyWebdriver, logPath='', warningPath=''):
	citedInPapers = []

	warningInfo = 'Can not get the citedInPapers from this page, for this page has no citedInPapers'
	tools.warning(warningInfo, warningPath)

	return citedInPapers

def getPdfURL(MyWebdriver, logPath='', warningPath=''):
	pdfURL = ''
	#获取pdfURL
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('/html/body/font/div/font[2]/table/tbody/tr/td[2]/table/tbody/tr/td/font/a'))
		downloadTag = MyWebdriver.find_element_by_xpath('/html/body/font/div/font[2]/table/tbody/tr/td[2]/table/tbody/tr/td/font/a')
	except Exception as e:
		warningInfo = 'Can not get the pdfURL from this page\n              Failed info:{0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		pdfURL = downloadTag.get_attribute('href')
		successInfo = 'Successfully get the pdfURL from this page'
		if pdfURL == None:
			pdfURL = ''
			successInfo = '!!!Successfully get the pdfURL from this page, but the pdfURL is None'
		tools.log(successInfo, logPath)

	# print(pdfURL)
	return pdfURL

def getPaperInfo(MyWebdriver, logPath='', warningPath=''):
	return {
		'pdfURL': getPdfURL(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'abstract': getAbstract(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'references': getReferences(MyWebdriver, logPath=logPath, warningPath=warningPath),
		'citedInPapers': getCitedInPapers(MyWebdriver, logPath=logPath, warningPath=warningPath),
	}


if __name__ == '__main__':
	from MyWebdriver import MyWebdriver

	def test_getPaperInfo():
		import json

		myWebdriver = MyWebdriver()

		# url = 'http://drops.dagstuhl.de/opus/volltexte/2011/3082/'
		url = 'https://doi.org/10.4230/OASIcs.ASD.2019.7'
		myWebdriver.get(url)
		infos = getPaperInfo(myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
		print(json.dumps(infos, indent=4, separators=(',', ': ')))

	test_getPaperInfo()