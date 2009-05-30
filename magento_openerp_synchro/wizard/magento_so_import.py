# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaêl Valyi
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

import netsvc
import xmlrpclib
import pooler
import wizard
from xml.parsers.expat import ExpatError
from xmlrpclib import ProtocolError

#===============================================================================
#    Payment mapping constants; change them if you need
#===============================================================================

#TODO: makes this a parametrable OpenERP persistent object
payments_mapping = {'checkmo': 'prepaid', 'ccsave': 'prepaid', 'free':'prepaid','googlecheckout':'prepaid','paypayl_express':'prepaid'}
default_payment = 'prepaid'
#other possible OpenERP values would be: 'manual', 'postpaid' and 'picking'
#using 'postpaid' might be interresting for testing purposes


def _do_import(self, cr, uid, data, context):
    
    so_nb = 0
    has_error = 0

    self.pool = pooler.get_pool(cr.dbname)
    logger = netsvc.Logger()
    
    mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
    mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
    server = mw.connect_custom_api()


    #===============================================================================
    #    Sale order sync processing
    #===============================================================================
    
    magento_orders = self.pool.get('sale.order').search(cr, uid, [('magento_id', '>', 0)])
    if magento_orders:
        last_order = self.pool.get('sale.order').browse(cr, uid, max(magento_orders))
        last_order_id = last_order.magento_id
    else:
        last_order_id = 0
    
    # attempt to retrieve the sale order
    sale_order_array=[]

    try:
        sale_order_array = server.sale_orders_sync(last_order_id)
    except ProtocolError, error:
        logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Error, can't connect to Magento OpenERP sale import PHP extension at %s ! Are you sure you installed it? Error: %s") % (mw.magento_url, error))
        raise wizard.except_wizard(_("Magento Import"), _("Error, can't connect to Magento OpenERP sale import PHP extension at %s ! Are you sure you installed it? Error: %s") % (mw.magento_url, error))
    except ExpatError, error:
        logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Error occurred during Sales Orders Sync, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!\nError %s") % error)
        raise wizard.except_wizard(_("Magento Import"), _("Error occurred during Sales Orders Sync, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!"))

    
    # order Processing
    for so in sale_order_array:
        
        # is there a matching OpenERP partner?
        partner_id = self.pool.get('res.partner').search(cr, uid, [('magento_id', '=', so['customer']['customer_id'])])
        
        # if partner is known, then check the address
        if partner_id:
            known_ba= False
            known_sa= False
            
            # getting all the partner addresses
            adr_ids = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', partner_id[0])])
            
            # checks for bill an ship address
            for adr_id in adr_ids:
                # iterates over the addresses
                address = self.pool.get('res.partner.address').browse(cr, uid, adr_id)
                # Does the address exist?
                if ((address.name == so['billing_address']['firstname']+" "+so['billing_address']['lastname']) and 
                    (address.street == so['billing_address']['street']) and 
                    (address.street2 == so['billing_address']['street2']) and 
                    (address.city == so['billing_address']['city']) and 
                    (address.zip == so['billing_address']['postcode']) and 
                    (address.phone == so['billing_address']['phone'])):
                
                    known_ba= True
                    bill_adr_id = address.id
                    
                if ((address.name == so['shipping_address']['firstname']+" "+so['shipping_address']['lastname']) and 
                    (address.street == so['shipping_address']['street']) and 
                    (address.street2 == so['shipping_address']['street2']) and 
                    (address.city == so['shipping_address']['city']) and 
                    (address.zip == so['shipping_address']['postcode']) and 
                    (address.phone == so['shipping_address']['phone'])):
                    
                    known_sa= True
                    ship_adr_id = address.id
        
                
        # unknown business partner -> create a new one 
        else:
            partner_id = self.pool.get('res.partner').create(cr, uid, {
                'name': so['customer']['customer_name'],
                'magento_id': so['customer']['customer_id'],
            })
            
            known_ba= False
            known_sa= False
            
            
        if(type(partner_id) == list):
            fixed_partner_id = partner_id[0]
        else:
            fixed_partner_id = partner_id
                    
        # if address doesn't exist, create it
        if(known_ba == False):
            bill_adr_id = self.pool.get('res.partner.address').create(cr, uid, {
            'partner_id': fixed_partner_id,
            'name': so['billing_address']['firstname']+" "+so['billing_address']['lastname'],
            'street': so['billing_address']['street'],
            'street2': so['billing_address']['street2'],
            'city': so['billing_address']['city'],
            'zip': so['billing_address']['postcode'],
            'phone': so['billing_address']['phone'],
            })
            
        # if the address does'nt exist & isn't the same as billing, create it
        if((so['shipping_address'] == so['billing_address']) and known_sa == False):
            ship_adr_id = self.pool.get('res.partner.address').create(cr, uid, {
                'partner_id': fixed_partner_id,
                'name': so['shipping_address']['firstname']+" "+so['shipping_address']['lastname'],
                'street': so['shipping_address']['street'],
                'street2': so['shipping_address']['street2'],
                'city': so['shipping_address']['city'],
                'zip': so['shipping_address']['postcode'],
                'phone': so['shipping_address']['phone'],
            })
        # if billing & shipping are the same, retrieve id
        else:
            ship_adr_id = bill_adr_id
                
        
        # retrieves Magento Shop in OpenERP
        shop_id=self.pool.get('sale.shop').search(cr, uid, [('magento_flag', '=', True)])
        if shop_id and len(shop_id) >= 1:
            shop=self.pool.get('sale.shop').browse(cr, uid, shop_id[0])
        else:
            raise wizard.except_wizard(_('UserError'), _('You must have one shop with magento_id set to 1'))
            
        # creates Sale Order
        order_id=self.pool.get('sale.order').create(cr, uid, {
                'name': _('magento SO/')+str(so['id']),
                'partner_id': fixed_partner_id,
                'partner_shipping_id': ship_adr_id,
                'partner_invoice_id': bill_adr_id,
                'partner_order_id': bill_adr_id,
                'shop_id' : shop.id or 1, #Deal with Shop!!
                'pricelist_id' : shop.pricelist_id.id or 1, #Deal with PriceList!!
                'magento_id' : so['id'],
                'has_error' : 0,
                'order_policy' : payments_mapping[so['payment']] or default_payment 
            })
        
        #===============================================================================
        # Sale order lines
        #-If the product exist : create line
        #-Else : report error on sale order
        #===============================================================================
        line_error = False
        
        for line in so['lines']:
            # is the Magento id known?
            product=self.pool.get('product.product').search(cr, uid, [('magento_id', '=', line["product_magento_id"])])
            if product: # then save the line
                product = self.pool.get('product.product').browse(cr, uid, product[0])
                self.pool.get('sale.order.line').create(cr, uid, {
                        'product_id': product.id,
                        'name': line['product_name'],
                        'order_id': order_id,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': line['product_qty'],
                        'price_unit': line['product_price'],
                        'discount' : float(100*float(line['product_discount_amount']))/(float(line['product_price'])*float(line['product_qty'])),
                        'tax_id' : [(6, 0, [x.id for x in product.taxes_id])] #See fields.py, many2many set method.
                })
                
            # report the error
            else:
                logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Sale Order %s : Error on product id : %s sku : %s name %s") % (order_id , line['product_magento_id'], line['product_sku'], line['product_name']))
                self.pool.get('sale.order').write(cr, uid, order_id, {'has_error' : 1})
                line_error = True
           
        # shipping line
        try:
            ship_product_id=self.pool.get('product.product').search(cr, uid, [('default_code', '=', 'SHIP')])
            ship_product=self.pool.get('product.product').browse(cr, uid, ship_product_id[0])
    
            self.pool.get('sale.order.line').create(cr, uid, {
                    'product_id': ship_product_id[0],
                    'name': ship_product.name,
                    'order_id': order_id,
                    'product_uom': ship_product.uom_id.id,
                    'product_uom_qty': 1,
                    'price_unit': so['shipping_amount'],
            })

        except error:
            logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("ERROR: couldn't create a shipping product, did you configure a shipping product in the delivery module? %s") % error)
            
        # done fields counter   
        if line_error:
            has_error += 1
        
        so_nb += 1
    
    return {'so_nb':so_nb, 'has_error':has_error}


#===============================================================================
#   Wizard Declaration
#===============================================================================
        
_import_done_form = '''<?xml version="1.0"?>
<form string="Saleorders import">
    <separator string="Magento Sale Orders Synchronization" colspan="4" />
    <field name="so_nb"/>
    <field name="has_error"/>
</form>'''

_import_done_fields = {
    'so_nb': {'string':'New Sales Orders', 'readonly':True, 'type':'integer'},
    'has_error': {'string':'Sales Orders With Error', 'readonly':True, 'type':'integer'},
}

class wiz_magento_so_import(wizard.interface):
    states = {
        'init': {
            'actions': [_do_import],
            'result': {'type': 'form', 'arch': _import_done_form, 'fields': _import_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_so_import('magento.saleorders.import');
