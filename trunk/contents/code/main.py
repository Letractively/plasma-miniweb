from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import *
from PyKDE4 import plasmascript
from PyKDE4 import kdecore
import lxml.html
import os
PLASMOID_WIDTH=380
PLASMOID_HEIGHT=480
UPPER_BAR_HEIGHT=24
URL='http://3g.163.com/t/'
HELPER_NAMES=["NeteaseMicroBlogHelper"]
HELPERS={}
ACTIVE_HELPER=None
for helper in HELPER_NAMES:
	exec "from helpers import " + helper
	exec "HELPERS[\"" + helper + "\"]=" + helper +".Helper()"
	print "Loaded", helper
ACTIVE_HELPER=HELPERS["NeteaseMicroBlogHelper"]

class MiniWebPage(QWebPage):
	def __init__(self, parent):
		QWebPage.__init__(self, parent)
		self.cookieJar = QNetworkCookieJar()
		self.networkAccessManager().setCookieJar(self.cookieJar)
	def userAgentForUrl(self, url):
		return QString("Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.05 Mobile/8A293 Safari/6531.22.7")
	def acceptNavigationRequest(self, frame, request, type):
		# use helper to translate URL
		needNewWindow = False
		if ACTIVE_HELPER != None:
			needNewWindow = ACTIVE_HELPER.needNewWindow(request.url())
			request.setUrl(ACTIVE_HELPER.translateUrl(request.url()))
		if type == QWebPage.NavigationTypeLinkClicked and (frame == None or needNewWindow):
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
	def loadFinished(self):
		self.saveCookies()
		self.busyWidget.setRunning(False)
		doc = lxml.html.document_fromstring(self.web.html().toUtf8().data().decode("utf-8"))
		title = doc.find(".//title")
		if title != None:
			self.title.setText(QString(title.text))
	def loadStarted(self):
		self.busyWidget.setRunning(True)
	def loadCookies(self):
		allCookieString = self.applet.config().readEntry(QString("cookies"))
		if allCookieString == None:
			return
		allCookieString = allCookieString.toUtf8().data()
		cookies = QNetworkCookie.parseCookies(allCookieString)
		self.page.cookieJar.setAllCookies(cookies)
	def refreshPage(self):
		url = self.page.triggerAction(QWebPage.Reload)
	def init(self):
		self.resize(PLASMOID_WIDTH, PLASMOID_HEIGHT)
		self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
		self.setHasConfigurationInterface(True)
		# the main layout
		self.layout = QGraphicsLinearLayout(Qt.Vertical)
		self.setLayout(self.layout)
		# the upper sub-layout
		self.upperLayout = QGraphicsLinearLayout(Qt.Horizontal)
		# A web browser
		self.web = Plasma.WebView()
		self.web.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		# A title label
		self.title = Plasma.Label()
		self.title.setPreferredHeight(UPPER_BAR_HEIGHT)
		self.title.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
		self.upperLayout.addItem(self.title)
		# A loading icon
		self.busyWidget = Plasma.BusyWidget()
		self.busyWidget.setPreferredSize(QSizeF(UPPER_BAR_HEIGHT, UPPER_BAR_HEIGHT))
		self.busyWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		self.upperLayout.addItem(self.busyWidget)
		# use a customized WebPage class that sends customized user agent
		self.page = MiniWebPage(self)
		self.web.setPage(self.page)
		self.web.setUrl(kdecore.KUrl(URL))
		# add it to current layout
		self.layout.addItem(self.upperLayout)
		self.layout.addItem(self.web)
		# save cookies when page finishes loading
		self.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
		self.connect(self.page, SIGNAL("loadStarted()"), self.loadStarted)
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
