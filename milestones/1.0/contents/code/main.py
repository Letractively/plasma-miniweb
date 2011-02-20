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
import time

# UI metrics
PLASMOID_WIDTH=380
PLASMOID_HEIGHT=480
UPPER_BAR_HEIGHT=24

# Default settings
DEFAULT_HOME_PAGE='http://news.google.com/'
DEFAULT_CUSTOMIZE_USER_AGENT="True"
#iPhone:
#DEFAULT_USER_AGENT='Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.05 Mobile/8A293 Safari/6531.22.7'
#Nokia E51:
DEFAULT_USER_AGENT='Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaE51-1/220.34.37; Profile/MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413'

DEFAULT_RELOAD_INTERVAL=60
DEFAULT_AUTO_RELOAD='False'
DEFAULT_DISABLE_RELOAD_WHEN_FOCUSED='True'
DEFAULT_HELPER="BaseHelper"
DEFAULT_SHOW_TITLE="True"

# Initialize site helpers
HELPER_NAMES=["BaseHelper", "NeteaseMicroBlogHelper"]
HELPERS={}
for helper in HELPER_NAMES:
	exec "from helpers import " + helper
	exec "HELPERS[\"" + helper + "\"]=" + helper +".Helper()"
	print "Loaded", helper


class MiniWebPage(QWebPage):
	''' A customized QWebPage to be used by the WebView widget'''
	def __init__(self, applet):
		QWebPage.__init__(self, applet)
		self.cookieJar = QNetworkCookieJar()
		self.networkAccessManager().setCookieJar(self.cookieJar)
		self.hoveredLink = None
		self.applet = applet
	def userAgentForUrl(self, url):
		if self.applet.getConfigString("customizeuseragent", DEFAULT_CUSTOMIZE_USER_AGENT) == "True":
			return self.applet.getConfigQString("useragent", DEFAULT_USER_AGENT)
		else:
			return QWebPage.userAgentForUrl(self, url)
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
			os.system("xdg-open '" + url.toEncoded().data() + "'")
		return None
