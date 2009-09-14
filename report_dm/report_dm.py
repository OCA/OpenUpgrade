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
# Sales by Segment and Offer Step

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
                    to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text as name,
                    s.id as offer_step_id, 
                    o.id as offer_id,
                    cmp.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity 
                from sale_order so,dm_campaign_proposition_segment seg,
                    dm_campaign_proposition pro,dm_campaign cmp,
                    dm_offer o ,dm_offer_step s
                where
                    so.segment_id = seg.id and pro.id = seg.proposition_id 
                    and cmp.id = pro.camp_id and cmp.offer_id = o.id and
                    s.offer_id = o.id and so.offer_step_id = s.id
                group by to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text ,cmp.id , o.id , s.id
            )
        """)
report_sale_per_month()

# Sales by Offer Step
class report_sale_offer_step_per_month(osv.osv):
    _name = "report.sale.offer.step.per.month"
    _description = "Sales by Offer Step per Month"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        #'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_offer_step_per_month as (
           select
                min(so.id) as id,
                to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text as name,
        dos.id as offer_step_id,
                do1.id as offer_id,
                sum(so.amount_total) as sale_amount ,
                count(so.id) as sale_quantity
            from sale_order as so, dm_offer_step dos, dm_offer do1
            where 
                so.offer_step_id is not null and so.offer_step_id = dos.id and dos.offer_id = do1.id 
            group by do1.id,  to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text, dos.id

        )
        """)
report_sale_offer_step_per_month()

############Sales by Segment
class report_sale_segment_per_month(osv.osv):
    _name = "report.sale.segment.per.month"
    _description = "Sales by Segment per Month"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        #'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_segment_per_month as (
               select
                    min(so.id) as id,
                    to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text as name,
                    dcps.id as Segment,
                    do1.id as offer_id,
                    dc.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity
                from sale_order as so, dm_campaign_proposition_segment dcps,
                    dm_campaign_proposition dcp, dm_campaign dc, dm_offer do1
                where 
                    so.segment_id is not null and so.segment_id = dcps.id and 
                    dcp.id = dcps.proposition_id and dc.id  = dcp.camp_id and do1.id = dc.offer_id 
                group by do1.id, dc.id, to_char(date_trunc('month',so.date_order),'YYYY-MM-DD')::text, dcps.id
       )
        """)
report_sale_segment_per_month()

######DAYSSSSSSSSSSSSSSSS
#Sales by Segment and Offer Step

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
                    to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text as name,
                    s.id as offer_step_id, 
                    o.id as offer_id,
                    cmp.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity 
                from sale_order so, dm_campaign_proposition_segment seg,  
                    dm_campaign_proposition pro, dm_campaign cmp,
                    dm_offer o, dm_offer_step s
                where so.segment_id = seg.id and pro.id = seg.proposition_id
                    and cmp.id = pro.camp_id and cmp.offer_id = o.id
                    and s.offer_id = o.id and so.offer_step_id = s.id
                group by to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text ,cmp.id , o.id , s.id
             )
        """)
report_sale_per_day()

# Sales by Offer Step
class report_sale_offer_step_per_day(osv.osv):
    _name = "report.sale.offer.step.per.day"
    _description = "Sales by Offer Step per day"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        #'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_offer_step_per_day as (
               select
                    min(so.id) as id,
                    to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text as name,
            dos.id as offer_step_id,
                    do1.id as offer_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity
                from sale_order as so, dm_offer_step dos, dm_offer do1
                where 
                    so.offer_step_id is not null and so.offer_step_id = dos.id and dos.offer_id = do1.id 
                group by do1.id,  to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text, dos.id

             )
        """)
report_sale_offer_step_per_day()

#Sales by Segment
class report_sale_segment_per_day(osv.osv):
    _name = "report.sale.segment.per.day"
    _description = "Sales per day"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
       # 'offer_step_id': fields.many2one('dm.offer.step','Step', readonly=True),
        'offer_id': fields.many2one('dm.offer','Offer', readonly=True),
        'campaign_id': fields.many2one('dm.campaign','Campaign', readonly=True),
        'sale_amount': fields.float('Amount', readonly=True),
        'sale_quantity': fields.float('Quantity', readonly=True),        
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_sale_segment_per_day as (
               select
                    min(so.id) as id,
                    to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text as name,
                    dcps.id as Segment,
                    do1.id as offer_id,
                    dc.id as campaign_id,
                    sum(so.amount_total) as sale_amount ,
                    count(so.id) as sale_quantity
                from sale_order as so, dm_campaign_proposition_segment dcps,
                    dm_campaign_proposition dcp, dm_campaign dc, dm_offer do1
                    
                where 
                    so.segment_id is not null and so.segment_id = dcps.id and 
                    dcp.id = dcps.proposition_id and dc.id  = dcp.camp_id and do1.id = dc.offer_id 
                    
                group by do1.id, dc.id, to_char(date_trunc('day',so.date_order),'YYYY-MM-DD')::text, dcps.id
             )
        """)
report_sale_segment_per_day()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

