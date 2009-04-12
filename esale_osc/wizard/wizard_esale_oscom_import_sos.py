##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

import ir
import time
import os
import netsvc
import xmlrpclib
import pooler
import wizard
from osv import osv

_import_form = '''<?xml version="1.0" encoding="utf-8"?>
<form title="Categories import" />
'''

_import_fields = {}

_import_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form title="Saleorders import">
<separator string="saleorders succesfully imported" colspan="4" />
%s
</form>'''

_import_done_fields = {}

def _country_info(self,cr, uid, data, context):
    country_pooler = pooler.get_pool(cr.dbname).get('res.country')
    data['code'] = data['code'].upper()
    search_country = country_pooler.search(cr,uid,[('code','=',data['code'])])
    if len(search_country):
        return search_country[0]
    #end if len(search_country):
    del data['code3']
#    data['esale_oscom_id'] = data['country_id']
    del data['esale_oscom_id']
    return country_pooler.create(cr,uid,data)

def _state_info(self,cr, uid, data, country_id, context):
    state_pooler = pooler.get_pool(cr.dbname).get('res.country.state')
    data['country_id'] = country_id
    search_state = state_pooler.search(cr, uid, ['|',('code','ilike',data['code']),('name','ilike','%'+data['code']+'%'), ('country_id','=',data['country_id'])])
    if len(search_state):
        return search_state[0]
    #end if len(search_country):
#    data['esale_oscom_id'] = data['state_id']
    del data['esale_oscom_id']
    return state_pooler.create(cr,uid,data)

def _add_address(self,cr, uid, data, partner_id, context):
    address_pooler = pooler.get_pool(cr.dbname).get('res.partner.address')
    country_id = _country_info(self,cr, uid, data['country'].copy(), context)
    del data['country']
    data['country_id'] = country_id
    if type(data['state']) == type({}):
        state_id = _state_info(self,cr, uid, data['state'].copy(), country_id, context)
        data['state_id'] = state_id
    #end if type(data['state']) == type({}):
    del data['state']
    search_address = address_pooler.search(cr,uid,[('partner_id','=',partner_id),('esale_oscom_id','=',data['esale_oscom_id'])])
    if len(search_address):
        address_pooler.write(cr,uid,search_address,data)
        return search_address[0]
    else:
        data['partner_id'] = partner_id
        return address_pooler.create(cr,uid,data)
    #end if len(search_address):

def _do_import(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    website = self.pool.get('esale.oscom.web').browse(cr, uid, data['id'])

    server = xmlrpclib.ServerProxy("%s/openerp-synchro.php" % website.url)

    cr.execute("select max(esale_oscom_id) from sale_order where esale_oscom_web=%s;" % str(website.id))
    max_web_id=cr.fetchone()[0]

    min_openorder=-1
    if max_web_id:
        saleorders = server.get_saleorders(max_web_id)
        min_openorder = server.get_min_open_orders(max_web_id)
    else:
        saleorders = server.get_saleorders(0)
    no_of_so = 0
    for saleorder in saleorders:
        print "Sale order:",str(saleorder)
        oscom_partner = saleorder['partner'][0]
        default_address = saleorder['address'][0]
        del saleorder['address']
        shipping_address = saleorder['delivery'][0]
        del saleorder['delivery']
        billing_address = saleorder['billing'][0]
        del saleorder['billing']
        partner_ids = self.pool.get('res.partner').search(cr,uid,[('esale_oscom_id','=',oscom_partner['esale_oscom_id'])])
        if len(partner_ids):
            partner_id = partner_ids[0]
            self.pool.get('res.partner').write(cr,uid,partner_ids,{'name':oscom_partner['name']})
        else:
            del oscom_partner['addresses']
            partner_id = self.pool.get('res.partner').create(cr,uid,oscom_partner)
        #end if len(partner_ids):
        shipping_address['type'] = 'delivery'
        shipping_address_id = _add_address(self,cr, uid, shipping_address.copy(), partner_id, context)

        billing_address['type'] = 'invoice'
        billing_address_id = _add_address(self,cr, uid, billing_address.copy(),partner_id, context)

        default_address['type'] = 'default'
        default_address_id = _add_address(self,cr, uid, default_address.copy(), partner_id, context)

        value={ 'esale_oscom_web': website.id,
                'esale_oscom_id' : saleorder['id'],
                'shop_id'        : website.shop_id.id,
                'partner_id'     : partner_id,
                'note'           : saleorder['note'],
                #'price_type'     : saleorder['price_type']
            }

        saleorder_pool=self.pool.get('sale.order')
        value.update(saleorder_pool.onchange_shop_id(cr, uid, [], value['shop_id'])['value'])
        value.update(saleorder_pool.onchange_partner_id(cr, uid, [], value['partner_id'])['value'])
#        addresses_pool = self.pool.get('res.partner.address')
#        for address in [('address','order'), ('billing', 'invoice'), ('delivery', 'shipping')]:
#            criteria = [('partner_id', '=', website.partner_anonymous_id.id)]
#            insert = {'partner_id': website.partner_anonymous_id.id}
#            for criterium in [('city', 'city'), ('name', 'name'), ('zip','zip'), ('address', 'street') ]:
#                criteria.append((criterium[1], 'like', saleorder[address[0]][criterium[0]]))
#                insert[criterium[1]]=saleorder[address[0]][criterium[0]]
#            address_ids=addresses_pool.search(cr, uid, criteria)
#            if len(address_ids):
#                id=address_ids[0]
#            else:
#                country_ids=self.pool.get('res.country').search(cr, uid, [('name', 'ilike', saleorder[address[0]]['country'])])
#                if len(country_ids):
#                    country_id=country_ids[0]
#                else:
#                    country_id=self.pool.get('res.country').create(cr, uid, { 'name' : saleorder[address[0]]['country'],
#                                                                              'code' : saleorder[address[0]]['country'][0:2].lower()})
#                insert['country_id']=country_id
#                if address[0]=='address':
#                    insert['email']=saleorder['address']['email']
#                id=addresses_pool.create(cr, uid, insert)
#
#            value.update({'partner_%s_id' % address[1]: id})
        value['partner_invoice_id'] = billing_address_id
        value['partner_order_id'] = default_address_id
        value['partner_shipping_id'] = shipping_address_id

        order_id=saleorder_pool.create(cr, uid, value)

        for orderline in saleorder['lines']:
            ids=self.pool.get('esale.oscom.product').search(cr, uid, [('esale_oscom_id', '=', orderline['product_id']), ('web_id', '=', website.id)])
            if len(ids):
                oscom_product_id=ids[0]
                oscom_product=self.pool.get('esale.oscom.product').browse(cr, uid, oscom_product_id)
                linevalue={    'product_id'    : oscom_product.product_id.id,
                        'product_uom_qty'    : orderline['product_qty'],
                        'order_id'        : order_id
                }
                onchange_product_sol = self.pool.get('sale.order.line').product_id_change(cr, uid, [], value['pricelist_id'], linevalue['product_id'], linevalue['product_uom_qty'],False, 0, False, '', value['partner_id'])['value']
                onchange_product_sol['tax_id'] = False
                if orderline['tax_rate'] > 0.0000:
                    tax_rate_search_ids = self.pool.get('account.tax').search(cr,uid,[('tax_group','=','vat'),('amount','=',orderline['tax_rate']/100)])
                    if tax_rate_search_ids:
                        onchange_product_sol['tax_id'] = tax_rate_search_ids
                    else:
                        new_tax_id = int(self.pool.get('account.tax').create(cr,uid,{'name':'NEW '+str(orderline['tax_rate']),'amount':orderline['tax_rate']/100}))
                        onchange_product_sol['tax_id'] = [new_tax_id]
                    #end if tax_rate_search_ids:
                #end if orderline['tax_rate'] > 0.0000:
                price = orderline['price']
                name = orderline['name']
                attributes = (orderline.has_key('attributes') and orderline['attributes']) or False
                if saleorder['price_type'] == 'tax_excluded' and attributes:
                    price = eval(str(price) + attributes['price_prefix'] + str(attributes['options_values_price']))
                    name = name + ' ' + attributes['products_options'] + ' + ' + attributes['products_options_values']
                elif saleorder['price_type'] == 'tax_included':
                    price = price * (1+orderline['tax_rate']/100)
                    if attributes:
                        options_value_price = attributes['options_values_price']
                        cal_options_value_price = options_value_price * (1+orderline['tax_rate']/100)
                        price = eval(str(price) + attributes['price_prefix'] + str(cal_options_value_price))
                        name = name + ' ' + attributes['products_options'] + ' + ' + attributes['products_options_values']
                    #end if attributes:
                #end if saleorder['price_type'] == 'tax_excluded' and orderline.has_key('attributes'):
                onchange_product_sol['price_unit'] = round(price,2)
                linevalue.update(onchange_product_sol)
                linevalue.update(self.pool.get('sale.order.line').default_get(cr, uid, ['sequence', 'invoiced', 'state', 'product_packaging']))
                linevalue['name'] = name
                if linevalue.get('weight',False):
                    del linevalue['weight']
                linevalue["product_uos"]= linevalue['product_uos'] and linevalue['product_uos'][0]
                tax_id=linevalue['tax_id'] and linevalue['tax_id'][0]
                del linevalue['tax_id']

                ids=self.pool.get('sale.order.line').create(cr, uid, linevalue)
                if tax_id:
                    cr.execute('insert into sale_order_tax (order_line_id,tax_id) values (%d,%d)', (ids, tax_id))
                #end if tax_id:
        #end for orderline in saleorder['lines']:
        shopping_cost_id = self.pool.get('product.product').search(cr,uid,[('name','=','Shipping Cost')])
        if shopping_cost_id:
            if saleorder['shipping_price'] > 0.0000:
                so_line_shipping = {
                                    'product_id'    : shopping_cost_id[0],
                                    'product_uom_qty'    : 1,
                                    'order_id'        : order_id
                                    }
                so_line_shipping.update(self.pool.get('sale.order.line').product_id_change(cr, uid, [], value['pricelist_id'], so_line_shipping['product_id'], so_line_shipping['product_uom_qty'],False, 0, False, '', value['partner_id'])['value'])
                so_line_shipping.update(self.pool.get('sale.order.line').default_get(cr, uid, ['sequence', 'invoiced', 'state', 'product_packaging']))
                so_line_shipping['price_unit'] = saleorder['shipping_price']
                if so_line_shipping.get('weight',False):
                    del so_line_shipping['weight']
                del so_line_shipping['tax_id']
                ids=self.pool.get('sale.order.line').create(cr, uid, so_line_shipping)
            #end if saleorder['shipping_price'] > 0.0000:
        #end if shopping_cost_id:
        no_of_so +=1

        ######################################################################################
        oscom_pay_met = saleorder['pay_met']
        typ_ids = self.pool.get('esale.oscom.paytype').search(cr,uid,[('esale_oscom_id', '=', oscom_pay_met), ('web_id', '=', website.id)])
        so_datas = saleorder_pool.read(cr,uid,[order_id])[0]
        if typ_ids:
            typ_data = self.pool.get('esale.oscom.paytype').browse(cr, uid, typ_ids)[0]
            paytype = typ_data.paytyp
            cr.execute('select * from ir_module_module where name=%s and state=%s', ('sale_payment','installed'))
            if cr.fetchone():
                saleorder_pool.write(cr, uid, [order_id], {'payment_type': typ_data.payment_id.id})
        else:
            paytype = 'type1'
        wf_service = netsvc.LocalService("workflow")
        if paytype == 'type1':
            #SO in state draft so nothing
            pass
        elif paytype == 'type2':
            #SO in state confirmed
            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
        elif paytype == 'type3':
            #INVOICE draft
            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
            wf_service.trg_validate(uid, 'sale.order', order_id, 'manual_invoice', cr)
        elif paytype == 'type4':
            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
            wf_service.trg_validate(uid, 'sale.order', order_id, 'manual_invoice', cr)
            inv_obj = self.pool.get('account.invoice')
            inv_ids = inv_obj.search(cr,uid,[('origin','=',so_datas['name'])])
            inv_datas = inv_obj.read(cr,uid,inv_ids)[0]
            inv_id = inv_datas['id']
            inv_obj.button_compute(cr, uid, [inv_id])
            wf_service.trg_validate(uid, 'account.invoice',inv_id, 'invoice_open', cr)
        elif paytype == 'type5':
            #INVOICE payed
            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
            wf_service.trg_validate(uid, 'sale.order', order_id, 'manual_invoice', cr)
            inv_obj = self.pool.get('account.invoice')
            journal_obj = self.pool.get('account.journal')
            pay_account_id=(website.esale_account_id)['id']
            pay_journal_id=journal_obj.search(cr,uid,[('name','ilike','Bank Journal')])
            inv_ids = inv_obj.search(cr,uid,[('origin','=',so_datas['name'])])
            inv_datas = self.pool.get('account.invoice').read(cr,uid,inv_ids)[0]
            inv_id = inv_datas['id']
            inv_obj.button_compute(cr, uid, [inv_id])
            wf_service.trg_validate(uid, 'account.invoice',inv_id, 'invoice_open', cr)
            ids = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = False
            if len(ids):
                period_id = ids[0]

            invoice = self.pool.get('account.invoice').browse(cr, uid,inv_id,{})
            company_currency = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
            if invoice.currency_id.id != company_currency:
                amount = round(self.pool.get('res.currency').compute(cr, uid, invoice.currency_id.id, company_currency, invoice.amount_total), 2)
            else:
                amount = invoice.amount_total
            #inv_obj.pay_and_reconcile(cr, uid, [inv_id],amount, pay_account_id, pay_journal_id[0], False,period_id, False, context={})

            inv_obj.pay_and_reconcile(cr, uid, [inv_id],amount, pay_account_id, period_id, pay_journal_id[0], False, False, False, context={})
        else:
            #The payment method hasn't been mapped
            pass
    cr.commit()
    for saleorder in saleorders:
        server.process_order(saleorder['id'])
    lable_string = "<label string='%s SO has been imported from the web site' />" % str(no_of_so)
    wiz_esale_oscom_import_sos.states['init']['result']['arch'] = _import_done_form % lable_string
    ###################### look for open orders in site that are 'done' in TinyERP ###################
    ######################                and close them                           ###################
    if (min_openorder > -1):
        cr.execute("select esale_oscom_id from sale_order where (esale_oscom_id>=%d) and (state = 'done') and (esale_oscom_web=%d);", (min_openorder,website.id))
        openorders=cr.fetchall()
        for openorder in openorders:
            server.close_open_orders(openorder[0])
    return {}

class wiz_esale_oscom_import_sos(wizard.interface):

    states = { 'init' : { 'actions' : [_do_import],
                          'result' : { 'type'   : 'form',
                                       'arch'   : _import_done_form,
                                       'fields' : _import_done_fields,
                                       'state'  : [('end', 'End')]
                                     }
                        }
             }

wiz_esale_oscom_import_sos('esale.oscom.saleorders');
