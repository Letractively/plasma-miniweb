# -*- coding: utf-8 -*-
#
# BaseHelper.py - the base class of site helpers for plasma-miniweb
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

class Helper():
	def translateUrl(self, originalUrl):
		return originalUrl
	def needNewWindow(self, originalUrl):
		return False
