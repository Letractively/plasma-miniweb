# -*- coding: utf-8 -*-
#
# main.py - the main file of the Miniweb plasma
# Copyright © 2011 Kun Zhang <arthur.kun@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Authors:
# Kun Zhang <arthur.kun@gmail.com>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import *
from PyKDE4 import plasmascript
from PyKDE4 import kdecore
import lxml.html
import os
import traceback
PLASMOID_WIDTH=380
PLASMOID_HEIGHT=480
UPPER_BAR_HEIGHT=24

DEFAULT_HOME_PAGE='http://3g.163.com/t/'
DEFAULT_USER_AGENT='Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.05 Mobile/8A293 Safari/6531.22.7'

HELPER_NAMES=["BaseHelper", "NeteaseMicroBlogHelper"]
HELPERS={}
for helper in HELPER_NAMES:
	exec "from helpers import " + helper
	exec "HELPERS[\"" + helper + "\"]=" + helper +".Helper()"
	print "Loaded", helper

DEFAULT_HELPER="NeteaseMicroBlogHelper"

DEFAULT_SHOW_TITLE="True"

class MiniWebPage(QWebPage):
	''' A customized QWebPage to be used by the WebView widget'''
	def __init__(self, applet):
		QWebPage.__init__(self, applet)
		self.cookieJar = QNetworkCookieJar()
		self.networkAccessManager().setCookieJar(self.cookieJar)
		self.hoveredLink = None
		self.applet = applet
	def userAgentForUrl(self, url):
		return self.applet.getConfigQString("useragent", DEFAULT_USER_AGENT)
	def acceptNavigationRequest(self, frame, request, type):
		needNewWindow = HELPERS[self.applet.getConfigString("helper", DEFAULT_HELPER)].needNewWindow(request.url())
		# use helper to translate URL
		request.setUrl(HELPERS[self.applet.getConfigString("helper", DEFAULT_HELPER)].translateUrl(request.url()))
		if type == QWebPage.NavigationTypeLinkClicked and (frame == None or needNewWindow):
			# open in new window
			os.system("xdg-open " + request.url().toEncoded().data())
			return False
		return QWebPage.acceptNavigationRequest(self, frame, request, type)
	def createWindow(self, type):
		# the "Open in new window" in the context-menu only goes here
		# instead of acceptNavigationRequest.
		# Because no one actualy create the window, I have to create it myself using the hoveredLink
		if self.hoveredLink != None:
			url = QUrl(self.hoveredLink)
			url = HELPERS[self.applet.getConfigString("helper", DEFAULT_HELPER)].translateUrl(url)
			os.system("xdg-open " + url.toEncoded().data())
		return None

class GeneralConfigPage(QWidget):
	def __init__(self, parent, applet):
		QLabel.__init__(self, parent)
		self.applet = applet
		self.setupUi()
		self.loadConfig()
		self.connect(parent, SIGNAL("okClicked()"), self.saveConfig)
	def setupUi(self):
		layout = QGridLayout()
		# home page settings
		self.homePageBox = QLineEdit()
		self.homePageBox.setFixedWidth(300)
		layout.addWidget(QLabel(QString("Home page:")), 0, 0, Qt.AlignRight)
		layout.addWidget(self.homePageBox, 0, 1, Qt.AlignLeft)
		# user agent
		self.userAgentBox = QTextEdit()
		self.userAgentBox.setFixedSize(QSize(500, 100))
		layout.addWidget(QLabel(QString("User agent:")), 1, 0, Qt.AlignRight)
		layout.addWidget(self.userAgentBox, 1, 1, Qt.AlignLeft)
		# helpers
		self.helperBox = QComboBox()
		for helper in HELPER_NAMES:
			self.helperBox.addItem(QString(helper))
		layout.addWidget(QLabel(QString("Site helper:")), 2, 0, Qt.AlignRight)
		layout.addWidget(self.helperBox, 2, 1, Qt.AlignLeft)
		# options
		self.showTitleOption = QCheckBox()
		layout.addWidget(QLabel(QString("Show the title bar")), 3, 0, Qt.AlignRight)
		layout.addWidget(self.showTitleOption, 3, 1, Qt.AlignLeft)
		self.setLayout(layout)
		self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
	def loadConfig(self):
		self.homePageBox.setText(self.applet.getConfigQString("homepage", DEFAULT_HOME_PAGE))
		self.userAgentBox.setText(self.applet.getConfigQString("useragent", DEFAULT_USER_AGENT))
		self.helperBox.setCurrentIndex(HELPER_NAMES.index(self.applet.getConfigQString("helper", DEFAULT_HELPER)))
		if self.applet.getConfigString("showtitle", "True") == "True":
			self.showTitleOption.setCheckState(Qt.Checked)
		else:
			self.showTitleOption.setCheckState(Qt.Unchecked)
	def saveConfig(self):
		self.applet.applet.config().writeEntry(QString("homepage"), self.homePageBox.text())
		self.applet.applet.config().writeEntry(QString("helper"), QString(HELPER_NAMES[self.helperBox.currentIndex()]))
		if self.showTitleOption.checkState() == Qt.Checked:
			self.applet.applet.config().writeEntry(QString("showtitle"), QString("True"))
		else:
			self.applet.applet.config().writeEntry(QString("showtitle"), QString("False"))
		self.applet.initializeView()

