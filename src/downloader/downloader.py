#导入上层文件夹的模块
import sys
sys.path.append('../')

import os
from lxml import etree
import time
import tools
import projectInfo
from . import ACM, IEEE, Schloss, Springer

def downloadPDF(pdfURL, pdfPath, logPath='', warningPath=''):
    """下载pdf

    :param pdfURL: pdf下载地址
    :param pdfPath: pdf存储地址
    :param logPath: log日志地址
    :param warningPath: warning日志地址
    :return: 存储pdf成功返回True，失败返回False
    """
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    }

    #pdfURL为空
    if pdfURL == '' or pdfURL == None:
        warningInfo = 'Failed to download the paper, for pdfURL is none'
        tools.warning(warningInfo, warningPath)
        return False

    #下载pdf
    pdf = tools.requestsGet(pdfURL, headers=headers, logPath=logPath, warningPath=warningPath)

    # 下载pdf失败
    if pdf == '':
        warningInfo = 'Failed to download the {0} from the page {1}'.format(pdfPath, pdfURL)
        tools.warning(warningInfo, warningPath)
        return False

    #下载成功
    logInfo = 'Successfully download {0}'.format(pdfPath)
    tools.log(logInfo, logPath)

    #写入成功则返回True，失败返回False
    return tools.write(pdf.content, pdfPath, mode='wb', logPath=logPath, warningPath=warningPath)

#获取论文基本信息（摘要，引用，被引用，pdf源地址）
def getPaperInfo(urls, title, MyWebdriver, logPath='', warningPath='', hasSearcher=False):
    newWebsiteLog = './newWebsite.txt'

    infos = {
        'ee': '',
        'pdfURL': '',
        'abstract': '',
        'references': [],
        'citedInPapers': [],
    }
    #检测是否经过搜索了
    if hasSearcher:
        infos['ee'] = urls
    else:
        del infos['ee']

    #若传入的urls不是一个列表
    if not isinstance(urls, list):
        [url, urls] = [urls, []]
        urls.append(url)
    #传入的urls为空列表
    elif len(urls) == 0:
        warningInfo = 'Can not get the abstract、references、citedInPapers、pdfURL of <{0}>, for the paper\'s urls is None'.format(title)
        tools.warning(warningInfo, warningPath)
        return infos

    #遍历urls
    for url in urls:
        if url == '':
            continue

        result = tools.webdriverGet(url, MyWebdriver, logPath=logPath, warningPath=warningPath)
        #打开页面失败
        if not result:
            continue

        #成功打开页面后获取页面跳转后真实的url
        time.sleep(2)
        try:
            current_url = MyWebdriver.current_url()
        except:
            time.sleep(5)
            try:
                current_url = MyWebdriver.current_url()
            #无法获取到ee的真实url地址
            except Exception as e:
                warningInfo = 'Can not get the real url of {0}\n            Failed info: {1}'.format(url, repr(e))
                tools.warning(warningInfo, warningPath)
                continue

        # print(current_url)
        # 根据url来分类
        # IEEE
        if current_url.find('https://ieeexplore.ieee.org/') == 0:
            infos.update(IEEE.getPaperInfo(MyWebdriver, logPath=logPath, warningPath=warningPath))
            return infos
        # ACM
        elif current_url.find('https://dl.acm.org/') == 0:
            infos.update(ACM.getPaperInfo(MyWebdriver, logPath=logPath, warningPath=warningPath))
            return infos
        # Springer
        elif current_url.find('https://link.springer.com/') == 0:
            infos.update(Springer.getPaperInfo(MyWebdriver, logPath=logPath, warningPath=warningPath))
            return infos
        # Schloss
        elif current_url.find('http://drops.dagstuhl.de/') == 0:
            infos.update(Schloss.getPaperInfo(MyWebdriver, logPath=logPath, warningPath=warningPath))
            return infos
        # EDA
        # elif (current_url.find('') >= 0) or (current_url.find('') >= 0):
        #     pass
        # Kluwer
        # elif current_url.find('') == 0:
        #     pass
        # Technische
        # elif current_url.find('') >= 0:
        #     pass
        else:
            continue

    #可能出现新的论文网站，记录下来
    print('New website: {0}'.format(urls))
    with open(newWebsiteLog, 'a', encoding='utf-8') as f:
        f.write('New website: {0}\n'.format(urls))
        f.close()

    #先在ACM中搜索、后在IEEE中搜索
    if not (title == '' or title == None):
        for search in [ACM.search, IEEE.search]:
            newURL = search(title, logPath=logPath, warningPath=warningPath)
            if newURL != '':
                return getPaperInfo(newURL, title, MyWebdriver, logPath=logPath, warningPath=warningPath, hasSearcher=True)

    #在ACM、IEEE中查找无结果后检测是否是CURE网站上的论文
    for url in urls:
        # CURE,直接是论文下载地址，无法直接获取abstract、references，需人工处理
        # 使用current_url获取到的url是‘data:’
        if (url.find('http://ceur-ws.org/') == 0) and (url.find('.pdf') >= 0):
            warningInfo = "Can not get abstract、references、citedInPapers from this website {0}".format(url)
            tools.warning(warningInfo, warningPath)
            infos['pdfURL'] = url
            logInfo = 'Successfully get pdfURL'
            tools.log(logInfo, logPath)
            return infos

    #上述操作都无效，只能都返回空值
    warningInfo = 'Failed to get pdfURL、abstract、references、citedInPapers, For can not find the paper'
    tools.warning(warningInfo, warningPath)
    return infos

