from osv import fields,osv
import tools
import ir
import pooler
from mx import DateTime

class crm_case(osv.osv):
    _inherit = "crm.case" 
    _columns = {
        'incident_ref': fields.char('Incident Ref', size=64, required=True, select=1),
        'external_ref': fields.char('Ticket Code', size=64, select=1),
        'fleet_id': fields.many2one('stock.location', 'Fleet', required = False, select = 1),
        'is_fleet_expired': fields.related('fleet_id', 'is_expired', type='boolean', string='Is Fleet Expired?'),
        'picking_id': fields.many2one('stock.picking.incident', 'Repair Picking', required = False, select = True),
        'incoming_move_id': fields.many2one('stock.move', 'Incoming Move', required = False, select = 1),
        'outgoing_move_id': fields.many2one('stock.move', 'Outgoing Move', required = False, select = True),
        'in_supplier_move_id': fields.many2one('stock.move', 'Return To Supplier Move', required = False, select = True),
        'out_supplier_move_id': fields.many2one('stock.move', 'Return From Supplier Move', required = False, select = True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', required = False, select = 1),
        'product_id': fields.related('prodlot_id', 'product_id', type='many2one', relation='product.product', string='Related Product'),
    }
    
    def default_incident_date(self, cr, uid, context={}):
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, now.day, 0, 0, 0.0)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    
    _defaults = {
        'incident_ref': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'crm.case'),
        'date': default_incident_date,
        }
    
    #def copy(self, cr, uid, id, default=None,context={}):#TODO
    
    
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id):
        result = {}
        result['value'] = {}
        if not prodlot_id:
            return result
        
        print "select stock_location.id from stock_location left join stock_move on location_dest_id = stock_location.id where stock_move.prodlot_id = %s and fleet_type = 'sub_fleet' order by stock_move.date ASC LIMIT 1 " % prodlot_id
        
        cr.execute("select stock_location.id from stock_location left join stock_move on location_dest_id = stock_location.id where stock_move.prodlot_id = %s and fleet_type = 'sub_fleet' order by stock_move.date ASC LIMIT 1 " % prodlot_id)
        
        
        # sale_order_line where is_supplier_direct_delivery=true and order_id=%d' % id)
        results = cr.fetchone()

        if results and len(results) > 0:
            sub_fleet = self.pool.get('stock.location').browse(cr, uid, results[0])
            result['value'].update({'fleet_id': sub_fleet.id})
            result['value'].update({'partner_id': sub_fleet.parent_partner_id.id})
            result['value'].update({'is_fleet_expired': sub_fleet.is_expired})
            product_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id).product_id.id
            result['value'].update({'product_id': product_id})
        else:
            result['value'].update({'fleet_id': False})
            result['value'].update({'partner_id': False})
            result['value'].update({'is_fleet_expired': False})


        return result
         
        
crm_case()