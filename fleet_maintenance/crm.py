from osv import fields,osv
import tools
import ir
import pooler

class crm_case(osv.osv):
    _inherit = "crm.case" 
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet', required = False, select = True),
        'picking_id': fields.many2one('stock.picking', 'Repair Movement', required = False, select = True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', required = False, select = True),
    }
    
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id):
        result = {}
        result['value'] = {}
        if not prodlot_id:
            return result
        
        cr.execute('select id from stock_location left join stock_move on move_dest_id = stock_location.id order by stock_move.date ASC LIMIT 1' % prodlot_id)
        #TODO: prodlot_id, where is_sub_fleet = true !!!!!!!!
        
        
        # sale_order_line where is_supplier_direct_delivery=true and order_id=%d' % id)
        results = cr.fetchone()
        if results and len(results) > 0:
            res[id] = True #TODO
  
        
        return result
         
        
crm_case()