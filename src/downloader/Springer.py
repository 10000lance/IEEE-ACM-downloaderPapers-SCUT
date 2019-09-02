import sys
sys.path.append('../')

import os
import tools

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

base_URL = 'https://link.springer.com/'

def getAbstract(MyWebdriver, logPath='', warningPath=''):
	abstract = ''
	#获取abstract
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="Abs1"]/p'))
		abstractsTag = MyWebdriver.find_elements_by_xpath('//*[@id="Abs1"]/p')
	except Exception as e:
		warningInfo = 'Can not get the abstract from this page\n                Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		for abstractTag in abstractsTag:
			# print(abstractTag.text)
			abstract += abstractTag.text
		successInfo = 'Successfully get the abstract from this page'
		if abstract == '':
			successInfo = '!!!Successfully get the abstract from this page, but the abstract is None'
		tools.log(successInfo, logPath)
		# print(abstract)

	return abstract

def getReferences(MyWebdriver, logPath='', warningPath=''):
	references = []
	#获取references
	try:
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="Bib1"]/div/ol/li'))
		referencesTag = MyWebdriver.find_elements_by_xpath('//*[@id="Bib1"]/div/ol/li')
	except Exception as e:
		warningInfo = 'Can not get the references from this page\n              Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		for referenceTag in referencesTag:
			# print(referenceTag.text.replace('\n', ''))
			references.append(referenceTag.text.replace('\n', ''))
		successInfo = 'Successfully get the references from this page'
		if len(references) == 0:
			successInfo = '!!!Successfully get the references from this page, but the references is None'
		tools.log(successInfo, logPath)

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
		MyWebdriver.WebDriverWait_until(30, lambda x: x.find_element_by_xpath('//*[@id="cobranding-and-download-availability-text"]/div/a'))
		downloadTag = MyWebdriver.find_element_by_xpath('//*[@id="cobranding-and-download-availability-text"]/div/a')
	except Exception as e:
		warningInfo = 'Can not get the pdfURL from this page\n              Failed info: {0}'.format(repr(e))
		tools.warning(warningInfo, warningPath)
	else:
		# print(downloadTag.get_attribute('href'))
		pdfURL = downloadTag.get_attribute('href')
		if pdfURL != None and pdfURL.find('https://link.springer.com') != 0:
			pdfURL = os.path.join(base_URL, downloadTag.get_attribute('href'))

		successInfo = 'Successfully get the pdfURL from this page'
		if pdfURL == '' or pdfURL == None:
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

		url = 'https://link.springer.com/chapter/10.1007%2F978-3-642-24322-6_22'
		myWebdriver.get(url)
		infos = getPaperInfo(myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
		print(json.dumps(infos, indent=4, separators=(',', ': ')))

	test_getPaperInfo()