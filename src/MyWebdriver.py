from selenium.webdriver.support.ui import WebDriverWait
import tools

class MyWebdriver:
	def __init__(self, browserConstructor=tools.getChrome):
		self.browserConstructor = browserConstructor
		self.browser = self.browserConstructor()
		self.state = 1

	def get(self, url):
		if self.state == 0:
			self.restart()
		self.browser.get(url)

	def set_page_load_timeout(self, timeout):
		if self.state == 0:
			self.restart()
		self.browser.set_page_load_timeout(timeout)

	def quit(self):
		self.browser.quit()
		self.state = 0

	def current_url(self):
		return self.browser.current_url

	def title(self):
		return self.browser.title

	def WebDriverWait_until(self, timeout, lambdaFunc):
		return WebDriverWait(self.browser, timeout).until(lambdaFunc)

	def find_element_by_xpath(self, xpath):
		return self.browser.find_element_by_xpath(xpath)

	def find_elements_by_xpath(self, xpath):
		return self.browser.find_elements_by_xpath(xpath)

	def restart(self):
		if self.state == 1:
			self.quit()
		self.browser = self.browserConstructor()
		self.state = 1

if __name__ == '__main__':

	chrome = MyWebdriver(tools.getChrome)
	chrome.get('http://www.baidu.com')
	print(chrome.title())
	print(chrome.browser)
	import time
	time.sleep(3)
	chrome.restart()
	print(chrome.browser)
	print(chrome.title())
