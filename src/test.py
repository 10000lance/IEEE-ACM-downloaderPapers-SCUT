import os
print(os.path.abspath('.'))
from urllib.parse import urlencode
import tools
import time
from MyWebdriver import MyWebdriver

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
}
url = 'https://dl.acm.org/citation.cfm?doid=3092627.3092632'
# response = tools.requestsGet(url, headers=headers)
# print(response.status_code)
data = {
    'query': 'lance',
    'lance1': '无'
}

import os
# os.makedirs('./lance')
import string
print(int('2018/'))