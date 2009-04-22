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

from mx.DateTime import now
from osv import osv
import wizard
import netsvc
import ir
import pooler
import tools
from tools.translate import _

class maintenance_maintenance_module_refresh_wizard(wizard.interface):
    def init(self, cr, uid, data, context):
        pooler.get_pool(cr.dbname).get('maintenance.maintenance.module').refresh(cr, uid)
        raise osv.except_osv(_('Refresh'), _('List refreshed successfully'))
        return {}

    states = {
        'init': {
            'actions': [init],
            'result': {'type': 'state', 'state': 'end'}
        }
    }
maintenance_maintenance_module_refresh_wizard("maintenance.maintenance.module.refresh")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