def getPublishers(conferences):
    '''将各个年份按照出版分类

    :param conferences:
    :return:
    '''
    IEEE = []
    ACM = []
    IEEE_Computer_Society = []
    ACM_IEEE_Computer_Society = []
    Kluwer = []
    Technische = []
    EDA_or_European = []
    Springer = []
    Schloss = []
    CEUR = []
    num = 0
    for conference in conferences:
        foldersPath = tools.getFolders(projectInfo.folderPath, conference)
        for folderPath in foldersPath:
            num += 1
            infoPath = os.path.join(folderPath, 'paperInfo.xml')
            with open(infoPath, 'r') as f:
                paperInfo = f.read()
                f.close()
            xml = etree.fromstring(paperInfo)
            # 该年份论文的出版信息
            publisher = xml.xpath('/Year/attribute::publisher')[0]
            if publisher == 'IEEE':
                IEEE.append(folderPath)
            elif publisher == 'ACM' or publisher == 'ACM Press':
                ACM.append(folderPath)
            elif publisher == 'IEEE Computer Society':
                IEEE_Computer_Society.append(folderPath)
            elif publisher.find('IEEE Computer Society') >= 0 and publisher.find('ACM') >= 0:
                ACM_IEEE_Computer_Society.append(folderPath)
            elif publisher.find('Kluwer') >= 0:
                Kluwer.append(folderPath)
            elif publisher.find('Technische') >= 0:
                Technische.append(folderPath)
            elif (publisher.find('EDA') >= 0) or (publisher.find('European') >= 0):
                EDA_or_European.append(folderPath)
            elif publisher.find('Springer') >= 0:
                Springer.append(folderPath)
            elif publisher.find('Schloss') >= 0:
                Schloss.append(folderPath)
            elif publisher.find('CEUR') >= 0:
                CEUR.append(folderPath)
    print(num)
    with open('./publishers_sort.txt', 'w', encoding='utf-8') as f:
        f.writelines('IEEE:\n')
        for p in IEEE:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('ACM:\n')
        for p in ACM:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('IEEE Computer Society:\n')
        for p in IEEE_Computer_Society:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('IEEE Computer Society / ACM:\n')
        for p in ACM_IEEE_Computer_Society:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('Kluwer:\n')
        for p in Kluwer:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('Technische:\n')
        for p in Technische:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('EDA_or_European:\n')
        for p in EDA_or_European:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('Springer:\n')
        for p in Springer:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('Schloss:\n')
        for p in Schloss:
            f.writelines(p + '\n')
        f.write('\n\n')

        f.writelines('CEUR:\n')
        for p in CEUR:
            f.writelines(p + '\n')
        f.close()

if __name__ == '__main__':
    def test_downloadPDF():
        pdfURL = 'https://ieeexplore.ieee.org/ielx5/7307/19761/0091.pdf'
        downloadPDF(pdfURL, '1.pdf', logPath='TestLog.txt', warningPath='TestWarning.txt')

    def test_getPaperInfo():
        import json
        from MyWebdriver import MyWebdriver
        urls = 'https://doi.org/10.1109/DATE.2001.915001'
        title = ''
        myWebdriver = MyWebdriver()
        infos = getPaperInfo(urls, title, myWebdriver, logPath='TestLog.txt', warningPath='TestWarning.txt')
        print(json.dumps(infos, indent=4, separators=(',', ':')))

    test_getPaperInfo()