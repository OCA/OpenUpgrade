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
from osv import fields,osv
from mx import DateTime


class report_auction_adjudication1(osv.osv):
    _name = "report.auction.adjudication1"
    _description = "report_auction_adjudication"
    _auto = False
    def _adjudication_get(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        tmp={}
        for id in ids:
            tmp[id]=0.0
            cr.execute("select sum(obj_price) from auction_lots where auction_id=%s", (id,))
            sum = cr.fetchone()
            if sum:
                tmp[id]=sum[0]
        return tmp
    _columns = {
                'name': fields.char('Auction date', size=64, required=True,select=True),
                'auction1': fields.date('First Auction Day', required=True,select=True),
                'auction2': fields.date('Last Auction Day', required=True,select=True),
                'buyer_costs': fields.many2many('account.tax', 'auction_buyer_taxes_rel', 'auction_id', 'tax_id', 'Buyer Costs'),
                'seller_costs': fields.many2many('account.tax', 'auction_seller_taxes_rel', 'auction_id', 'tax_id', 'Seller Costs'),
                'adj_total': fields.float('Total Adjudication',select=True),
#                'state': fields.selection((('draft','Draft'),('close','Closed')),'State', select=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_auction_adjudication1 as (
                select
                    l.id as id,
                    l.name as name,
                    l.auction1 as auction1,
                    l.auction2 as auction2,
                    sum(m.obj_price) as adj_total

                from
                    auction_dates l ,auction_lots m
                where m.auction_id=l.id
                group by l.id,l.name,l.auction1,l.auction2

            )
        """)
report_auction_adjudication1()

class report_per_seller_customer(osv.osv):
        _name = "report.per.seller.customer"
        _description = "Customer per seller"
        _auto = False
        _columns = {
                    'name': fields.char('Seller', size=64, required=True,select=True),
                    'no_of_buyer': fields.integer('Buyer'),
                    'partner_id' : fields.many2one('res.partner', 'Partner')
        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_per_seller_customer as (
                   select
                           ad.id as id,
                           rs.name as name,
                           count(ab.partner_id) as no_of_buyer

                    from auction_bid ab,
                        auction_bid_line abl,
                        auction_lots al,
                        auction_deposit ad,
                        res_partner rs
                    where rs.id=ad.partner_id and
                         ab.id=abl.bid_id and
                         abl.lot_id=al.id and
                         al.bord_vnd_id=ad.id and
                         ad.partner_id=rs.id
                    group by rs.name,ad.id
                  )""")
report_per_seller_customer()

class report_latest_deposit(osv.osv):
        _name = "report.latest.deposit"
        _description = "Latest 10 Deposits"
        _auto = False
        _columns = {
            'name': fields.char('Depositer Inventory', size=64, required=True,select=True),
            'partner_id': fields.many2one('res.partner', 'Seller', required=True, change_default=True,select=True),
            'date_dep': fields.date('Deposit date', required=True,select=True),
            'method': fields.selection((('keep','Keep until sold'),('decease','Decrease limit of 10%'),('contact','Contact the Seller')), 'Withdrawned method', required=True),
            'tax_id': fields.many2one('account.tax', 'Expenses'),
            'info': fields.char('Description', size=64),
            'lot_id': fields.one2many('auction.lots', 'bord_vnd_id', 'Objects'),
            'specific_cost_ids': fields.one2many('auction.deposit.cost', 'deposit_id', 'Specific Costs'),
            'total_neg': fields.boolean('Allow Negative Amount'),
            'user_id':fields.many2one('res.users', 'User', select=True),
        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_latest_deposit as (
                    SELECT
                       l.id as id,
                       l.create_uid as user_id,
                       l.name as name,
                       l.partner_id as partner_id,
                       l.date_dep as date_dep,
                       l.method as method,
                       l.tax_id as tax_id,
                       l.info as info

                   from auction_deposit l
                   order by l.id desc
                   limit 10

                  )""")
report_latest_deposit()

class report_latest_objects(osv.osv):
        _name = "report.latest.objects"
        _description = "Latest 10 Objects"
        _auto = False
        _columns = {
                'partner_id': fields.many2one('res.partner', 'Seller', required=True, change_default=True),
                'auction_id': fields.many2one('auction.dates', 'Auction Date'),
                'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True,select=True),
                'obj_desc': fields.text('Object Description',select=True),
                'obj_num': fields.integer('Catalog Number',select=True),
                'obj_ret': fields.float('Price retired',select=True ),
                'obj_comm': fields.boolean('Commission', select=True),
                'obj_price': fields.float('Adjudication price', select=True),
                'user_id':fields.many2one('res.users', 'User',  select=True),
        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_latest_objects as (
                    SELECT
                       l.id as id,
                       l.bord_vnd_id as bord_vnd_id,
                       l.create_uid as user_id,
                       l.auction_id as auction_id,
                       l.obj_desc as obj_desc,
                       l.obj_num as obj_num,
                       l.obj_ret as obj_ret,
                       l.obj_comm as obj_comm,
                       l.obj_price as obj_price

                   from auction_lots l
                   order by l.id desc
                   limit 10

                  )""")
