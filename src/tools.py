import requests
import random
import time
import os
import re
from lxml import etree
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def warning(warningInfo, warningPath='', hasTime=True, isPrint=True):
	"""写入warning日志

	:param warningInfo: warning信息
	:param warningPath: warning日志路径
	:param hasTime: 是否在日志中写入时间
	:param isPrint: 是否在控制台输出
	:return: True
	"""
	if isPrint:
		print(warningInfo)
	if warningPath != '':
		with open(warningPath, 'a', encoding='utf-8')  as f:
			if hasTime:
				warningInfo += '            ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
			f.write(warningInfo)
			f.close()
	return True

def log(logInfo, logPath='', hasTime=True, isPrint=True):
	"""写入log日志

	:param logInfo: log信息
	:param logPath: log日志路径
	:param hasTime: 是否在日志中写入时间
	:param isPrint: 是否在控制台输出
	:return: True
	"""
	if isPrint:
		print(logInfo)
	if logPath != '':
		with open(logPath, 'a', encoding='utf-8') as f:
			if hasTime:
				logInfo += '            ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
			f.write(logInfo)
			f.close()
	return True

def write(file, path, mode='w', times=2, logPath='', warningPath=''):
	"""文件写入

	:param file: 要写入的文件
	:param path: 写入位置
	:param mode: 写入模式
	:param times: 写入最大尝试次数
	:param logPath: log日志位置
	:param warningPath: warning日志位置
	:return: 写入成功返回True，失败返回False
	"""
	#文件若已存在，则创建临时文件，最后再将临时文件改名、删除原文件
	if os.path.exists(path):
		tempPath = path + '.temp'
	else:
		tempPath = path

	mode += '+'

	if times <= 0:
		times = 2
	while times > 0:
		times -= 1
		print('Writing into {0}...'.format(path))
		try:
			with open(tempPath, mode) as f:
				f.write(file)
				# for chunk in file.iter_content(chunk_size=128):
				#     f.write(chunk)
				f.close()
		#写入失败
		except Exception as e:
			if times > 0:
				waitingTime = random.randint(30, 60)
				warningInfo = 'Failed to write into {0}\n        Failed info: {1}\n        waiting {2}s to write again'.format(path, repr(e), waitingTime)
			else:
				waitingTime = 0
				warningInfo = 'Failed to write into {0}\n        Failed info: {1}'.format(path, repr(e))
			warning(warningInfo, warningPath)
			#删除临时文件
			if os.path.exists(tempPath):
				os.remove(tempPath)
			time.sleep(waitingTime)
		# 成功写入
		else:
			#将新文件改名，删除原文件
			if tempPath != path:
				deletePath = path + '.delete'
				os.rename(path, deletePath)
				os.rename(tempPath, path)
				os.remove(deletePath)

			logInfo = 'successfully write into "{0}"'.format(path)
			log(logInfo, logPath)
			return True
	#写入失败，返回False
	return False

def getChrome():
	"""打开chrome

	:return: 返回chrome
	"""
	chrome_options = Options()

	#无头浏览器
	chrome_options.add_argument('--headless')
	# chrome_options.add_argument('--enable-devtools-experiments')
	# chrome_options.add_argument('--enable-ui-devtools')
	chrome = webdriver.Chrome(chrome_options=chrome_options)

	#有头浏览器
	# chrome = webdriver.Chrome()
	return chrome

def requestsGet(url, headers, params=None, times=3, logPath='', warningPath=''):
	"""封装requests的get请求，有times次请求尝试机会

	:param url: 需请求的地址
	:param headers: 伪造请求头
	:param params: 传递的参数（字典对象）
	:param times: 最大请求尝试次数
	:param logPath: log日志位置（绝对地址）
	:param warningPath: warning日志地址（绝对地址）
	:return: 请求成功返回response对象，失败返回空字串''
	"""
	if times <= 0:
		times = 3
	while times > 0:
		times -= 1
		pageURL = (url + '?' + urlencode(params)) if params != None else url
		print('Getting the page from {0}...'.format(pageURL))
		try:
			#设置180s超时
			response = requests.get(url, headers=headers, params=params, timeout=180)
		except Exception as e:
			#超时以及各种网络问题,会等待【60，100】s后再重新请求
			if times > 0:
				waitingTime = random.randint(60, 100)
				warningInfo = 'Failed to get page from {0}\n        Failed info: {1}\n        waiting {2}s to get again'.format(
					pageURL, repr(e), waitingTime)
			else:
				waitingTime = 0
				warningInfo = 'Failed to get page from {0}\n        Failed info: {1}'.format(pageURL, repr(e))
		else:
			#404等问题
			if response.status_code != 200:
				if times > 0:
					waitingTime = random.randint(60, 100)
					warningInfo = 'Failed to get the page from {0}\n        Failed info: {1} {2}\n        waiting {3}s to get again'.format(pageURL, 'Http request error', response.status_code, waitingTime)
				else:
					waitingTime = 0
					warningInfo = 'Failed to get the page from {0}\n        Failed info: {1} {2}'.format(pageURL, 'Http request error', response.status_code)
			else:
				#成功获取到页面，返回response
				successInfo = 'Successfully to get the page from {0}'.format(pageURL)
				log(successInfo, logPath)
				return response
		#只有不成功获取到页面，才会warning()
		warning(warningInfo, warningPath)
		time.sleep(waitingTime)

	#times次机会都用完后，返回
	return ''

