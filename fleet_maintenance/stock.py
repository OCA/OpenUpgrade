from osv import fields,osv
from mx import DateTime

#TODO make this configurable parameters:
fixed_month_init_day = 1
fixed_default_anniversary_month = 12

class stock_location(osv.osv):
    _inherit = "stock.location"


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form' and context.get('fleet_type', False) == 'sub_fleet':
            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name','=','stock.location.fleet.form.sub_fleet_maintenance')])[0]
        elif view_type == 'form' and context.get('fleet_type', False) == 'fleet':
            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name','=','stock.location.fleet.form.fleet_maintenance')])[0]
        elif view_type == 'tree' and context.get('fleet_type', False) == 'sub_fleet':
            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name','=','sub_fleet.tree')])[0]
        #elif view_type == 'tree' and context.get('fleet_type', False) == 'fleet':
        #    pass
        return  super(stock_location, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)


    def _is_expired(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, now.day, 0, 0, 0.0)
        for fleet in self.browse(cr, uid, ids, context):
            if fleet.expire_time:
                res[fleet.id] = date > DateTime.strptime(fleet.expire_time, '%Y-%m-%d')
            else:
                res[fleet.id] = True #by default no maintenance expire terms means no coverage
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
            res[fleet.id] = fleet.expire_time and int((DateTime.strptime(fleet.expire_time, '%Y-%m-%d') - date).days) or False
        return res

    #retrieve anniversary time from parent eventually
    def _anniversary_time(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for fleet in self.browse(cr, uid, ids, context):
            res[fleet.id] = fleet.location_id and fleet.location_id.intrinsic_anniversary_time or fleet.intrinsic_anniversary_time
        return res


    _columns = {
        'fleet_type': fields.selection([('none','Not a Fleet'),('fleet','Fleet'),('sub_fleet','Sub Fleet')], 'Fleet type', required=False),
        'partner_id': fields.many2one('res.partner', 'Customer', required = False, ondelete = 'cascade', select = True),
        'parent_partner_id': fields.related('location_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', store=True),
        'sale_order_lines': fields.one2many('sale.order.line', 'fleet_id', 'Sale Order Lines'),
        'fleet_sale_order_lines': fields.one2many('sale.order.line', 'parent_fleet_id', 'Sale Order Lines'),
        'account_invoice_lines': fields.one2many('account.invoice.line', 'fleet_id', 'Invoice Lines'),
        'fleet_account_invoice_lines': fields.one2many('account.invoice.line', 'parent_fleet_id', 'Invoice Lines'),
        'crm_cases': fields.one2many('crm.case', 'fleet_id', 'Events'),
        'fleet_crm_cases': fields.one2many('crm.case', 'parent_fleet_id', 'Events'),
        'is_expired': fields.function(_is_expired, method=True, type='boolean', string="Expired ?"),
        'time_to_expire': fields.function(_time_to_expire, method=True, type='integer', string="Days before expiry"),
        'intrinsic_anniversary_time':fields.date('Intrinsic Time', required = False),
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

    #FIXME: this call back is due to a current OpenERP limitation:
    #currently (v5, March 2009), it's not possible to use the orm create method to create a hierarchy of objects all together within a single call.
    #this is due to a bug/limitation of the Modified Pre-orderered Tree Traversal algorithm.
    def sub_fleet_change(self, cr, uid, ids, fleet_id):
        result = {}
        if not fleet_id:
            result['warning'] = {'title': 'Save PARENT FLEET first please!', 'message':'Due to a current OpenERP limitation, you should please close the SUBFLEET popup and save the form BEFORE adding any subfleet'}
            result['value'] = {'child_ids':[]}
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
            return 8 #FIXME, not very solid, rather use something like property_stock_customer
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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form' and context.get('view', False) == 'incident':
            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name','=','stock.picking.incident.form')])[0]
        return  super(stock_picking, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)


    #copy extra invoice line info when invoicing on delivery, if the "delivery" module is installed, it should be a dependence of this module for this to
    #work properly!
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):

        create_ids = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id,
            group, type, context)

        for picking in self.browse(cr, uid, ids, context=context):
            if picking.sale_id:
                for order_line in picking.sale_id.order_line:
                    for invoice_line in order_line.invoice_lines:
                        if order_line.product_id and order_line.product_id.is_maintenance:
                            self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'maintenance_start_date':order_line.maintenance_start_date, \
                                                                                                   'maintenance_end_date':order_line.maintenance_end_date, \
                                                                                                   'maintenance_product_qty':order_line.maintenance_product_qty, \
                                                                                                   'account_analytic_id':order_line.product_id.maintenance_analytic_id.id \
                                                                                                   }) #TODO, we could use product categories to retrieve the maintenance_analytic_id
                        if order_line.fleet_id: #product sent to fleet but not maintenance -> we copy the information too
                            self.pool.get('account.invoice.line').write(cr, uid, invoice_line.id, {'fleet_id':order_line.fleet_id.id})


        return create_ids

stock_picking()



class stock_move(osv.osv):
    _inherit = "stock.move"

    def _default_product_id(self, cr, uid, context={}):
        return context.get('product_id', False)

    def _default_prodlot_id(self, cr, uid, context={}):
        return context.get('prodlot_id', False)

    def _default_location_id(self, cr, uid, context={}):
        return context.get('location_id', False) or super(stock_move, self)._default_location_source(cr, uid, context)

    def _default_location_dest_id(self, cr, uid, context={}):
        return context.get('location_dest_id', False) or super(stock_move, self)._default_location_destination(cr, uid, context)

    def _default_name(self, cr, uid, context={}):
        return "RMA_move"


    _defaults = {
        'product_id': _default_product_id,
        'prodlot_id': _default_prodlot_id,
        'location_id': _default_location_id,
        'location_dest_id': _default_location_dest_id,
        'name': _default_name,
    }

stock_move()
