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


import wizard
import netsvc
import time
import pooler
from osv import osv

class wiz_launch_phase1(wizard.interface):

    def _launch_phase1(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        mod_obj = pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'profile_business_game', 'phase1')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']

        value = {
            'name': 'Business Game',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'profile.game.phase1',
            'view_id': False,
            'res_id' : id,
            'type': 'ir.actions.act_window'
        }
        return value

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type':'action', 'action':_launch_phase1, 'state':'end'}
        }
    }
wiz_launch_phase1('profile_game.open.phase1')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

