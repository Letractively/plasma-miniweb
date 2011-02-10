from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyKDE4.plasma import *
from PyKDE4 import plasmascript
from PyKDE4 import kdecore
PLASMOID_WIDTH=380
PLASMOID_HEIGHT=480
URL='http://3g.163.com/t/#t'
class MiniWebPage(QWebPage):
	def __init__(self, parent):
		QWebPage.__init__(self, parent)
	def userAgentForUrl(self, url):
		return QString("Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.05 Mobile/8A293 Safari/6531.22.7")

class MiniWebApplet(plasmascript.Applet):
	def __init__(self,parent,args=None):
		plasmascript.Applet.__init__(self,parent)
	def init(self):
		self.resize(PLASMOID_WIDTH, PLASMOID_HEIGHT)
		self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
		self.setHasConfigurationInterface(True)
		# We need a layout
		self.layout = QGraphicsLinearLayout(self.applet)
		self.setLayout(self.layout)
		# A web browser
		self.web = Plasma.WebView()

		page = MiniWebPage(self)
		self.web.setPage(page)
		self.web.setUrl(kdecore.KUrl(URL))
		# add it to current layout
		self.layout.addItem(self.web)

		# use a timer for automatic refresh

def CreateApplet(parent):
	return MiniWebApplet(parent)
