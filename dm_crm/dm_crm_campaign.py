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

class dm_campaign(osv.osv):
    _inherit = "dm.campaign"
    
    def create(self, cr, uid, vals, context={}):
        crm_obj = self.pool.get('crm.case.section')
        crm_id = crm_obj.search(cr, uid, [('code','ilike','DM')])[0]
        section_vals = {
                'name' : vals['name'],
                'parent_id' : crm_id,
        }
        crm_obj.create(cr,uid,section_vals)
        return super(dm_campaign,self).create(cr, uid, vals, context)
    
dm_campaign()

class dm_campaign_proposition(osv.osv):
    _inherit = "dm.campaign.proposition"
    
    def create(self, cr, uid, vals, context={}):
        crm_obj = self.pool.get('crm.case.section')
        camp_id = self.pool.get('dm.campaign').browse(cr,uid,[vals['camp_id']])[0]
        crm_id = crm_obj.search(cr, uid, [('name','=',camp_id.name)])[0]
        section_vals = {
                'name' : vals['name'],
                'parent_id' : crm_id,
        }
        crm_obj.create(cr,uid,section_vals)
        return super(dm_campaign_proposition,self).create(cr, uid, vals, context)
    
dm_campaign_proposition()