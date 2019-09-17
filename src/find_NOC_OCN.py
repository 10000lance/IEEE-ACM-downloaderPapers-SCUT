import os
from lxml import etree

def find_NOC_OCN(folderPath):
	outputFolder = '../NOC_OCN/'
	FIND_STR = [
		'network-on-chip',
		'network on chip',
		'on-chip-network',
		'on chip network',
		'NOC',
		'OCN',
	]

	infoPath = os.path.join(folderPath, 'paperInfo.xml')
	with open(infoPath, 'r') as f:
		paperInfo = f.read()
		f.close()
	xml = etree.fromstring(paperInfo)
	hits = xml.xpath('//hit')
	for hit in hits:
		if (hit.find('./info/pages')) is None:
			continue

		title = hit.xpath('./info/title')[0].text
		# title = title.lower()
		for str in FIND_STR:
			if title.find(str) >= 0:
				pdfPath = os.path.join(folderPath, tools.toFilename(title))
				#如果pdf文档存在
				if os.path.exists(pdfPath):
					# print(os.path.abspath(pdfPath))

					#输出路径
					outputPath = pdfPath.replace(projectInfo.folderPath, outputFolder)
					# print(os.path.abspath(outputPath))

					with open(pdfPath, 'rb') as f:
						pdf = f.read()
						f.close()

					tools.write(pdf, outputPath, mode='wb')
				break

if __name__ == '__main__':
	import projectInfo
	import tools

	for conference in projectInfo.conferences:
		foldersPath = tools.getFolders(projectInfo.folderPath, conference)
		for folderPath in foldersPath:
			find_NOC_OCN(folderPath)