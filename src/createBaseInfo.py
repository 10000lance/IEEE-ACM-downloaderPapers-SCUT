from lxml import etree
import os
import projectInfo
import tools

defaultPath = '../papers/'
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

def getBaseInfoURL(conference, logPath='', warningPath=''):
	"""获取会议内每个年份的xml文档地址

	:param conference: 会议名
	:param logPath: log日志地址
	:param warningPath: warning日志地址
	:return: 成功则返回xml地址集合
	"""
	baseUrl = 'https://dblp.org/db/'
	url = baseUrl + conference
	urls = []
	response = tools.requestsGet(url, headers=headers, logPath=logPath, warningPath=warningPath)
	#若获取页面失败，返回的response为空字串，返回的xmlsUrl为空列表
	if response == '':
		return urls
	html = etree.HTML(response.text)

	#会议返回的是每个年份的xml
	if conference.find('conf/') == 0:
		urls = html.xpath('//a[contains(@href, ".xml")]/attribute::href')
	#期刊返回的是每个volume的html
	# elif conference.find('journals/') == 0:
	# 	urls = html.xpath('//*[@id="main"]/ul/li/a')

	# for xmlUrl in xmlsUrl:
	#     print(xmlUrl)
	# print(len(xmlsUrl))
	return urls

def createBaseInfoXML(conference, papersfolderPath=defaultPath, logPath='', warningPath=''):
	"""构建会议里的每个年份的基本信息（xml文档包括年份、volume、出版社）

	:param conference: 会议/期刊名
	:param papersfolderPath: 存储论文集的根目录
	:param logPath: log日志路径（使用绝对路径）
	:param warningPath: warning日志路径（使用绝对路径）
	:return:
	"""
	baseUrl = 'https://dblp.org/'

	#若该文件夹已存在，则返回
	if os.path.exists(papersfolderPath + conference):
		# warningInfo = '{0} has exists already'.format(papersfolderPath + conference)
		# tools.warning(warningInfo, warningPath)
		return

	#为该会议/期刊创建一个文件夹
	os.makedirs(papersfolderPath + conference)

	if conference.find('conf/') == 0:
		#为该会议xml文档创建一个Conference最外层标签
		root = etree.Element('Conference', name = conference)
		# print(etree.tostring(root))
		xmlsUrl = getBaseInfoURL(conference, logPath=logPath, warningPath=warningPath)
		#遍历每个年份的xml文档
		for xmlUrl in xmlsUrl:
			response = tools.requestsGet(xmlUrl, headers = headers, logPath=logPath, warningPath=warningPath)

			#若获取页面失败，返回的response为空字串
			if response == '':
				warningInfo = 'Failed to get the dblps from the page {0}'.format(xmlUrl)
				tools.warning(warningInfo, warningPath)
				continue

			xml = etree.fromstring(response.content)
			dblps = xml.xpath('/dblp')
			for dblp in dblps:
				# print(etree.tostring(dblp))
				year = dblp.xpath('//year')[0].text
				if int(year) >= projectInfo.firstYear:
					url = dblp.xpath('//url')[0].text
					name = url.split('/')[-1].split('.')[0]
					url = baseUrl + url
					publisher = dblp.xpath('//publisher')[0].text
					root.append(dblp)
					#构建每个年份的xml文档
					createPaperInfoXML(url, name, conference, publisher, papersfolderPath=papersfolderPath, logPath=logPath, warningPath=warningPath)
				else:
					break

		# print(etree.tostring(root))
		with open('{0}{1}/baseInfo.xml'.format(papersfolderPath, conference), 'wb') as f:
			f.write(etree.tostring(root))

	elif conference.find('journals/') == 0:
		journalsBaseURL = 'https://dblp.org/db/'
		response = tools.requestsGet(journalsBaseURL+conference, headers=headers, logPath=logPath, warningPath=warningPath)
		#若获取页面失败，返回的response为空字串，返回的xmlsUrl为空列表
		if response == '':
			return
		html = etree.HTML(response.text)
		volumes = html.xpath('//*[@id="main"]/ul/li/a')
		for volume in volumes:
			name = volume.text
			year = name.split(' ')[-1].split('/')[0]
			if int(year) >= projectInfo.firstYear:
				url = volume.xpath('./attribute::href')[0]
				createPaperInfoXML(url, name, conference, papersfolderPath=papersfolderPath, logPath=logPath, warningPath=warningPath)
	else:
		return

	successInfo = "{0}'s baseInfo setup".format(conference)
	tools.log(successInfo, logPath)
	tools.log('\n', logPath, hasTime=False)

