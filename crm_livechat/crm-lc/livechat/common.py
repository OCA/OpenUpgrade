# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

class TinyException(Exception):

    def __init__(self, message, title=None):

        self.title = title
        self.message = message

    def __str__(self):
        return self.message

class TinyError(TinyException):

    def __init__(self, message, title=_("Error")):
        TinyException.__init__(self, message=message, title=title)

class TinyWarning(TinyException):

    def __init__(self, message, title=_("Warning")):
        TinyException.__init__(self, message=message, title=title)

class TinyMessage(TinyException):

    def __init__(self, message, title=_("Information")):
        TinyException.__init__(self, message=message, title=title)

def error(title, msg, details=None):
    raise TinyError(message=msg, title=title or _("Error"))

def warning(msg, title=None):
    raise TinyWarning(message=msg, title=title or _("Warning"))

def message(msg):
    raise TinyMessage(message=msg)

def to_xml(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

