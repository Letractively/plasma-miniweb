import string
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
class Helper():
	def translateUrl(self, originalUrl):
		if string.find(originalUrl.toEncoded().data(), "http://3g.163.com/t/urlcheck") == 0:
			if originalUrl.hasQueryItem(QString("p")):
				translated = QUrl(originalUrl.queryItemValue(QString("p")))
				print "NeteaseMicroBlogHelper translated:", originalUrl.toString(), "to", translated
				return translated
		return originalUrl
