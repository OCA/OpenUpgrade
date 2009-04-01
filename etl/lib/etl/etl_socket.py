# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
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
"""
        Class of ETL socket.
"""
import socket
import cPickle
import marshal

class etl_socket_exception(Exception):
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString
        self.args = (faultCode, faultString)

DNS_CACHE = {}
class etl_socket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(120)

    def connect(self, host, port=False):
        if not port:
            protocol, buf = host.split('//')
            host, port = buf.split(':')
        if host in DNS_CACHE:
            host = DNS_CACHE[host]        
        self.sock.connect((host, int(port)))
        DNS_CACHE[host], port = self.sock.getpeername()

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def mysend(self, msg, exception=False, traceback=None):
        msg = cPickle.dumps([msg,traceback])
        self.sock.sendall('%8d%s%s' % (len(msg), exception and "1" or "0", msg))

    def myreceive(self):
        def read(socket, size):
            buf=''
            while len(buf) < size:
                chunk = self.sock.recv(size - len(buf))
                if chunk == '':
                    raise RuntimeError, "socket connection broken"
                buf += chunk
            return buf

        size = int(read(self.sock, 8))
        buf = read(self.sock, 1)
        exception = buf != '0' and buf or False
        res = cPickle.loads(read(self.sock, size))

        if isinstance(res[0],Exception):
            if exception:
                raise etl_socket_exception(str(res[0]), str(res[1]))
            raise res[0]
        else:
            return res[0]

