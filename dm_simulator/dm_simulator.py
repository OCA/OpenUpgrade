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

from osv import fields
from osv import osv

class dm_sim_scenario(osv.osv):
    _name = "dm.sim.scenario"
    _columns = {
        'name' : fields.char('Name',size=64,required=True),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
        'date_start' : fields.datetime('Date Start'),
        'date_stop' : fields.datetime('Date Stop'),
        'action_qty' : fields.integer('Action Quantity'),
    }

    def simulation_start(self, cr, uid, ids, *args):
        return True
      
dm_sim_scenario()
