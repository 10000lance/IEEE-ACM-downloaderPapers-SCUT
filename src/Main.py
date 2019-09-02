from lxml import etree
import os
import time
import random
import tools
from downloader import downloader
from MyWebdriver import MyWebdriver
from createBaseInfo import createBaseInfoXML
import projectInfo

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}

def getPapers(folderPath, MyWebdriver, isDownload, minTime=20, maxTime=50):

	infoPath = os.path.join(folderPath, 'paperInfo.xml')
	# print(infoPath)

	logPath = os.path.join(folderPath, 'log.txt')
	warningPath = os.path.join(folderPath, 'warning.txt')

	with open(infoPath, 'r') as f:
		paperInfo = f.read()
		f.close()
	xml = etree.fromstring(paperInfo)
	hits = xml.xpath('//hits')[0]

	# 该年份论文的出版信息
	publisher = xml.xpath('/Year/attribute::publisher')[0]
	print('{0}出版信息: {1}'.format(folderPath, publisher))

	# 该年份的总论文数
	paperNum = int(hits.get('total'))
	print('{0}论文总数：{1}'.format(folderPath, paperNum))

	# 该年份的论文已处理数
	paperCompleted = int(hits.get('completed'))
	print('{0}已处理论文数：{1}'.format(folderPath, paperCompleted))

	# 下载完全则输出completed信息
	if (paperCompleted == paperNum):
		print('{0} has completed!!!'.format(folderPath))
		return

	#info标签内是一篇论文的信息
	hitTags = xml.xpath('//hit')
	current = 0
	for hitTag in hitTags:
		infoTag = hitTag.find('./info')

		#论文title
		title = infoTag.find('./title').text

		#有pages标签的才是一篇论文
		if (infoTag.find('./pages')) is None:
			continue

		else:
			current += 1

			hasSolved = hitTag.get('hasSolved')
			#论文未被处理过
			if (hasSolved == None or hasSolved == 'False'):
				#收录论文的网址集合
				urls = []
				for eeTag in infoTag.findall('./ee'):
					urls.append(eeTag.text)

				#无收录论文的网址
				if len(urls) == 0:
					waitingTime = 1
				else:
					waitingTime = random.randint(minTime, maxTime)

				print('\n{0}/{1}  <{2}>'.format(current, paperNum, title))
				logInfo = warningInfo = '<{0}>\n'.format(title)
				tools.log(logInfo, logPath, hasTime=False, isPrint=False)
				tools.warning(warningInfo, warningPath, hasTime=False, isPrint=False)

				#获取论文信息
				infos = downloader.getPaperInfo(urls, title, MyWebdriver, logPath=logPath, warningPath=warningPath)

				# 更新xml中的info
				tools.updateInfo(infoTag, infos, logPath=logPath, warningPath=warningPath)
				# print(etree.tostring(info))
			#论文已处理过
			else:
				print('{0}/{1}  <{2}> has solved already'.format(current, paperNum, title))
				continue

		# 下载pdf
		hasDownloadPDF = hitTag.get('hasDownloadPDF')
		# print(hasDownloadPDF)
		if isDownload and ((hasDownloadPDF == 'False') or (hasDownloadPDF == None)):

			#pdf文件路径
			pdfPath = os.path.join(folderPath, tools.toFilename(title))
			# print(pdfPath)

			#检测论文是否已经存在
			if not os.path.exists(pdfPath):
				#获取pdfURL
				pdfURLTag = infoTag.find('./pdfURL')
				pdfURL = pdfURLTag.text if pdfURLTag is not None else ''

				if downloader.downloadPDF(pdfURL, pdfPath, logPath=logPath, warningPath=warningPath):
					hitTag.set('hasDownloadPDF', 'True')
			else:
				hitTag.set('hasDownloadPDF', 'True')
				print('The paper has download already')

		# 更新completed值
		paperCompleted += 1
		hits.set('completed', str(paperCompleted))
		hitTag.set('hasSolved', 'True')

		#若更新xml文档失败，则回退paperCompleted和hasSolved
		if  not tools.write(etree.tostring(xml), infoPath, mode='wb', logPath=logPath, warningPath=warningPath):
			paperCompleted -= 1
			hits.set('completed', str(paperCompleted))
			hitTag.set('hasSolved', 'False')

		print('Sleeping {0}S...'.format(waitingTime))
		tools.log('\n', logPath=logPath, hasTime=False, isPrint=False)
		tools.warning('\n', warningPath=warningPath, hasTime=False, isPrint=False)
		time.sleep(waitingTime)

def main():
	myWebdriver = MyWebdriver()

	for conference in projectInfo.conferences:
		print(conference)
		createBaseInfoXML(conference, papersfolderPath=projectInfo.folderPath, logPath='log.txt', warningPath='warning.txt')
		folderPaths = tools.getFolders(projectInfo.folderPath, conference)
		for folderPath in folderPaths:
			getPapers(folderPath, myWebdriver, True, projectInfo.waitingTime[0], projectInfo.waitingTime[1])

	def test_IEEE():
		# test IEEE
		getPapers('../papers/date\date2009', myWebdriver, True)

	def test_ACM():
		# test ACM
		getPapers('../papers/isca/hasp2017', myWebdriver, True)
		# getPapers('../papers/dac/dac2013', myWebdriver, True)

	def test_Springer():
		# test Springer
		getPapers('../papers/vlsi/vlsisoc2009', myWebdriver, True)

	def test_Schloss():
		# test Schloss
		getPapers('../papers/date/ppes2011', myWebdriver, True)

	def test_CEUR():
		# test CEUR
		getPapers('../papers/date/ermavss2016', myWebdriver, True)

	def test_Kluwer_Technische():
		# test Kluwer and Technische
		getPapers('../papers/vlsi/vlsisoc2003', myWebdriver, True)
		# getPapers('../papers/vlsi\ifip10-5-2001', myWebdriver, True)

	def test_ieee_computer():
		#test ieee computer
		# getPapers('../papers/date/date2003', myWebdriver, True)
		getPapers('../papers/date/date2004-1', myWebdriver, True)

if __name__ == '__main__':
	main()