def requestsPost(url, headers, data=None, json=None, times=3, logPath='', warningPath=''):
	"""封装requests的get请求，有times次请求尝试机会

	:param url: 需请求的地址
	:param data: 传递的参数（字典对象）
	:param json: 传递的参数（json对象）
	:param headers: 伪造请求头
	:param times: 最大请求尝试次数
	:param logPath: log日志位置（绝对地址）
	:param warningPath: warning日志地址（绝对地址）
	:return: 请求成功返回response对象，失败返回空字串''
	"""
	if times <= 0:
		times = 3
	while times > 0:
		times -= 1
		print('Getting the page from {0}...'.format(url))
		try:
			#设置180s超时
			response = requests.post(url, headers=headers, data=data, json=json, timeout=180)
		except Exception as e:
			#超时以及各种网络问题,会等待【60，100】s后再重新请求
			if times > 0:
				waitingTime = random.randint(60, 100)
				warningInfo = 'Failed to get page from {0}\n        Failed info: {1}\n        waiting {2}s to get again'.format(
					url, repr(e), waitingTime)
			else:
				waitingTime = 0
				warningInfo = 'Failed to get page from {0}\n        Failed info: {1}'.format(url, repr(e))
		else:
			#404等问题
			if response.status_code != 200:
				if times > 0:
					waitingTime = random.randint(60, 100)
					warningInfo = 'Failed to get the page from {0}\n        Failed info: {1} {2}\n        waiting {3}s to get again'.format(pageURL, 'Http request error', response.status_code, waitingTime)
				else:
					waitingTime = 0
					warningInfo = 'Failed to get the page from {0}\n        Failed info: {1} {2}'.format(url, 'Http request error', response.status_code)
			else:
				#成功获取到页面，返回response
				successInfo = 'Successfully to get the page from {0}'.format(url)
				log(successInfo, logPath)
				return response
		#只有不成功获取到页面，才会warning()
		warning(warningInfo, warningPath)
		time.sleep(waitingTime)

	#times次机会都用完后，返回
	return ''

def webdriverGet(url, MyWebdriver, times=3, logPath='', warningPath=''):
	"""封装webdriver的get方法，有times次尝试请求的机会

	:param url: 请求url
	:param MyWebdriver: MyWebdriver对象
	:param times: 最大请求尝试次数
	:param logPath: log日志路径（绝对路径）
	:param warningPath: warning日志路径（绝对路径）
	:return: 请求成功返回True，失败则返回False
	"""

	if times <= 0:
		times = 3
	while times > 0:
		times -= 1
		print('Getting the page from {0} by webdriver...'.format(url))
		try:
			#设置180s超时
			MyWebdriver.set_page_load_timeout(180)
			MyWebdriver.get(url)
		except Exception as e:
			#webdriver只能判断超时以及网络问题,会等待【60，100】s后再重新请求
			if times > 0:
				waitingTime = random.randint(60, 100)
				warningInfo = 'Failed to get page from {0} by webdriver\n        Failed info: {1}\n        waiting {2}s to get again'.format(url, repr(e), waitingTime)
			else:
				waitingTime = 0
				warningInfo = 'Failed to get page from {0} by webdriver\n        Failed info: {1}'.format(url, repr(e))

			#重启webdriver
			MyWebdriver.restart()
			warning(warningInfo, warningPath)
			time.sleep(waitingTime)
		else:
			#webdriver无方法检测是否成功打开了链接页面，只能简单从title判断
			if MyWebdriver.title() == '设置' or MyWebdriver.title() == ('file:' + url):
				warningInfo = 'Failed to get the page from {0} by webdriver, please check your url'.format(url)
				MyWebdriver.restart()
				warning(warningInfo, warningPath)
				return False
			else:
				#成功获取到页面，返回True
				successInfo = 'Successfully to get the page from {0} by webdriver'.format(url)
				log(successInfo, logPath)
				return True

	#尝试次数都使用完
	return False