def createPaperInfoXML(paperInfoUrl, name, conference, publisher='', papersfolderPath=defaultPath, logPath='', warningPath=''):
	"""构建每个年份里论文集的信息表（包括论文作者，标题，页码，下载地址）

	:param paperInfoUrl: 包含该年份所有论文信息的xml文档的url地址
	:param name: 该年份文件夹的名字
	:param conference: 该年份所属的会议
	:param publisher: 该年份论文的出版社
	:param papersfolderPath: 存储论文集根目录
	:param logPath: log日志路径（绝对路径）
	:param warningPath: warning日志路径（绝对路径）
	:return:
	"""

	name = tools.toFilename(name, False)

	#若该文件夹已存在，则返回
	if os.path.exists('{0}{1}/{2}'.format(papersfolderPath, conference, name)):
		# warningInfo = '{0}{1}/{2} has exists already'
		# tools.warning(warningInfo, warningPath)
		return

	response = tools.requestsGet(paperInfoUrl, headers=headers, logPath=logPath, warningPath=warningPath)
	#无法获取到该年份的页面
	if response == '':
		warningInfo = 'Failed to construct the {0}{1}/{2}/paperInfo.xml'.format(papersfolderPath, conference, name)
		tools.warning(warningInfo, warningPath)
		tools.warning('\n', warningPath, hasTime=False)
		return

	#查找该页面下收录了所有论文基础信息的xml文档地址
	html = etree.HTML(response.text)
	paperInfoXMLURLs = html.xpath('//a[contains(@href, "format=xml")]/attribute::href')

	#没有找到相应的xml文档地址，可能是该年份有几个volumes或xpath表达式不匹配问题
	if len(paperInfoXMLURLs) <= 0:
		name = name + '-'
		volumeURLs = html.xpath('//a[contains(@href, "{0}")]/attribute::href'.format(name))

		#也无发找到volume的地址，建议检查xpath表达式
		if len(volumeURLs) <= 0:
			warningInfo = 'Failed to get the xml address from the page {0}, Please check your xpath expression'.format(paperInfoUrl)
			tools.warning(warningInfo, warningPath)
			warningInfo = 'Failed to construct the {0}{1}/{2}/paperInfo.xml'.format(papersfolderPath, conference, name)
			tools.warning(warningInfo, warningPath)
			tools.warning('\n', warningPath, hasTime=False)
			return

		#找到volume地址，遍历每个volume，给每个volume建立xml文档
		for volumeURL in volumeURLs:
			name = volumeURL.split('/')[-1].split('.')[0]
			createPaperInfoXML(volumeURL, name, conference, publisher, logPath=logPath, warningPath=warningPath)
		return

	#找到xml文档地址并打开
	paperInfoXMLURL = paperInfoXMLURLs[0]
	response = tools.requestsGet(paperInfoXMLURL, headers=headers, logPath=logPath, warningPath=warningPath)

	#获取xml文档失败
	if response == '':
		warningInfo = 'Failed to get the xml document {0}'.format(paperInfoXMLURL)
		tools.warning(warningInfo, warningPath)
		warningInfo = 'Failed to construct the {0}{1}/{2}/paperInfo.xml'.format(papersfolderPath, conference, name)
		tools.warning(warningInfo, warningPath)
		tools.warning('\n', warningPath, hasTime=False)
		return

	#成功获取xml文档
	paperInfoXML = etree.XML(response.content)
	paperInfo = paperInfoXML.xpath('//hits')[0]

	#创建xml文档最外层标签
	root = etree.Element('Year', name=name, publisher=publisher)

	#对xml的element取len长度，返回其子节点个数
	#paperInfo的长度为0时，表示一次性抓取所有论文的Info失败时，需一个一个抓取论文的Info，再拼接到root中
	if len(paperInfo) <= 0:
		#获取该年份\volume下的所有论文的xml文档地址
		paperInfoXMLURLs = html.xpath('//a[contains(@href, ".xml")]/attribute::href')[1 : ]
		paperNum = len(paperInfoXMLURLs)
		hits = etree.Element('hits',
							 total = str(len(paperInfoXMLURLs)),
							 completed = '0',
							 current = '0')

		logInfo = 'Getting paper infos one by one, {0}/{1} has {2} papers'.format(conference, name, paperNum)
		tools.log(logInfo, logPath)

		#遍历存储论文信息的xml文档，将论文的信息拼接到一起
		for paperInfoXMLURL in paperInfoXMLURLs:
			response = tools.requestsGet(paperInfoXMLURL, headers=headers, logPath=logPath, warningPath=warningPath)
			#打开存储论文信息的xml文档失败
			if response == '':
				warningInfo = "Failed to get the paper's info from the page {0}".format(paperInfoXMLURL)
				tools.warning(warningInfo, warningPath)
				continue

			#成功打开存储论文信息的xml文档
			paperInfoXML = etree.XML(response.content)
			hit = paperInfoXML.xpath('//dblp')[0]
			hit.tag = 'hit'
			hit.set('hasDownloadPDF', 'False')
			hit.set('hasSolved', 'False')
			info = paperInfoXML.xpath('//inproceedings')[0]
			info.tag = 'info'
			hits.append(hit)

		root.append(hits)

	#可以一次性获取到所有论文的Info
	else:
		paperInfo.set('completed', '0')
		paperInfo.set('current', '0')
		paperNum = 0
		# print(paperInfo.get('total'))
		hits = paperInfo.xpath('.//hit')
		for hit in hits:
			hit.set('hasDownloadPDF', 'False')
			hit.set('hasSolved', 'False')
			#统计论文数
			if hit.find('.//pages') is not None:
				paperNum += 1
		paperInfo.set('total', str(paperNum))
		root.append(paperInfo)

	#为每个年份\volume创建文件夹
	os.makedirs('{0}{1}/{2}'.format(papersfolderPath, conference, name))
	with open('{0}{1}/{2}/paperInfo.xml'.format(papersfolderPath, conference, name), 'wb') as f:
		f.write(etree.tostring(root))
	successInfo = "{0}/{1}'s baseInfo set up, it has {2} papers totally".format(conference, name, paperNum)
	tools.log(successInfo, logPath)
	tools.log('\n', logPath, hasTime=False)
	# print(etree.tostring(root))

if __name__ == '__main__':
	for conference in projectInfo.conferences:
		createBaseInfoXML(conference, papersfolderPath=projectInfo.folderPath, logPath='TestLog.txt', warningPath='TestWarn.txt')

	# createPaperInfoXML('https://dblp.org/db/conf/date/date2004.html', 'date2004', 'date', 'IEEE', logPath='TestLog.txt', warningPath='TestWarn.txt')
	# createBaseInfoXML('vlsi')