###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following 
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be 
#     kept as in original distribution without any changes in all software 
#     screens, especially in start-up page and the software header, even if 
#     the application source code has been changed or updated or code has been 
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
# 
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

import socket
import cPickle
import marshal

DNS_CACHE = {}

class Myexception(Exception):
	def __init__(self, faultCode, faultString):
		self.faultCode = faultCode
		self.faultString = faultString
		self.args = (faultCode, faultString)

class mysocket:
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
		size = len(msg)
		self.sock.send('%8d' % size)
		self.sock.send(exception and "1" or "0")
		totalsent = 0
		while totalsent < size:
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError, "socket connection broken"
			totalsent = totalsent + sent
	def myreceive(self):
		buf=''
		while len(buf) < 8:
			chunk = self.sock.recv(8 - len(buf))
			if chunk == '':
				raise RuntimeError, "socket connection broken"
			buf += chunk
		size = int(buf)
		buf = self.sock.recv(1)
		if buf != "0":
			exception = buf
		else:
			exception = False
		msg = ''
		while len(msg) < size:
			chunk = self.sock.recv(size-len(msg))
			if chunk == '':
				raise RuntimeError, "socket connection broken"
			msg = msg + chunk
		res = cPickle.loads(msg)
		if isinstance(res[0],Exception):
			if exception:
				raise Myexception(str(res[0]), str(res[1]))
			raise res[0]
		else:
			return res[0]
		
# vim: ts=4 sts=4 sw=4 si et

