from osv import fields,osv
import tools
import ir
import pooler

class crm_case(osv.osv):
    _inherit = "crm.case" 
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet', required = False, select = True),
        'is_fleet_expired': fields.related('stock.location', 'is_expired', type='boolean', string='Is Fleet Expired?'),
        #'purchase_order_state': fields.related('purchase_order', 'state', type='char', size=64, string='Purchase Order State'),
        'picking_id': fields.many2one('stock.picking', 'Repair Movement', required = False, select = True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', required = False, select = True),
    }
    
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id):
        result = {}
        result['value'] = {}
        if not prodlot_id:
            return result
        
        print prodlot_id
        
        print "select stock_location.id from stock_location left join stock_move on location_dest_id = stock_location.id where stock_move.prodlot_id = %s and fleet_type = 'sub_fleet' order by stock_move.date ASC LIMIT 1 " % prodlot_id
        
        cr.execute("select stock_location.id from stock_location left join stock_move on location_dest_id = stock_location.id where stock_move.prodlot_id = %s and fleet_type = 'sub_fleet' order by stock_move.date ASC LIMIT 1 " % prodlot_id)
        #TODO: prodlot_id, where is_sub_fleet = true !!!!!!!!
        
        
        # sale_order_line where is_supplier_direct_delivery=true and order_id=%d' % id)
        results = cr.fetchone()
        print results
        if results and len(results) > 0:
            sub_fleet = self.pool.get('stock.location').browse(cr, uid, results[0])
            result['value'].update({'fleet_id': sub_fleet.id})
            result['value'].update({'partner_id': sub_fleet.parent_partner_id.id})
            result['value'].update({'is_fleet_expired': sub_fleet.is_expired})

  
        
        return result
         
        
crm_case()