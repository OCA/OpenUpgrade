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

import time
from osv import fields
from osv import osv

class dm_campaign_group(osv.osv):#{{{
    _name = "dm.campaign.group"
    
    def _quantity_planned_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_planned_total.isdigit():
                    quantity += int(campaign.quantity_planned_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_wanted_total.isdigit():
                    quantity += int(campaign.quantity_wanted_total)
                elif campaign.quantity_wanted_total == "AAA for a Segment":
                    result[group.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_delivered_total.isdigit():
                    quantity += int(campaign.quantity_delivered_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_usable_total(self, cr, uid, ids, name, args, context={}):
        result={}
        quantity=0
        numeric=True
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_usable_total.isdigit():
                    quantity += int(campaign.quantity_usable_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _camp_group_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        offer_code = ''
        offer_name = ''
        for id in ids:

            dt = time.strftime('%Y-%m-%d')
            date = dt.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=year+month
            grp = self.browse(cr,uid,id)
            for c in grp.campaign_ids:
                if c.offer_id:
                    d = self.pool.get('dm.offer').browse(cr, uid, c.offer_id.id)
                    offer_code = d.code
                    offer_name = d.name
            code1='-'.join([final_date,offer_code, offer_name])
            result[id]=code1
        return result

    _columns = {
        'name': fields.char('Campaign group name', size=64, required=True),
        'code' : fields.function(_camp_group_code,string='Code',type='char',method=True,readonly=True),
        'campaign_ids': fields.one2many('dm.campaign', 'campaign_group_id', 'Campaigns', domain=[('campaign_group_id','=',False)], readonly=True),
#        'quantity_planned_total' : fields.function(_quantity_planned_total, string='Total planned Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_usable_total' : fields.function(_quantity_usable_total, string='Total Usable Quantity',type="char",size=64,method=True,readonly=True),
    }
dm_campaign_group()#}}}

class dm_campaign(osv.osv):#{{{
    _inherit = "dm.campaign"
    _columns = {
        'campaign_group_id' : fields.many2one('dm.campaign.group', 'Campaign group'),
    }
dm_campaign()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: