from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import *
from PyKDE4 import plasmascript
from PyKDE4 import kdecore
import os
PLASMOID_WIDTH=380
PLASMOID_HEIGHT=480
URL='http://3g.163.com/t/'
HELPER_NAMES=["NeteaseMicroBlogHelper"]
HELPERS=[]
for helper in HELPER_NAMES:
	exec "from helpers import " + helper
	exec "HELPERS.append(" + helper + ".Helper())"
	print "Loaded", helper

class MiniWebPage(QWebPage):
	def __init__(self, parent):
		QWebPage.__init__(self, parent)
		self.cookieJar = QNetworkCookieJar()
		self.networkAccessManager().setCookieJar(self.cookieJar)
	def userAgentForUrl(self, url):
		return QString("Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.05 Mobile/8A293 Safari/6531.22.7")
	def acceptNavigationRequest(self, frame, request, type):
		# use helper to translate URL
		for helper in HELPERS:
			request.setUrl(helper.translateUrl(request.url()))
		if type == QWebPage.NavigationTypeLinkClicked and frame == None:
			# open in new window
			os.system("xdg-open " + request.url().toEncoded().data())
			return False
		return QWebPage.acceptNavigationRequest(self, frame, request, type)

class MiniWebApplet(plasmascript.Applet):
	def __init__(self,parent,args=None):
		plasmascript.Applet.__init__(self,parent)
	def saveCookies(self):
		allCookieString = ""
		for cookie in self.page.cookieJar.allCookies():
			allCookieString += cookie.toRawForm() + "\r\n"
		self.applet.config().writeEntry(QString("cookies"), QString(allCookieString))
	def loadCookies(self):
		allCookieString = self.applet.config().readEntry(QString("cookies"))
		if allCookieString == None:
			return
		allCookieString = allCookieString.toUtf8().data()
		cookies = QNetworkCookie.parseCookies(allCookieString)
		self.page.cookieJar.setAllCookies(cookies)
	def refreshPage(self):
		url = self.page.triggerAction(QWebPage.Reload)
		print "page reloaded"
	def init(self):
		self.resize(PLASMOID_WIDTH, PLASMOID_HEIGHT)
		self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
		self.setHasConfigurationInterface(True)
		# We need a layout
		self.layout = QGraphicsLinearLayout(self.applet)
		self.setLayout(self.layout)
		# A web browser
		self.web = Plasma.WebView()
		# use a customized WebPage class that sends customized user agent
		self.page = MiniWebPage(self)
		self.web.setPage(self.page)
		self.web.setUrl(kdecore.KUrl(URL))
		# add it to current layout
		self.layout.addItem(self.web)
		# save cookies when page finishes loading
		self.connect(self.page, SIGNAL("loadFinished(bool)"), self.saveCookies)
		# load saved cookies
		self.loadCookies()
		# use a timer for automatic refresh
		self.refreshTimer = QTimer(self)
		self.refreshTimer.setInterval(6000)
		self.refreshTimer.setSingleShot(True)
		self.connect(self.refreshTimer, SIGNAL("timeout()"), self.refreshPage)
#		self.connect(self.page, SIGNAL("loadStarted()"), self.refreshTimer.stop)
#		self.connect(self.page, SIGNAL("loadFinished(bool)"), self.refreshTimer.start)

def CreateApplet(parent):
	return MiniWebApplet(parent)
