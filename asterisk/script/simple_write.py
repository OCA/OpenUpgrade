# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import xmlrpclib
import sys

sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (sys.argv[3],sys.argv[4]))

ids = sock.execute(sys.argv[5], 3, 'admin', 'asterisk.phone', 'search', [('phoneid','=',sys.argv[1])])
sock.execute(sys.argv[5], 3, 'admin', 'asterisk.phone', 'write', ids, {'current_callerid': sys.argv[2]})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

