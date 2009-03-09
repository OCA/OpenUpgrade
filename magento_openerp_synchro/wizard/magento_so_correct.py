# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi
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

import xmlrpclib
import pooler
import wizard
import netsvc
from xml.parsers.expat import ExpatError


def _do_correct(self, cr, uid, data, context):
    
    #===============================================================================
    #  Init
    #===============================================================================

    corrected = 0
    has_error = 0
    self.pool = pooler.get_pool(cr.dbname)
    logger = netsvc.Logger()


    mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
    mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
    server = mw.connect_custom_api()

    #===============================================================================
    #    Sale Order Processing
    #===============================================================================
    
    # retrieves sale orders with errors
    has_error_so_array=[]
    has_error_so_array=self.pool.get('sale.order').search(cr, uid,[('has_error','=',1)])
    
    # sale orders processing
    for so_id in has_error_so_array:
        error_so=self.pool.get('sale.order').browse(cr, uid, so_id)
        

        try:
            mag_so=server.get_sale_order(error_so.magento_id)
        except ExpatError, error:
            logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Error occurred during Sales Orders correct, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!\nError %s") % error)
            raise wizard.except_wizard(_("Magento Import"), _("Error occurred during Sales Orders correct, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!") % mw.magento_url)


        error_counter = 0
        
        for mag_line in mag_so['lines']:
            
            # is the product in the OpenERP Sale Order?
            so_line=self.pool.get('sale.order.line').search(cr,uid,[('name','=',mag_line['product_name']),('order_id','=',error_so.id)])
            
            # creates the line if not found
            if so_line:
                # tries to find the product
                product=self.pool.get('product.product').search(cr, uid, [('magento_id','=',mag_line["product_magento_id"])])
                
                # if found, register the line
                if product:
                    product = self.pool.get('product.product').browse(cr, uid, product[0])
                    self.pool.get('sale.order.line').create(cr, uid, {
                                'product_id': product.id,
                                'name': mag_line['product_name'],
                                'order_id': error_so.id,
                                'product_uom': product.uom_id.id,
                                'product_uom_qty': mag_line['product_qty'],
                                'price_unit': mag_line['product_price'],
                                'discount' : mag_line['product_discount_amount']/mag_line['product_price']*100,
                                'tax_id' : [(6,0,[x.id for x in product.taxes_id])] # See fields.py, many2many set method.
                    })
                # else declare the error
                else:
                    error_counter += 1
         
        # update the counters
        if(error_counter == 0):
            self.pool.get('sale.order').write(cr,uid,so_id,{'has_error' : 0})
            corrected += 1
        else:
            has_error += 1
             
    return {'corrected':corrected,'has_error':has_error}

#===============================================================================
#   Wizard Declaration
#===============================================================================

_correct_done_form = '''<?xml version="1.0"?>
<form string="Saleorders import">
    <separator string="Magento Sale Orders Correction" colspan="4" />
    <field name="corrected"/>
    <field name="has_error"/>
</form>'''

_correct_done_fields = {
    'corrected': {'string':'Corrected Sales Orders', 'readonly':True, 'type':'integer'},
    'has_error': {'string':'Sales Orders With Error', 'readonly':True, 'type':'integer'},
}
        
class wiz_magento_so_correct(wizard.interface):
    states = {
        'init': {
            'actions': [_do_correct],
            'result': {'type': 'form', 'arch': _correct_done_form, 'fields': _correct_done_fields,'state': [('end', 'End')] }
        }
    }
wiz_magento_so_correct('magento.saleorders.correct');
