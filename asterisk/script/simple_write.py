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

import xmlrpclib
import sys

sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (sys.argv[3],sys.argv[4]))

ids = sock.execute(sys.argv[5], 3, 'admin', 'asterisk.phone', 'search', [('phoneid','=',sys.argv[1])])
sock.execute(sys.argv[5], 3, 'admin', 'asterisk.phone', 'write', ids, {'current_callerid': sys.argv[2]})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

