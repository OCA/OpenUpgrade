from osv import fields, osv
from mx.DateTime import RelativeDateTime, DateTime
from mx import DateTime


fixed_month_init_day = 1 # TODO make this a fields.property parameter!
fixed_days_before_month_end = 0 #TODO make this a fields.property parameter!
min_maintenance_months = 6 #TODO make this a fields.property parameter!


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def _get_maintenance_month_qty_from_start_end(self, cr, uid, start, end):
        delta = DateTime.RelativeDateDiff(end + RelativeDateTime(days=fixed_days_before_month_end + 1), start)
        return delta.months + delta.years * 12
    
    def _maintenance_month_qty(self, cr, uid, ids, prop, unknow_none, context={}):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.maintenance_start_date and line.maintenance_end_date:
                result[line.id] = self._get_maintenance_month_qty_from_start_end(cr, uid, DateTime.strptime(line.maintenance_start_date, '%Y-%m-%d'), DateTime.strptime(line.maintenance_end_date, '%Y-%m-%d'))
            else:
                result[line.id] = False
        return result
    
    _columns = {
        'maintenance_product_qty': fields.integer('Maintenance Product Quantity', required=False),
        'maintenance_month_qty': fields.function(_maintenance_month_qty, method=True, string="Maintenance Month Quantity", type='integer', store=True),          
        'fleet_id': fields.many2one('stock.location', 'Sub Fleet'),
        'parent_fleet_id': fields.related('fleet_id', 'location_id', type='many2one', relation='stock.location', string='Fleet', store=True),
        'maintenance_start_date':fields.date('Maintenance Start Date', required=False),
        'maintenance_end_date':fields.date('Maintenance End Date', required=False),
        'order_fleet_id': fields.related('order_id', 'fleet_id', type='many2one', relation='stock.location', string='Default Sale Order Sub Fleet'),
        'is_maintenance': fields.related('product_id', 'is_maintenance', type='boolean', string='Is Maintenance'),
    }
    
    def maintenance_qty_change(self, cr, uid, ids, maintenance_product_qty=False, maintenance_month_qty=False, maintenance_start_date=False, maintenance_end_date=False, is_maintenance=False, fleet_id=False):
        result = {}
        if not is_maintenance:
            return result
        
        result['value'] = {}
        warning_messages = ""
        
        if maintenance_start_date:
            start = DateTime.strptime(maintenance_start_date, '%Y-%m-%d')
            if start.day != fixed_month_init_day: 
                warning_messages += "- Start date should should ideally start at day %s of the month; corrected to day %s\n" % (fixed_month_init_day, fixed_month_init_day)
                start = DateTime.DateTime(start.year, start.month, fixed_month_init_day)
            
            result['value'].update({'maintenance_start_date': start.strftime('%Y-%m-%d')})
                #return result
            

        if maintenance_end_date:
            end = DateTime.strptime(maintenance_end_date, '%Y-%m-%d')
            en_date_check = end + DateTime.RelativeDateTime(days=fixed_days_before_month_end + 1)
            
            if end.month == en_date_check.month or en_date_check.day != 1:
                warning_messages += "- End date should should end %s days before the end of the month! It has been reset to the correct value.\n" % fixed_days_before_month_end
                day = end.days_in_month - fixed_days_before_month_end
                end = DateTime.DateTime(end.year, end.month, day, 0, 0, 0.0)
                result['value'].update({'maintenance_end_date': end.strftime('%Y-%m-%d')})

        
        if maintenance_start_date and maintenance_end_date:
            if end < start:
                warning_messages += "- End date should be AFTER Start date!\n"
                day = start.days_in_month - fixed_days_before_month_end #then we set the minimal end date 
                end = DateTime.DateTime(start.year, start.month, day, 0, 0, 0.0)
                result['value'].update({'maintenance_end_date': end.strftime('%Y-%m-%d')})
                

            maintenance_month_qty = self._get_maintenance_month_qty_from_start_end(cr, uid, start, end)
            result['value'].update({'maintenance_month_qty': maintenance_month_qty})
            if maintenance_month_qty < min_maintenance_months:
                warning_messages += "- we usually try to sell %s months at least!\n" % min_maintenance_months
                
            
            if fleet_id:
                fleet = self.pool.get('stock.location').browse(cr, uid, fleet_id)
                theoretic_end = self._get_end_date_from_start_date(cr, uid, start, fleet)
                if theoretic_end.year != end.year or theoretic_end.month != end.month or theoretic_end.day != end.day:
                    warning_messages += "- Theoretic Maintenance End Date was: %s !\n" % theoretic_end.strftime('%Y-%m-%d')
                

        if maintenance_product_qty and maintenance_month_qty: #only set the default fleet at init
            result['value'].update({'product_uom_qty': maintenance_product_qty * maintenance_month_qty})
            result['value'].update({'product_uos_qty': maintenance_product_qty * maintenance_month_qty}) # TODO * product_obj.uos_coeff
            
        if len(warning_messages) > 1:
            result['warning'] = {'title': 'Maintenance Dates Warning', 'message': warning_messages}
        return result
    
    
    def _get_end_date_from_start_date(self, cr, uid, start_date, sub_fleet):
        year = start_date.year
        anniversary_time = DateTime.strptime(sub_fleet.anniversary_time, '%Y-%m-%d')
        month = anniversary_time.month
        day = anniversary_time.days_in_month - fixed_days_before_month_end
        end = DateTime.DateTime(year, month, day, 0, 0, 0.0)
        delta = DateTime.RelativeDateDiff(end + RelativeDateTime(days=fixed_days_before_month_end + 1), start_date)
        maintenance_month_qty = delta.months + delta.years * 12
        if maintenance_month_qty < min_maintenance_months:
            end = DateTime.DateTime(year + 1, month, day, 0, 0, 0.0)
        return end
    
    
    def fleet_id_change(self, cr, uid, ids, order_fleet_id=False, fleet_id=False, product_id=False, maintenance_start_date=False, maintenance_product_qty=False):
        result = {}
        
        result['value'] = {}
        fleet_id = order_fleet_id or fleet_id
        
        if fleet_id:
            fleet = self.pool.get('stock.location').browse(cr, uid, fleet_id)
            if fleet.expire_time and not fleet.is_expired:
                start_date = DateTime.strptime(fleet.expire_time, '%Y-%m-%d') + RelativeDateTime(days=fixed_days_before_month_end + 1)
            else:
                start_date = maintenance_start_date and DateTime.strptime(maintenance_start_date, '%Y-%m-%d') or DateTime.strptime(self.default_maintenance_start_date(cr, uid, {}), '%Y-%m-%d')
            end_date = self._get_end_date_from_start_date(cr, uid, start_date, fleet)
            
            result['value'].update({'fleet_id': fleet_id})
        
            if product_id:
                product = self.pool.get('product.product').browse(cr, uid, product_id)
                if product.is_maintenance:
                    maintenance_month_qty = self._get_maintenance_month_qty_from_start_end(cr, uid, start_date, end_date)
                    result['value'].update({'maintenance_start_date': start_date.strftime('%Y-%m-%d')})
                    result['value'].update({'maintenance_end_date': end_date.strftime('%Y-%m-%d')})
                    result['value'].update({'maintenance_month_qty': maintenance_month_qty})
                    
                    result['value'].update({'product_uom_qty': maintenance_product_qty * maintenance_month_qty})
                    result['value'].update({'product_uos_qty': maintenance_product_qty * maintenance_month_qty}) # TODO * product_obj.uos_coeff
                    
        return result
    
    #TODO adapt signature to new fiscal_position parameter
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
            is_maintenance=False, maintenance_product_qty=False, maintenance_month_qty=False,order_fleet_id=False):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position)
        
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            if product_obj.is_maintenance:
                result['value'].update({'is_maintenance': True})
            else:
                result['value'].update({'is_maintenance': False})
            if is_maintenance and maintenance_product_qty and maintenance_month_qty:
                result['value'].update({'product_uom_qty': maintenance_product_qty * maintenance_month_qty})
                result['value'].update({'product_uos_qty': maintenance_product_qty * maintenance_month_qty}) # TODO * product_obj.uos_coeff
                result['warning'] = {'title': 'Maintenance Quantity Warning', 'message': "For maintenance products, you should use instead the maintenance quantity from the other tab to compute this field"}


        fleet_result = self.fleet_id_change(cr, uid, ids, order_fleet_id, False, product, False, maintenance_product_qty)
        result['value'].update(fleet_result['value'])
        
        return result
    
    
    #deal with invoice on order
    def invoice_line_create(self, cr, uid, ids, context={}):
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        i = 0
        for line in self.browse(cr, uid, ids, context):
            self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'maintenance_start_date':line.maintenance_start_date, \
                                                                                   'maintenance_end_date':line.maintenance_end_date, \
                                                                                   'maintenance_product_qty':line.maintenance_product_qty, \
                                                                                   'account_analytic_id':line.product_id.maintenance_analytic_id.id \
                                                                                   })#TODO, we could use product categories to retrieve the maintenance_analytic_id
            if line.fleet_id:
                self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'fleet_id':line.fleet_id.id})
            i = i + 1
        return create_ids


    def _check_maintenance_dates(self, cr, uid, ids):
        for order_line in self.browse(cr, uid, ids):
            if order_line.product_id.is_maintenance:
                if order_line.maintenance_start_date and order_line.maintenance_end_date:
                    return True
                return False
            return True
        
    def _check_maintenance_fleet(self, cr, uid, ids):
        for order_line in self.browse(cr, uid, ids):
            if order_line.order_id.is_loan:  #FIXME ugly because depends on product_loan module
                return True
            elif order_line.product_id.is_maintenance or order_line.product_id.type == 'product' or order_line.product_id.type == 'consu':
                if order_line.fleet_id and order_line.fleet_id.fleet_type == 'sub_fleet' and order_line.fleet_id.location_id.partner_id == order_line.order_id.partner_id:
                    return True
                return False
            return True
         
        
    _constraints = [
        (_check_maintenance_dates,
            """A maintenance product should have a valid start date and an end date""", []),
        (_check_maintenance_fleet, """A maintenance product should have sub fleet associated to the selected customer""", [])
            ] #TODO others maintenance dates constraints to 
    
    
    def default_maintenance_start_date(self, cr, uid, context={}):
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, fixed_month_init_day, 0, 0, 0.0) + DateTime.RelativeDateTime(months=3)
        return date.strftime('%Y-%m-%d')

    
    _defaults = {
        'maintenance_product_qty': lambda *a: 1,
    }


sale_order_line()




class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Default Sub Fleet'), #TODO call that sub_fleet_id ?
    }

    def action_ship_create(self, cr, uid, ids, *args):
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.fleet_id:
                    for move in order_line.move_ids:
                        self.pool.get('stock.move').write(cr, uid, move.id, {'location_dest_id':order_line.fleet_id.id})
        return result
                    

sale_order()