from osv import fields,osv
import tools
import ir
import pooler
from mx import DateTime

class stock_location(osv.osv):
    _inherit = "stock.location"    
    
    def _is_expired(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for fleet in self.browse(cr, uid, ids, context):
            #print fleet.expire_time and DateTime.DateTime(fleet.expire_time.year, fleet.expire_time.month, fleet.expire_time.day)
            #print fleet.expire_time - DateTime.RelativeDateTime(years=-1)
            #print "*********"
            #print DateTime.now()
            #print "<"
            #print fleet.expire_time
            #print DateTime.now() < fleet.expire_time
            res[fleet.id] = DateTime.now() > fleet.expire_time #FIXME  False #not (fleet.expire_time and DateTime.now() < fleet.expire_time) #
        return res
    
    
    def _expire_time(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for fleet in self.browse(cr, uid, ids, context):
            max_time = 0
            for invoice_line in fleet.account_invoice_lines:
                if invoice_line.maintainance_end_date > max_time:
                    max_time = invoice_line.maintainance_end_date
            res[fleet.id] = max_time
        return res
    
    def _time_to_expire(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        now =  DateTime.now()
        for id in ids:
            res[id] = 0 #FIXME
        return res
    
    #retrieve anniversary time from parent eventually
    def _anniversary_time(self, cr, uid, ids, field_name, arg, context={}):
        res = {}    
        for fleet in self.browse(cr, uid, ids, context):
            #FIXME: parent_id log errors but location_id doesn't work
            #print "*******"
            #print fleet.location_id
            #print fleet.location_id.intrinsic_anniversary_time
            res[fleet.id] = fleet.location_id and fleet.location_id.intrinsic_anniversary_time or fleet.intrinsic_anniversary_time
        return res
    
    
    def _inherited_partner(self, cr, uid, ids, field_name, arg, context={}):
        res = {}    
        for fleet in self.browse(cr, uid, ids, context):
            #FIXME: parent_id log errors but location_id doesn't work
            res[fleet.id] = fleet.location_id and fleet.location_id.partner_id and fleet.location_id.partner_id.id or fleet.location_id and fleet.location_id.id or 0
            print "------------"
            print res[fleet.id]
            #res[fleet.id] = fleet.location_id and fleet.location_id.intrinsic_anniversary_time or fleet.intrinsic_anniversary_time
        return res

    _columns = {
        "is_fleet" : fields.boolean('Is Fleet?'),
        "is_sub_fleet" : fields.boolean('Is Sub Fleet?'),
        'partner_id': fields.many2one('res.partner', 'Partner', required = False, ondelete = 'cascade', select = True),
        'sale_order_lines': fields.one2many('sale.order.line', 'fleet_id', 'Sale Order Lines'),
        'account_invoice_lines': fields.one2many('account.invoice.line', 'fleet_id', 'Invoice Lines'),
        'crm_cases': fields.one2many('crm.case', 'fleet_id', 'Events'),
        'is_expired': fields.function(_is_expired, method=True, type='boolean', string="Expired ?"),
        'time_to_expire': fields.function(_time_to_expire, method=True, type='float', string="Time before expire"),
        'intrinsic_anniversary_time':fields.date('Intrinsic Time', required = False),
        'anniversary_time':fields.function(_anniversary_time, method=True, type='date', string="Anniversary Time"), #TODO no year!
        'inherited_partner':fields.function(_inherited_partner, method=True, type='integer', string="Inherited Partner"),
        'expire_time':fields.function(_expire_time, method=True, type='date', string="Maintenance Expire Time"),
    }
    
    _constraints = [] #TODO
stock_location()


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    #copy extra invoice line info when invoicing on delivery, if the "delivery" module is installed, it should be a dependence of this module for this to
    #work properly! 
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        
        create_ids = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
            group, type, context)
        
        for picking in self.browse(cr, uid, ids, context=context):
            for order_line in picking.sale_id.order_line:
                if order_line.product_id and order_line.product_id.is_maintenance:
                    for invoice_line in order_line.invoice_lines:
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'maintainance_start_date':order_line.maintainance_start_date})
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'maintainance_end_date':order_line.maintainance_end_date})
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'fleet_id':order_line.fleet_id.id})

        return create_ids
    
stock_picking()