import os
from lxml import etree
import projectInfo
import tools
import requests
from downloader import IEEE
import time
import random

def countPaperNum(folderPath):
	'''计算某会议某年份的论文总数

	:param folderPath: 某会议某个年份的文件夹路径
	:return: 该文件夹下论文应有的数量
	'''
	num = 0
	infoPath = os.path.join(folderPath, 'paperInfo.xml')
	with open(infoPath, 'r') as f:
		paperInfo = f.read()
		f.close()
	xml = etree.fromstring(paperInfo)
	infos = xml.xpath('//hit/info')
	for info in infos:
		if (info.find('./pages')) is not None:
			num += 1
	# print('{0} has {1} papers'.format(folderPath, int(num)))
	return int(num)

def countInIEEE(folderPath):
	'''计算某会议某年份已下载的论文数量

	:param folderPath: 某会议某年份的文件夹路径
	:return: 某会议某年份已下载的论文数量
	'''

	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
	}

	num = 0
	infoPath = os.path.join(folderPath, 'paperInfo.xml')
	with open(infoPath, 'r') as f:
		paperInfo = f.read()
		f.close()
	xml = etree.fromstring(paperInfo)
	hits = xml.xpath('//hit')
	for hit in hits:
		if (hit.find('./info/pages')) is None:
			continue

		waitingTime = random.randint(10, 40)
		time.sleep(waitingTime)
		print()
		title = hit.xpath('./info/title')[0].text
		# print(title)
		ee = hit.xpath('./info/ee')[0].text
		# print('ee: {0}'.format(ee))
		if ee:
			response = tools.requestsGet(ee, headers=headers)
			if response != '':
				# print('currentURL: {0}'.format(response.url))
				if response.url.find('https://ieeexplore.ieee.org/') == 0:
					print('{0} in IEEE'.format(title))
					num += 1
					continue

		newURL = IEEE.search(title)
		if newURL != '':
			# print('newURL: {0}'.format(newURL))
			print('{0} in IEEE'.format(title))
			num += 1

	return num

if __name__ == '__main__':
	paperNumTotal = 0
	paperNumInIEEETotal = 0
	for conference in projectInfo.conferences:
		paperNumInConf = 0
		paperNumInIEEE = 0
		foldersPath = tools.getFolders(projectInfo.folderPath, conference)
		for folderPath in foldersPath:
			paperNum = countPaperNum(folderPath)
			paperNumInConf += paperNum
			paperNumTotal += paperNum

			numInIEEE = countInIEEE(folderPath)
			paperNumInIEEE += numInIEEE
			paperNumInIEEETotal += numInIEEE

			print('{0} has {1}/{2} papers in IEEE'.format(folderPath, numInIEEE, paperNum))
		print('{0} has downloaded {1}/{2} papers'.format(conference, paperNumInIEEE, paperNumInConf))
		print()
	print('{0}/{1} papers has been downloaded totally'.format(paperNumInIEEETotal, paperNumTotal))

	# response = tools.requestsGet('https://doi.org/10.1109/MICRO.2002.1176270', headers=headers)
	# if (response != ''):
	# 	print(response.url)