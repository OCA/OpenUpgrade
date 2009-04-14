# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import socket
import tiny_socket


class gw_inter(object):
    __slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
    def __init__(self, url, db, uid, passwd, obj='/object'):
        self._url = url
        self._db = db
        self._uid = uid
        self._obj = obj
        self._passwd = passwd
    def exec_auth(method, *args):
        pass
    def execute(method, *args):
        pass

class tiny_sock(gw_inter):
    __slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
    def __init__(self, url, db, uid, passwd, obj='/object'):
        gw_inter.__init__(self, url, db, uid, passwd, obj)
        self._sock = tiny_socket.mysocket()
        self._obj = obj[1:]
    def exec_auth(self, method, *args):
        res = self.execute(method, self._uid, self._passwd, *args)
        return res
    def execute(self, method, *args):
        self._sock.connect(self._url)
        self._sock.mysend((self._obj, method, self._db)+args)
        res = self._sock.myreceive()
        self._sock.disconnect()
        return res


