#
#  sale.py
#  solstiswrk
#
#  Created by Nicolas Bessi on 04.05.09.
#  Copyright (c) 2009 CamptoCamp. All rights reserved.
#
from osv import osv, fields
class sale_order(osv.osv):
    _inherit = "sale.order"
    
    ## @param self The object pointer.
    ## @param cr A psycopg cursor.
    ## @param uid res.user.id that is currently loged
    ## @param ids An int or list of int that are equals to an invoice id
    ## @param context a simple dict
    def button_refresh_prices(self, cr, uid, ids, context={}):
        """when the price list change the unit price of the line does not change"""
        if not ids :
            return False
        for saleorder in self.browse(cr, uid, ids, context):
            if isinstance(saleorder.pricelist_id, osv.orm.browse_null) :
                raise osv.except_osv('Warning !', 'Please set the price list \
                the sale order')
            #we modify the requiered data in the line
            for line in saleorder.order_line :
                if  type(line.product_id) != osv.orm.browse_null\
                and line.product_id:
                    res = line.product_id_change(
                                                    saleorder.pricelist_id.id,
                                                    line.product_id.id,
                                                    line.product_uom_qty,
                                                    line.product_uom.id,
                                                    line.product_uos_qty,
                                                    line.product_uos,
                                                    '',
                                                    saleorder.partner_id, 
                                                    'lang' in context and context['lang'], 
                                                    False, 
                                                    saleorder.date_order, 
                                                    line.product_packaging, 
                                                    saleorder.fiscal_position, 
                                                    True
                                                )
                else :
                       continue
                if not line.product_uom :
                    price_unit = 0.0
                else :
                    price_unit = res['value']['price_unit']
                    self.pool.get('sale.order.line').\
                    write(cr, uid, line.id, {'price_unit' : price_unit}, {})
        return True
    
    
sale_order()