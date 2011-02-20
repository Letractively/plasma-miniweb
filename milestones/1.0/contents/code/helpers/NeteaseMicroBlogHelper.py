# -*- coding: utf-8 -*-
#
# NeteaseMicroBlogHelper.py - the site helper for NetEase's micro blogging service
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

import string
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
import BaseHelper
class Helper(BaseHelper.Helper):
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
