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
                if invoice_line.maintenance_end_date > max_time:
                    max_time = invoice_line.maintenance_end_date
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


    _columns = {
        "is_fleet" : fields.boolean('Is Fleet?'),
        "is_sub_fleet" : fields.boolean('Is Sub Fleet?'),
        'partner_id': fields.many2one('res.partner', 'Customer', required = False, ondelete = 'cascade', select = True),
        'parent_partner_id': fields.related('location_id', 'partner_id', type='many2one', relation='res.partner', string='Customer'),
        'sale_order_lines': fields.one2many('sale.order.line', 'fleet_id', 'Sale Order Lines'),
        'account_invoice_lines': fields.one2many('account.invoice.line', 'fleet_id', 'Invoice Lines'),
        'crm_cases': fields.one2many('crm.case', 'fleet_id', 'Events'),
        'is_expired': fields.function(_is_expired, method=True, type='boolean', string="Expired ?"),
        'time_to_expire': fields.function(_time_to_expire, method=True, type='float', string="Time before expire"),
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
        if context.get('is_fleet', True) or context.get('is_sub_fleet', True):
            return 'customer'
        return False
    
    def _default_anniversary_time(self, cr, uid, context={}):
        date = DateTime.DateTime(DateTime.now().year, fixed_default_anniversary_month, fixed_month_init_day, 0, 0, 0.0)
        return date.strftime('%Y-%m-%d')
    
    def _default_is_fleet(self, cr, uid, context={}):
        print context
        if context.has_key('is_fleet') and context['is_fleet']:
            return True
        return False
    
    def _default_is_sub_fleet(self, cr, uid, context={}):
        print context
        if context.has_key('is_sub_fleet') and context['is_sub_fleet']:
            return True
        return False
    
    
    _defaults = {
        'usage': _default_usage,
        'intrinsic_anniversary_time': _default_anniversary_time,
        'is_fleet' : _default_is_fleet,
        'is_sub_fleet' : _default_is_sub_fleet
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