class MiniWebApplet(plasmascript.Applet):
	def createConfigurationInterface(self, dlg):
		dlg.addPage(GeneralConfigPage(dlg, self), "General", "internet-web-browser")
	def getConfigQString(self, key, default):
		homepage = self.config().readEntry(QString(key))
		if homepage == None or homepage.trimmed().length() == 0:
			return QString(default)
		return homepage
	def getConfigString(self, key, default):
		return self.getConfigQString(key, default).toUtf8().data()
	def linkHovered(self, link, title, text):
		self.page.hoveredLink = link
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
		self.busyWidget.hide()
		doc = lxml.html.document_fromstring(self.web.html().toUtf8().data().decode("utf-8"))
		title = doc.find(".//title")
		if title != None:
			self.title.setText(QString(title.text))
	def loadStarted(self):
		self.busyWidget.show()
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
	def initializeView(self):
		if self.getConfigString("showtitle", "True") == "True":
			self.upperBar.setMaximumHeight(UPPER_BAR_HEIGHT)
		else:
			self.upperBar.setMaximumHeight(0)
		self.web.setUrl(kdecore.KUrl(self.getConfigString("homepage", DEFAULT_HOME_PAGE)))
	def init(self):
		self.resize(PLASMOID_WIDTH, PLASMOID_HEIGHT)
		self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
		self.setHasConfigurationInterface(True)
		# the main layout
		self.layout = QGraphicsLinearLayout(Qt.Vertical)
		self.setLayout(self.layout)
		# the upper sub-layout
		self.upperBar = QGraphicsWidget()
		upperLayout = QGraphicsLinearLayout(Qt.Horizontal)
		self.upperBar.setLayout(upperLayout)
		# A web browser
		self.web = Plasma.WebView()
		self.web.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		# A title label
		self.title = Plasma.Label()
		self.title.setPreferredHeight(UPPER_BAR_HEIGHT)
		self.title.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
		upperLayout.addItem(self.title)
		# A loading icon
		self.busyWidget = Plasma.BusyWidget()
		self.busyWidget.setPreferredSize(QSizeF(UPPER_BAR_HEIGHT, UPPER_BAR_HEIGHT))
		self.busyWidget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		upperLayout.addItem(self.busyWidget)
		# use a customized WebPage class that sends customized user agent
		self.page = MiniWebPage(self)
		self.web.setPage(self.page)
		# add it to current layout
		self.layout.addItem(self.upperBar)
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
		# keep track of the currently hovered link
		self.connect(self.page, SIGNAL("linkHovered(QString,QString,QString)"), self.linkHovered)

		self.initializeView()
#		self.connect(self.page, SIGNAL("loadStarted()"), self.refreshTimer.stop)
#		self.connect(self.page, SIGNAL("loadFinished(bool)"), self.refreshTimer.start)

def CreateApplet(parent):
	return MiniWebApplet(parent)
