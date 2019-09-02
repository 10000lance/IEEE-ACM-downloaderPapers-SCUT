import os
from lxml import etree

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

def countDownloadNum(folderPath):
    '''计算某会议某年份已下载的论文数量

    :param folderPath: 某会议某年份的文件夹路径
    :return: 某会议某年份已下载的论文数量
    '''
    num = 0
    infoPath = os.path.join(folderPath, 'paperInfo.xml')
    with open(infoPath, 'r') as f:
        paperInfo = f.read()
        f.close()
    xml = etree.fromstring(paperInfo)
    hits = xml.xpath('//hit')
    for hit in hits:
        hasDownload = hit.get('hasDownloadPDF')
        if hasDownload == 'True':
           num += 1
    # print('{0} has downloaded {1} papers'.format(folderPath, int(num)))
    return int(num)

if __name__ == '__main__':
    import projectInfo
    import tools

    paperNum = 0
    paperNumInTotal = 0
    paperDownloadNum = 0
    paperDownloadNumInTotal = 0
    for conference in projectInfo.conferences:
        paperNumInConf = 0
        paperDownloadNumInConf = 0
        foldersPath = tools.getFolders(projectInfo.folderPath, conference)
        for folderPath in foldersPath:
            paperNum = countPaperNum(folderPath)
            paperNumInConf += paperNum
            paperNumInTotal += paperNum
            paperDownloadNum = countDownloadNum(folderPath)
            paperDownloadNumInConf  += paperDownloadNum
            paperDownloadNumInTotal += paperDownloadNum
            # print('{0} has downloaded {1}/{2} papers'.format(folderPath, paperDownloadNum, paperNum))
        print('{0} has downloaded {1}/{2} papers'.format(conference, paperDownloadNumInConf, paperNumInConf))
    print('{0}/{1} papers has been downloaded totally'.format(paperDownloadNumInTotal, paperNumInTotal))