def getFolders(basePath, conference):
	"""获取会议目录下的每个年份的文件夹地址

	:param basePath: 论文集存储的地址（会议的父目录）
	:param conference: 会议名
	:return: 返回会议下年份的文件夹路径的集合
	"""
	dirpath = basePath + conference
	folders = []
	foldersPath = []
	#如果会议目录存在，就遍历会议下每个年份的目录
	if os.path.exists(dirpath):
		folders = os.listdir(dirpath)
	#遍历年份，返回每个年份文件夹的路径
	for folder in folders:
		if(not os.path.isfile(os.path.join(dirpath, folder))):
			foldersPath.append(os.path.join(dirpath, folder))
	# print(foldersPath)
	# print(len(foldersPath))
	return foldersPath

def toFilename(title, isPdf=True):
	"""去掉title中的特殊字符，并添加.pdf文件后缀名

	:param title: 需处理的字符串
	:return: 对特殊字符处理过并添加.pdf文件后缀的字符串
	"""
	title = title.strip(' ').strip('.'). \
		replace('?', '？'). \
		replace('*', '✳'). \
		replace(':', '：'). \
		replace('"', '“'). \
		replace('<', '《'). \
		replace('>', '》'). \
		replace('\\', '、'). \
		replace('/', '%'). \
		replace('|', '&')
	return title + '.pdf' if isPdf else title

def updateInfo(info, infos, logPath='', warningPath=''):
	if 'ee' in infos.keys():
		eeTag = etree.Element('ee')
		eeTag.text = infos['ee']
		info.append(eeTag)

	abstractTag = info.find('./abstract')
	pdfURLTag = info.find('./pdfURL')
	referencesTag = info.find('./references')
	citedInPapersTag = info.find('./citedInPapers')

	if not abstractTag is None:
		info.remove(abstractTag)
	if not pdfURLTag is None:
		info.remove(pdfURLTag)
	if not referencesTag is None:
		info.remove(referencesTag)
	if not citedInPapersTag is None:
		info.remove(citedInPapersTag)

	# 创建abstract节点
	abstractTag = etree.Element('abstract')
	#处理特殊字符，unicode和ASCII不能编码的不能写进xml文档中
	abstractTag.text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",infos['abstract'])

	# 创建pdfURL节点
	pdfURLTag = etree.Element('pdfURL')
	pdfURLTag.text = infos['pdfURL']

	# 创建references节点
	referencesTag = etree.Element('references')
	for reference in infos['references']:
		referenceTag = etree.Element('reference')
		#处理特殊字符
		referenceTag.text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",reference)
		referencesTag.append(referenceTag)

	#创建citedInPapers节点
	citedInPapersTag = etree.Element('citedInPapers')
	for citedInPaper in infos['citedInPapers']:
		citedInPaperTag = etree.Element('citedInpaper')
		#处理特殊字符
		citedInPaperTag.text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",citedInPaper)
		citedInPapersTag.append(citedInPaperTag)

	info.append(pdfURLTag)
	info.append(abstractTag)
	info.append(referencesTag)
	info.append(citedInPapersTag)

if __name__ == '__main__':
	def test_requestsGet():
		#success test
		# url = 'http://dblp.org/db/conf/date'
		# response = requestsGet(url, headers=headers, warningPath='./TestWarning.txt', logPath='./TestLog.txt')
		# print(response.text)
		#fail test
		url = 'http://dblp.org/db/conf/dat'
		response = requestsGet(url, headers=headers, warningPath='./TestWarning.txt', logPath='./TestLog.txt')
		print(response)

	def test_requestsPost():
		import json
		title = 'Methods and tools for systems engineering of automotive electronic architectures'
		title = title.strip('.')
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
		response = requestsPost(baseSearchUrl, json=jsonData, headers=headers, times=2, logPath='TestLog.txt', warningPath='Testwarning.txt')
		print(type(response))
		print(response)
		print(response.json())
		print(json.dumps(response.json(), indent=4, separators=(',', ': ')))

	def test_webdriverGet():
		from MyWebdriver import MyWebdriver
		urls = [
			'//dblp.org/db/conf/dat',
			'http://dblp.org/db/conf/date',
		]
		myWebdriver = MyWebdriver()
		for url in urls:
			time.sleep(3)
			result = webdriverGet(url, myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
			print(myWebdriver.browser)
			if result == False:
				print('Failed')
			else:
				print(myWebdriver.current_url())

	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
	}

	# test_requestsGet()
	# test_requestsPost()
	test_webdriverGet()

