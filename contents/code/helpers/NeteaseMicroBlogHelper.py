import string
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
class Helper():
	def translateUrl(self, originalUrl):
		urlString = originalUrl.toEncoded().data()
		if string.find(urlString, "http://3g.163.com/t/urlcheck") == 0:
			if originalUrl.hasQueryItem(QString("p")):
				translated = QUrl(originalUrl.queryItemValue(QString("p")))
				print "NeteaseMicroBlogHelper translated shorturl:", originalUrl.toString(), "to", translated
				return translated
		if string.find(urlString, "http://3g.163.com/post/pic_xhtml.jsp") == 0:
			if originalUrl.hasQueryItem(QString("picurl")):
				translated = QUrl(originalUrl.queryItemValue(QString("picurl")))
				if translated.hasQueryItem(QString("url")):
					translated = QUrl(translated.queryItemValue(QString("url")))
				print "NeteaseMicroBlogHelper translated picture url:", originalUrl.toString(), "to", translated
				return translated
		return originalUrl
	def needNewWindow(self, originalUrl):
		urlString = originalUrl.toEncoded().data()
		if string.find(urlString, "http://3g.163.com/t/urlcheck") == 0:
			return True
		if string.find(urlString, "http://3g.163.com/post/pic_xhtml.jsp") == 0:
			return True
		return False