report_latest_objects()
def _type_get(self, cr, uid,ids):
    cr.execute('select name, name from auction_lot_category order by name')
    return cr.fetchall()
class report_auction_object_date1(osv.osv):
    _name = "report.auction.object.date1"
    _description = "Objects per day"
    _auto = False
    _columns = {
            'auction_id': fields.many2one('auction.dates', 'Auction Date'),
            'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True),
            'name': fields.char('Short Description',size=64, required=True),
            'lot_type': fields.selection(_type_get, 'Object Type', size=64),
            'obj_desc': fields.text('Object Description'),
            'obj_num': fields.integer('Catalog Number',select=True),
            'obj_ret': fields.float('Price retired'),
            'obj_comm': fields.boolean('Commission'),
            'obj_price': fields.float('Adjudication price'),
            'state': fields.selection((('draft','Draft'),('unsold','Unsold'),('paid','Paid'),('invoiced','Invoiced')),'State', required=True, select=True),
            'date': fields.char('Name', size=64, required=True,select=True),
            'lot_num': fields.integer('Quantity', required=True),
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_auction_object_date1 as (
                select
                   min(l.id) as id,
                   to_char(l.create_date, 'YYYY-MM-DD') as date,
                   sum(l.obj_num) as obj_num,
                   l.state as state
                from
                    auction_lots l
                group by
                    to_char(l.create_date, 'YYYY-MM-DD'),l.id,l.state
            )
        """)
report_auction_object_date1()

class report_auction_estimation_adj_category1(osv.osv):
    _name = "report.auction.estimation.adj.category1"
    _description = "comparison estimate/adjudication "
    _auto = False
    _columns = {
            'auction_id': fields.many2one('auction.dates', 'Auction Date'),
            'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True),
            'name': fields.char('Short Description',size=64, required=True),
            'lot_type': fields.selection(_type_get, 'Object Type', size=64,select=True),
            'lot_est1': fields.float('Minimum Estimation',select=True),
            'lot_est2': fields.float('Maximum Estimation',select=True),
            'obj_desc': fields.text('Object Description',select=True),
            'obj_num': fields.integer('Catalog Number'),
            'obj_ret': fields.float('Price retired'),
            'obj_comm': fields.boolean('Commission'),
            'obj_price': fields.float('Adjudication price'),
            'state': fields.selection((('draft','Draft'),('unsold','Unsold'),('paid','Paid'),('invoiced','Invoiced')),'State', required=True,select=True),
            'date': fields.char('Name', size=64, required=True,select=True),
            'lot_num': fields.integer('Quantity', required=True),
            'lot_type': fields.selection(_type_get, 'Object Type', size=64),
            'adj_total': fields.float('Total Adjudication',select=True),
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_auction_estimation_adj_category1 as (
                select
                    min(l.id) as id,
                   to_char(l.create_date, 'YYYY-MM-01') as date,
                   l.state as state,
                   l.lot_type as lot_type,
                   sum(l.lot_est1) as lot_est1,
                   sum(l.lot_est2) as lot_est2,
                   sum(l.obj_price) as adj_total
                from
                    auction_lots l,auction_dates m
                where l.auction_id=m.id
                group by
                    to_char(l.create_date, 'YYYY-MM-01'),l.state,lot_type
            )
        """)
report_auction_estimation_adj_category1()

class report_auction_user_pointing1(osv.osv):
    _name = "report.auction.user.pointing1"
    _description = "user pointing "
    _auto = False
    _columns = {
            'user_id': fields.char('User',size=64, required=True, select=True),
            'name': fields.date('Date', select=True),
            'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet',  select=True),
            'total_timesheet': fields.float('Project Timesheet',select=True),
      }

    def init(self, cr):
        cr.execute("""
            create or replace view report_auction_user_pointing1 as (
                select r.name as user_id,
                        l.id as id,
                        l.total_timesheet as total_timesheet

                from hr_timesheet_sheet_sheet_day l,
                     hr_timesheet_sheet_sheet h,
                     res_users r
                where h.id=l.sheet_id
                and
                l.name=h.date_current-1
                and
                h.user_id=r.id

            )
        """)
report_auction_user_pointing1()

# Report for Seller and Buyer Reporting Menu


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

