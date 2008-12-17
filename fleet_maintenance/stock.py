from osv import fields,osv
import tools
import ir
import pooler
from mx import DateTime

#TODO make this configurable parameters:
fixed_month_init_day = 1
fixed_default_anniversary_month = 12 

class stock_location(osv.osv):
    _inherit = "stock.location"    
    
    def _is_expired(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, now.day, 0, 0, 0.0)
        for fleet in self.browse(cr, uid, ids, context):
            res[fleet.id] = fleet.expire_time and date > DateTime.strptime(fleet.expire_time, '%Y-%m-%d') or False
        return res
    
    
    def _expire_time(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for fleet in self.browse(cr, uid, ids, context):
            max_time = 0
            for invoice_line in fleet.account_invoice_lines:
                if invoice_line.maintenance_end_date > max_time:
                    max_time = invoice_line.maintenance_end_date
            res[fleet.id] = max_time
        return res
    
    def _time_to_expire(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, now.day)
        for fleet in self.browse(cr, uid, ids, context):
            print fleet.expire_time
            print date
            res[fleet.id] = fleet.expire_time and int((DateTime.strptime(fleet.expire_time, '%Y-%m-%d') - date).days) or False
        return res
    
    #retrieve anniversary time from parent eventually
    def _anniversary_time(self, cr, uid, ids, field_name, arg, context={}):
        res = {}    
        for fleet in self.browse(cr, uid, ids, context):
            res[fleet.id] = fleet.location_id and fleet.location_id.intrinsic_anniversary_time or fleet.intrinsic_anniversary_time
        return res
    
    def _get_parent_fleet_id(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for location in self.browse(cr, uid, ids):
            res[location.id] = location.location_id.id
        return res
    
    #dummy; what matters is onchange_parent_fleet_id
    def _set_parent_fleet_id(self, cr, uid, ids, name, value, arg, context):
        if not value: return False
        
        if isinstance(ids, (int, long)):
            ids = [ids]
            
        for location in self.browse(cr, uid, ids):
            print "2222222"
            print location
            print value
            
    def onchange_parent_fleet_id(self, cr, uid, ids, location_id):
        result = {}
        result['value'] = {}
        if not location_id:
            return result
        
        result['value'].update({'location_id': location_id})
        return result
        


    _columns = {
        'fleet_type': fields.selection([('none','Not a Fleet'),('fleet','Fleet'),('sub_fleet','Sub Fleet')], 'Fleet type', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', required = False, ondelete = 'cascade', select = True),
        'parent_partner_id': fields.related('location_id', 'partner_id', type='many2one', relation='res.partner', string='Customer'),
        'sale_order_lines': fields.one2many('sale.order.line', 'fleet_id', 'Sale Order Lines'),
        'account_invoice_lines': fields.one2many('account.invoice.line', 'fleet_id', 'Invoice Lines'),
        'crm_cases': fields.one2many('crm.case', 'fleet_id', 'Events'),
        'parent_fleet_id': fields.function(_get_parent_fleet_id, fnct_inv=_set_parent_fleet_id, method=True, type='many2one', relation='stock.location', string='Parent Fleet'),
        'is_expired': fields.function(_is_expired, method=True, type='boolean', string="Expired ?"),
        'time_to_expire': fields.function(_time_to_expire, method=True, type='integer', string="Days before expire"),
        'intrinsic_anniversary_time':fields.date('Intrinsic Time', required = False),
        #TODO anniversary_time -> fields related?
        'anniversary_time':fields.function(_anniversary_time, method=True, type='date', string="Anniversary Time"), #TODO no year!
        'expire_time':fields.function(_expire_time, method=True, type='date', string="Maintenance Expire Time"),
    }
    
    
    def intrinsic_anniversary_time_change(self, cr, uid, ids, anniversary_time=False):
        result = {}
        if anniversary_time:
            anniversary_time = DateTime.strptime(anniversary_time, '%Y-%m-%d')
            if anniversary_time.day != fixed_month_init_day:
                anniversary_time = DateTime.DateTime(anniversary_time.year, anniversary_time.month, fixed_month_init_day)
                result['value'] = {'intrinsic_anniversary_time': anniversary_time.strftime('%Y-%m-%d')}
                result['warning'] = {'title':'Incorrect Anniversary Time', 'message':"- Anniversary date should should ideally start at day %s of the month; corrected to day %s\n" % (fixed_month_init_day, fixed_month_init_day)}
        return result
                
    
    
    def _default_usage(self, cr, uid, context={}):
        if context.get('fleet_type', 'none') != 'none':
            return 'customer'
        return False
    
    def _default_anniversary_time(self, cr, uid, context={}):
        date = DateTime.DateTime(DateTime.now().year, fixed_default_anniversary_month, fixed_month_init_day, 0, 0, 0.0)
        return date.strftime('%Y-%m-%d')
    
    def _default_fleet_type(self, cr, uid, context={}):
        if context.get('fleet_type', 'none') == 'fleet':
            return 'fleet'
        elif context.get('fleet_type', 'none') == 'sub_fleet':
            return 'sub_fleet'
        return 'none'
    
    def _default_location_id(self, cr, uid, context={}):
        if context.get('fleet_type', 'none') == 'fleet':
            return 8 #FIXME, not very solid, rather use somthing like property_stock_customer
        return False
    
    
    _defaults = {
        'usage': _default_usage,
        'intrinsic_anniversary_time': _default_anniversary_time,
        'fleet_type' : _default_fleet_type,
        'location_id' : _default_location_id,
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
                for invoice_line in order_line.invoice_lines:
                    if order_line.product_id and order_line.product_id.is_maintenance:
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'maintenance_start_date':order_line.maintenance_start_date, \
                                                                                               'maintenance_end_date':order_line.maintenance_end_date, \
                                                                                               'maintenance_month_qty':order_line.maintenance_month_qty, \
                                                                                               'maintenance_product_qty':order_line.maintenance_product_qty, \
                                                                                               })
                    if order_line.fleet_id: #product sent to fleet but not maintenance -> we copy the information too
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'fleet_id':order_line.fleet_id.id})
                

        return create_ids
    
stock_picking()