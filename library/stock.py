# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import time
import netsvc

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'customer_ref': fields.char('Customer reference', size=64),
        'procurement_ids': fields.one2many('mrp.procurement','move_id', 'Procurements')
    }


    # New function to manage the update of the quantities
    def onchange_qty(self, cr, uid, ids, qty, context=None):
        return {'value': {'product_uos_qty':qty,'product_qty':qty}}



    # action_cancel overidden to avoid the cascading cancellation
    def action_cancel(self, cr, uid, ids, context={}):
        if not len(ids):
            return True
        pickings = {}
        for move in self.browse(cr, uid, ids):
            if move.state in ('confirmed','waiting','assigned','draft'):
                if move.picking_id:
                    pickings[move.picking_id.id] = True
        self.write(cr, uid, ids, {'state':'cancel'})
        for pick_id in pickings:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_cancel', cr)
        ids2 = []
        for res in self.read(cr, uid, ids, ['move_dest_id']):
            if res['move_dest_id']:
                ids2.append(res['move_dest_id'][0])

        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)
        #self.action_cancel(cr,uid, ids2, context) # $$ [removed to avoid cascading cancellation]
        return True

stock_move()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _order = "create_date desc"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale Order', ondelete='set null', select=True, readonly=True),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order', ondelete='set null', readonly=True,select=True),
        'date_done': fields.datetime('Picking date', readonly=True),
    }
    _defaults = {
        'sale_id': lambda *a: False,
        'purchase_id': lambda *a: False,
    }

    def action_done(self, cr, uid, ids, *args):
        res = super(stock_picking, self).action_done(cr, uid, ids, *args)
        self.write(cr,uid, ids, {'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context={}):
        print 'INvoice create'
        res={}
        pgroup = {}
        get_ids = lambda y: map(lambda x: x.id, y or [])
        sales = {}
        for p in self.browse(cr,uid,ids, context):
            if p.invoice_state<>'2binvoiced':
                continue
            if not p.address_id:
                raise osv.except_osv('No partner address', \
                                     'You have to provide a partner address if you want to invoice it (Picking %s ).'%(p.name))

            taxep = p.address_id.partner_id.property_account_tax
            taxep = taxep and self.pool.get('account.tax').browse(cr, uid,taxep.id) 

            a = p.address_id.partner_id.property_account_receivable.id
            if p.address_id.partner_id and p.address_id.partner_id.property_payment_term:
                pay_term = p.address_id.partner_id.property_payment_term.id
            else:
                pay_term = False

            if p.sale_id:
                pinv_id = p.sale_id.partner_invoice_id.id
                pcon_id = p.sale_id.partner_order_id.id
                if p.sale_id.id not in sales:
                    sales[p.sale_id.id] = [x.id for x in p.sale_id.invoice_ids]
            else:
                #
                # ideal: get_address('invoice') on partner
                #
                pinv_id = p.address_id.id
                pcon_id = p.address_id.id

            val = {
                'name': p.name,
                'origin': p.name+':'+ (p.origin or ''),
                'type': type,
                'reference': "P%dSO%d"%(p.address_id.partner_id.id,p.id),
                'account_id': a,
                'partner_id': p.address_id.partner_id.id,
                'address_invoice_id': pinv_id,
                'address_contact_id': pcon_id,
                #'project_id': (p.sale_id and p.sale_id.project_id.id) or False,
                'comment': (p.note or '') + '\n' + (p.sale_id and p.sale_id.note or ''),
                'payment_term': pay_term,
            }
            if p.sale_id:
                val['currency_id'] = (p.sale_id and p.sale_id.pricelist_id.currency_id.id) or False
            if journal_id:
                val['journal_id'] = journal_id

            if group and p.address_id.partner_id.id in pgroup:
                invoice_id= pgroup[p.address_id.partner_id.id]
            else:
                invoice_id = self.pool.get('account.invoice').create(cr, uid, val ,context= context)
                pgroup[p.address_id.partner_id.id] = invoice_id


            res[p.id]= invoice_id

            for line in p.move_lines:
                tax_ids = map(lambda x: x.id, line.product_id.taxes_id)
                if taxep :
                    for tax in self.pool.get('account.tax').browse(cr, uid,tax_ids):
                        if tax.tax_group == taxep.tax_group : tax_ids.remove(tax.id)
                    tax_ids.append(taxep.id)

                a =  line.product_id.product_tmpl_id.property_account_income.id
                if not a:
                    a = line.product_id.categ_id.property_account_income_categ.id
                account_id =  a
                punit = line.sale_line_id and line.sale_line_id.price_unit or line.product_id.list_price
                if type in ('in_invoice','in_refund'):
                    punit = line.product_id.standard_price

                iline_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.product_id.name,
                    'invoice_id': invoice_id,
                    'uos_id': line.product_uos.id,
                    'product_id': line.product_id.id,
                    'account_id': account_id,
                    'price_unit': line.sale_line_id and line.sale_line_id.price_unit or line.product_id.list_price,
                    'quantity': line.product_uos_qty == 0 and line.product_qty or line.product_uos_qty,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'customer_ref': line.customer_ref,
                    'production_lot_id': line.prodlot_id.id,
                })
                if line.sale_line_id:
                    self.pool.get('sale.order.line').write(cr, uid, [line.sale_line_id.id], {
                        'invoice_line_ids': [(6, 0, [iline_id])]
                    })

            self.pool.get('stock.picking').write(cr, uid, [p.id], {'invoice_state': 'invoiced'})
            if p.sale_id:
                sids = sales[p.sale_id.id]
                if invoice_id not in sids:
                    sales[p.sale_id.id].append(invoice_id)
                    self.pool.get('sale.order').write(cr, uid, [p.sale_id.id], {
                        'invoice_ids': [(6, 0, sales[p.sale_id.id])]
                    })

                self.pool.get('sale.order').write(cr, uid, [p.sale_id.id], {
                    'invoiced': True
                })

        print 'ICI'

        result = res
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking')
        carrier_obj = self.pool.get('delivery.carrier')
        grid_obj = self.pool.get('delivery.grid')
        invoice_line_obj = self.pool.get('account.invoice.line')

        picking_ids = result.keys()
        invoice_ids = result.values()

        invoices = {}
        for invoice in invoice_obj.browse(cr, uid, invoice_ids,
                context=context):
            invoices[invoice.id] = invoice

        for picking in picking_obj.browse(cr, uid, picking_ids,
                context=context):
            if not picking.carrier_id:
                continue
            grid_id = carrier_obj.grid_get(cr, uid, [picking.carrier_id.id],
                    picking.address_id.id, context=context)
            if not grid_id:
                raise osv.except_osv('Warning',
                        'The carrier %s (id: %d) has no delivery grid!' \
                                % (picking.carrier_id.name,
                                    picking.carrier_id.id))
            invoice = invoices[result[picking.id]]
            price = grid_obj.get_price_from_picking(cr, uid, grid_id,
                    invoice.amount_untaxed, picking.weight, picking.volume,
                    context=context)
            account_id = picking.carrier_id.product_id.product_tmpl_id\
                    .property_account_income.id
            if not account_id:
                account_id = picking.carrier_id.product_id.categ_id\
                        .property_account_income_categ.id
            invoice_line_obj.create(cr, uid, {
                'name': picking.carrier_id.name,
                'invoice_id': invoice.id,
                'uos_id': picking.carrier_id.product_id.uos_id.id,
                'product_id': picking.carrier_id.product_id.id,
                'account_id': account_id,
                'price_unit': price,
                'quantity': 1,
                'invoice_line_tax_id': [(6, 0,
                    [x.id for x in (picking.carrier_id.product_id.taxes_id
                        or [])])],
            })
        print result
        return result

stock_picking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

