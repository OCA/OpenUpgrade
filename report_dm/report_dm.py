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

from osv import fields,osv

class report_sale_per_month(osv.osv):
    _name = "report.sale.per.month"
    _description = "Sales per Month"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_per_month as (
                select min(so.id) as id , 
                    to_char(so.date_order, 'YYYY-MM-dd') as name,
                    s.id as offer_step_id, 
                    o.id as offer_id,
                    cmp.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity 
                from sale_order so 
                    left join dm_campaign_proposition_segment seg on (so.segment_id = seg.id) 
                    left join dm_campaign_proposition pro on (pro.id = seg.proposition_id) 
                    left join dm_campaign cmp on (cmp.id = pro.camp_id) 
                    left join dm_offer o on (cmp.offer_id = o.id) 
                    left join dm_offer_step s on (s.offer_id = o.id and so.offer_step_id = s.id) 
                    group by to_char(so.date_order, 'YYYY-MM-dd') ,cmp.id , o.id , s.id;
            )
        """)
report_sale_per_month()

class report_sale_per_day(osv.osv):
    _name = "report.sale.per.day"
    _description = "Sales per day"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_per_day as (
                select min(so.id) as id , 
                    to_char(so.date_order, 'YYYY-MM-01') as name,
                    s.id as offer_step_id, 
                    o.id as offer_id,
                    cmp.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity 
                from sale_order so 
                    left join dm_campaign_proposition_segment seg on (so.segment_id = seg.id) 
                    left join dm_campaign_proposition pro on (pro.id = seg.proposition_id) 
                    left join dm_campaign cmp on (cmp.id = pro.camp_id) 
                    left join dm_offer o on (cmp.offer_id = o.id) 
                    left join dm_offer_step s on (s.offer_id = o.id and so.offer_step_id = s.id) 
                    group by to_char(so.date_order, 'YYYY-MM-01') ,cmp.id , o.id , s.id;
             )
        """)
report_sale_per_day()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

