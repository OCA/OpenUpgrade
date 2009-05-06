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


from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config


class hotel_reservation(osv.osv):
    _name = "hotel.reservation"
    _description = "Reservation"
    _columns = {
                
                'reservation_no': fields.char('Reservation No', size=64, required=True, select=True),
                'date_order':fields.datetime('Date Ordered', required=True, readonly=True, states={'draft':[('readonly',False)]}),
                'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),      
                'partner_id':fields.many2one('res.partner', 'Guest Name', required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
                'partner_order_id':fields.many2one('res.partner.address', 'Ordering Contact', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="The name and address of the contact that requested the order or quotation."),
                'partner_shipping_id':fields.many2one('res.partner.address', 'Shipping Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
                'checkin': fields.datetime('Expected-Date-Arrival',required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'checkout': fields.datetime('Expected-Date-Departure',required=True, readonly=True, states={'draft':[('readonly',False)]}),
                'adults':fields.integer('Adults',size=64,readonly=True, states={'draft':[('readonly',False)]}),
                'childs':fields.integer('Childs',size=64,readonly=True, states={'draft':[('readonly',False)]}),             
                'reservation_line':fields.one2many('hotel_reservation.line','line_id','Reservation Line'),
                'state': fields.selection([('draft', 'Draft'),('confirm','Confirm'),('cancle','Cancle'),('done','Done')], 'State',readonly=True),
                'folio_id': fields.many2many('hotel.folio', 'hotel_folio_reservation_rel', 'order_id', 'invoice_id', 'Folio'),
                'dummy': fields.datetime('Dummy'),
               
        }
    _defaults = {
       
        'reservation_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'hotel.reservation'),
        'state': lambda *a: 'draft', 
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
         
       }
    def on_change_checkout(self,cr, uid, ids, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'),checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'),context=None):
        delta = datetime.timedelta(days=1)
        addDays = datetime.datetime(*time.strptime(checkout_date,'%Y-%m-%d %H:%M:%S')[:5]) + delta
        val = {'value':{'dummy':addDays.strftime('%Y-%m-%d %H:%M:%S')}}
        return val
        
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
        pricelist = self.pool.get('res.partner').browse(cr, uid, part).property_product_pricelist.id
        return {'value':{'partner_invoice_id': addr['invoice'], 'partner_order_id':addr['contact'], 'partner_shipping_id':addr['delivery'], 'pricelist_id': pricelist}}
    
     
    def confirmed_reservation(self,cr,uid,ids):
         
         for reservation in self.browse(cr, uid, ids):
             cr.execute("select count(*) from hotel_reservation as hr " \
                        "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                        "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                        "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                        "and hr.id <> cast(%s as integer) " \
                        "and hr.state = 'confirm' " \
                        "and hrlrr.hotel_reservation_line_id in (" \
                        "select hrlrr.hotel_reservation_line_id from hotel_reservation as hr " \
                        "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                        "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                        "where hr.id = cast(%s as integer) )" \
                        ,(reservation.checkin,reservation.checkout,str(reservation.id),str(reservation.id))
                        )
             res = cr.fetchone()
             roomcount =  res and res[0] or 0.0
             if roomcount:
                 raise osv.except_osv('Warning', 'You tried to confirm reservation with room those already reserved in this reservation period')
             else:
                 
                 self.write(cr, uid, ids, {'state':'confirm'})
             return True
    
    def _create_folio(self,cr,uid,ids):
        for reservation in self.browse(cr,uid,ids):
            for line in reservation.reservation_line:
                 for r in line.reserve:
                    folio=self.pool.get('hotel.folio').create(cr,uid,{
                                                                      'date_order':reservation.date_order,
                                                                      'shop_id':reservation.shop_id.id,
                                                                      'partner_id':reservation.partner_id.id,
                                                                      'pricelist_id':reservation.pricelist_id.id,
                                                                      'partner_invoice_id':reservation.partner_invoice_id.id,
                                                                      'partner_order_id':reservation.partner_order_id.id,
                                                                      'partner_shipping_id':reservation.partner_shipping_id.id,
                                                                      'checkin_date': reservation.checkin,
                                                                      'checkout_date': reservation.checkout,
                                                                      'room_lines': [(0,0,{'folio_id':line['id'],
                                                                                           'checkin_date':reservation['checkin'],
                                                                                           'checkout_date':reservation['checkout'],
                                                                                           'product_id':r['id'], 
                                                                                           'name':reservation['reservation_no'],
                                                                                           'product_uom':r['uom_id'].id,
                                                                                           'price_unit':r['lst_price'],
                                                                                           'product_uom_qty':(datetime.datetime(*time.strptime(reservation['checkout'],'%Y-%m-%d %H:%M:%S')[:5]) - datetime.datetime(*time.strptime(reservation['checkin'],'%Y-%m-%d %H:%M:%S')[:5])).days   
                                                                                           
                                                                                           })],
                                                                     'service_lines':reservation['folio_id']     
                                                                       })
            cr.execute('insert into hotel_folio_reservation_rel (order_id,invoice_id) values (%d,%d)', (reservation.id, folio))  
            self.write(cr, uid, ids, {'state':'done'})
        return True
hotel_reservation()

class hotel_reservation_line(osv.osv):
     _name = "hotel_reservation.line"
   
     _description = "Reservation Line"
     _columns = {
                 
               'line_id':fields.many2one('hotel.reservation'),
               'reserve':fields.many2many('product.product','hotel_reservation_line_room_rel','room_id','hotel_reservation_line_id', domain="[('isroom','=',True),('categ_id','=',categ_id)]"),   
               'categ_id': fields.many2one('product.category','Room Type',domain="[('isroomtype','=',True)]"), 
              
        }
hotel_reservation_line()





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


