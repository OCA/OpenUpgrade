# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

from osv import osv, fields
import pooler
import time
import math

from tools import config
import xmlrpclib

class maintenance_contract(osv.osv):
    _name = "maintenance.contract"
    _description = "Maintenance Contract"
    _columns = {
    'name' : fields.char('Name', size=256),
    'contract_date' : fields.date('Date'),
    'password' : fields.char('password', size=64, invisible=True),
        }

    _defaults = {
        'password' : lambda obj,cr,uid,context={} : '',
        'contract_date':lambda *a: time.strftime('%Y-%m-%d'),
              }
    def _test_maintenance(self, cr, uid, ids, context):
        remote_db='trunk'
        remote_server='localhost'
        port=8069
        module_obj=self.pool.get('ir.module.module')
        contract_obj=self.pool.get('maintenance.contract')
        module_ids=module_obj.search(cr, uid, [('state','=','installed')])
        modules=module_obj.read(cr, uid, module_ids, ['name','installed_version'])
        contract_obj=contract_obj.read(cr, uid, ids[0])
        local_url = 'http://%s:%d/xmlrpc/common'%(remote_server,port)
        rpc = xmlrpclib.ServerProxy(local_url)
        ruid = rpc.login(remote_db, 'admin', 'admin')
        local_url = 'http://%s:%d/xmlrpc/object'%(remote_server,port)
        rrpc = xmlrpclib.ServerProxy(local_url)
        result=rrpc.execute(remote_db, ruid, 'admin', 'maintenance.maintenance', 'check_contract' , modules,contract_obj)
        if result['status']=='ko':
            raise Exception(_('''Maintenance Contract
-----------------------------------------------------------
You do not have a valid maintenance contract ! If you use
Open ERP, it's highly suggested to take a maintenance
contract. The maintenance program offers you: migrations on
new versions, bugfixes guarantee, monthly announces on bugs,
security alerts, access to the customer portal.
* Check the maintenance contract (www.openerp.com)'''))
        elif result['status']=='partial':
            raise Exception(_('''Maintenance Contract
-----------------------------------------------------------
You have a maintenance contract but you installed modules that
are not covered by your maintenance:
'''+','.join(result['modules'])+'''
It means we can not offer you the garantee of the maintenance on
your whole installation. The maintenance program includes:
automatic migrations on new versions, bugfixes guarantee, monthly
announces on bugs, security alerts, access to the customer portal.

To include these modules in your maintenance contract, you should
extend your contract with the editor. We will review and validate
your installed modules.

* Extend the maintenance to the modules I use
* Check the maintenance contract'''))
        return {}
maintenance_contract()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