class GeneralConfigPage(QWidget):
	def __init__(self, parent, applet):
		QLabel.__init__(self, parent)
		self.applet = applet
		self.setupUi()
		self.loadConfig()
		self.connect(parent, SIGNAL("okClicked()"), self.saveConfig)
	def updateReloadSectionUi(self):
		if self.autoReloadOption.checkState() == Qt.Checked:
			enabled = True
		else:
			enabled = False
		self.disableReloadWhenFocusedLabel.setEnabled(enabled)
		self.reloadIntervalLabel.setEnabled(enabled)
		self.disableReloadWhenFocusedOption.setEnabled(enabled)
		self.reloadInterval.setEnabled(enabled)
	def updateUserAgentSectionUi(self):
		if self.customizeUserAgentOption.checkState() == Qt.Checked:
			enabled = True
		else:
			enabled = False
		self.userAgentBox.setEnabled(enabled)
		self.userAgentLabel.setEnabled(enabled)
	def setupUi(self):
		layout = QGridLayout()
		row = 0
		# home page settings
		self.homePageBox = QLineEdit()
		self.homePageBox.setFixedWidth(300)
		layout.addWidget(QLabel(QString("Home page:")), row, 0, Qt.AlignRight)
		layout.addWidget(self.homePageBox, row, 1, Qt.AlignLeft)
		# user agent
		row = row + 1
		self.customizeUserAgentOption = QCheckBox()
		layout.addWidget(QLabel(QString("Use custom user agent")), row, 0, Qt.AlignRight)
		layout.addWidget(self.customizeUserAgentOption, row, 1, Qt.AlignLeft)
		row = row + 1
		self.userAgentBox = QTextEdit()
		self.userAgentBox.setFixedSize(QSize(300, 100))
		self.userAgentLabel = QLabel(QString("Custom user agent:"))
		layout.addWidget(self.userAgentLabel, row, 0, Qt.AlignRight)
		layout.addWidget(self.userAgentBox, row, 1, Qt.AlignLeft)
		self.connect(self.customizeUserAgentOption, SIGNAL("stateChanged(int)"), self.updateUserAgentSectionUi)
		# helpers
		row = row + 1
		self.helperBox = QComboBox()
		for helper in HELPER_NAMES:
			self.helperBox.addItem(QString(helper))
		layout.addWidget(QLabel(QString("Site helper:")), row, 0, Qt.AlignRight)
		layout.addWidget(self.helperBox, row, 1, Qt.AlignLeft)
		# automatic reloading
		row = row + 1
		self.autoReloadOption = QCheckBox()
		layout.addWidget(QLabel(QString("Automatic refresh")), row, 0, Qt.AlignRight)
		layout.addWidget(self.autoReloadOption, row, 1, Qt.AlignLeft)
		self.connect(self.autoReloadOption, SIGNAL("stateChanged(int)"), self.updateReloadSectionUi)
		row = row + 1
		self.disableReloadWhenFocusedOption = QCheckBox()
		self.disableReloadWhenFocusedLabel = QLabel(QString("Pause auto-refresh when<br>mouse hoverring or content changed"))
		self.disableReloadWhenFocusedLabel.setAlignment(Qt.AlignRight)
		layout.addWidget(self.disableReloadWhenFocusedLabel, row, 0, Qt.AlignRight)
		layout.addWidget(self.disableReloadWhenFocusedOption, row, 1, Qt.AlignLeft)
		row = row + 1
		self.reloadInterval = QTimeEdit()
		self.reloadInterval.setDisplayFormat(QString("hh:mm:ss"))
		self.reloadIntervalLabel = QLabel(QString("Refresh interval"))
		layout.addWidget(self.reloadIntervalLabel, row, 0, Qt.AlignRight)
		layout.addWidget(self.reloadInterval, row, 1, Qt.AlignLeft)

		# options
		row = row + 1
		self.showTitleOption = QCheckBox()
		layout.addWidget(QLabel(QString("Show the title bar")), row, 0, Qt.AlignRight)
		layout.addWidget(self.showTitleOption, row, 1, Qt.AlignLeft)
		self.setLayout(layout)
		self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))

		self.checkBoxes = [{"key":"customizeuseragent", "default":DEFAULT_CUSTOMIZE_USER_AGENT, "widget":self.customizeUserAgentOption},
				{"key":"showtitle", "default":DEFAULT_SHOW_TITLE, "widget":self.showTitleOption},
				{"key":"autoreload", "default":DEFAULT_AUTO_RELOAD, "widget":self.autoReloadOption},
				{"key":"disablereloadwhenfocused", "default":DEFAULT_DISABLE_RELOAD_WHEN_FOCUSED, "widget":self.disableReloadWhenFocusedOption}]
	def loadConfig(self):
		''' Load saved configuration to the UI'''
		self.homePageBox.setText(self.applet.getConfigQString("homepage", DEFAULT_HOME_PAGE))
		self.userAgentBox.setText(self.applet.getConfigQString("useragent", DEFAULT_USER_AGENT))
		self.helperBox.setCurrentIndex(HELPER_NAMES.index(self.applet.getConfigQString("helper", DEFAULT_HELPER)))
		reloadIntervalTime = QTime().addSecs(self.applet.getConfigInt("reloadinterval", DEFAULT_RELOAD_INTERVAL))
		self.reloadInterval.setTime(reloadIntervalTime)
		for checkbox in self.checkBoxes:
			if self.applet.getConfigString(checkbox["key"], checkbox["default"]) == "True":
				checkbox["widget"].setCheckState(Qt.Checked)
			else:
				checkbox["widget"].setCheckState(Qt.Unchecked)
		self.updateReloadSectionUi()
		self.updateUserAgentSectionUi()
	def saveConfig(self):
		''' Save updated configuration from UI '''
		self.applet.config().writeEntry(QString("homepage"), self.homePageBox.text())
		self.applet.config().writeEntry(QString("useragent"), self.userAgentBox.toPlainText())
		self.applet.config().writeEntry(QString("helper"), QString(HELPER_NAMES[self.helperBox.currentIndex()]))
		self.applet.config().writeEntry(QString("reloadinterval"), str(QTime().secsTo(self.reloadInterval.time())))
		for checkbox in self.checkBoxes:
			if checkbox["widget"].checkState() == Qt.Checked:
				self.applet.config().writeEntry(QString(checkbox["key"]), QString("True"))
			else:
				self.applet.config().writeEntry(QString(checkbox["key"]), QString("False"))
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
	def getConfigInt(self, key, default):
		return int(self.getConfigString(key, str(default)))
	def linkHovered(self, link, title, text):
		self.page.hoveredLink = link
	def __init__(self,parent,args=None):
		plasmascript.Applet.__init__(self,parent)
		self.nextAutoReloadTime = -1
	def resetAutoReloadTimer(self):
		self.nextAutoReloadTime = int(time.time()) + self.getConfigInt("reloadinterval", DEFAULT_RELOAD_INTERVAL)
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
		self.resetAutoReloadTimer()
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
	def checkAutoReloadPage(self):
		# I can't find a way to know whether the plasmoid has keyboard focus,
		# so I use this work-around
		if self.getConfigString("disablereloadwhenfocused", DEFAULT_DISABLE_RELOAD_WHEN_FOCUSED) == "True":
			if self.page.isModified():
				self.resetAutoReloadTimer()
				return
			if self.applet.isUnderMouse():
				self.resetAutoReloadTimer()
				return
		if self.nextAutoReloadTime < 0 or self.nextAutoReloadTime > time.time():
			return
		print "Automatic reloading page ..."
		# I do not use QWebPage.Reload, instead I set re-set the Url to
		# only refresh the page, and not to reload other resources such as images
		#url = self.page.triggerAction(QWebPage.Reload)
		self.web.setUrl(kdecore.KUrl(self.web.mainFrame().url()))
		# -1 means temporarily disable the timer
		# it will be resumed after load finished
		self.nextAutoReloadTime = -1
	def initializeView(self):
		if self.getConfigString("showtitle", DEFAULT_SHOW_TITLE) == "True":
			self.upperBar.setMaximumHeight(UPPER_BAR_HEIGHT)
		else:
			self.upperBar.setMaximumHeight(0)
		self.web.setUrl(kdecore.KUrl(self.getConfigString("homepage", DEFAULT_HOME_PAGE)))
		if self.getConfigString("autoreload", DEFAULT_AUTO_RELOAD) == "True":
			self.refreshTimer.start()
		else:
			self.refreshTimer.stop()
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
		self.refreshTimer.setInterval(1000)
		self.refreshTimer.setSingleShot(False)
		self.connect(self.refreshTimer, SIGNAL("timeout()"), self.checkAutoReloadPage)
		# keep track of the currently hovered link
		self.connect(self.page, SIGNAL("linkHovered(QString,QString,QString)"), self.linkHovered)

		self.initializeView()
		self.refreshTimer.start()

def CreateApplet(parent):
	return MiniWebApplet(parent)
