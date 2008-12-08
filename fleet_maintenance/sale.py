from osv import fields, osv
import ir
import pooler


class sale_order_line(osv.osv):
    _inherit = "sale.order.line" 
    
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet'), #TODO call that sub_fleet_id ?
        'maintainance_start_date':fields.date('Maintenance Start Date', required=False),
        'maintainance_end_date':fields.date('Maintenance End Date', required=False),
    }
    
    #FIXME deal with invoice on delivery
    def invoice_line_create(self, cr, uid, ids, context={}):
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        print create_ids
        i = 0
        for line in self.browse(cr, uid, ids, context):
            self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'maintainance_start_date':line.maintainance_start_date})
            self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'maintainance_end_date':line.maintainance_end_date})
            self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'fleet_id':line.fleet_id.id})
            i = i + 1
        return create_ids
    

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False):
        
        print "############"
        print ids
        

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging)
        
        if product:
            context = {'lang': lang, 'partner_id': partner_id, 'qty': qty}
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product_obj.is_direct_delivery_from_product:
                result['value'].update({'fleet_id': 'make_to_order', 'is_supplier_direct_delivery': True})
        return result    


    def _check_maintenance_dates(self, cr, uid, ids):
        for order_line in self.browse(cr, uid, ids):
            if order_line.product_id.is_maintenance:
                if order_line.maintainance_start_date and order_line.maintainance_end_date:
                    return True
                return False
            return True
        
    def _check_maintenance_fleet(self, cr, uid, ids):
        for order_line in self.browse(cr, uid, ids):
            if order_line.product_id.is_maintenance:
                if order_line.fleet_id and order_line.fleet_id.is_sub_fleet and order_line.fleet_id.location_id.partner_id == order_line.order_id.partner_id:
                    return True
                return False
            return True
         
        
    _constraints = [
        (_check_maintenance_dates,
            """A maintenance product should have a valid start date and an end date""", []),
        (_check_maintenance_fleet, """A maintenance product should have sub fleet associated to the selected customer""", [])
            ]


sale_order_line()




class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Default Sub Fleet'), #TODO call that sub_fleet_id ?
    }

    #TODO test
    def action_ship_create(self, cr, uid, ids, *args):
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.sub_fleet:
                    for move in order_line.move_ids:
                        move.write(cr, uid, invoice_line.id, {'location_dest_id':order_line.fleet_id})
        return result
                    

sale_order()