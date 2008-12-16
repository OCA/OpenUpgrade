from osv import fields, osv
import ir
import pooler
from mx.DateTime import RelativeDateTime, DateTime, localtime, RelativeDateTimeDiff
import time
from mx import DateTime


fixed_month_init_day = 1 # TODO make this a parameter!
fixed_days_before_month_end = 0 #TODO make this a parameter!
min_maintenance_months = 6 #TODO make this a parameter!


class sale_order_line(osv.osv):
    _inherit = "sale.order.line" 
    
#    def _maintenance_end_date(self, cr, uid, ids, field_name, arg, context={}):
#        res = {}    
#        for line in self.browse(cr, uid, ids, context):
#            if line.maintenance_start_date and line.maintenance_month_qty:
#                res[line.id] = (DateTime.strptime(line.maintenance_start_date, '%Y-%m-%d') + DateTime.RelativeDateTime(months=line.maintenance_month_qty)).strftime('%Y-%m-%d')
#                print res[line.id]
#            else:
#                res[line.id] = False
#                
#            return res
    
    
    _columns = {
        'maintenance_month_qty': fields.integer('Maintenance Month Quantity', required=False),
        'maintenance_product_qty': fields.integer('Maintenance Product Quantity', required=False),              
        'fleet_id': fields.many2one('stock.location', 'Fleet'), #TODO call that sub_fleet_id ?
        'maintenance_start_date':fields.date('Maintenance Start Date', required=False),
        'maintenance_end_date':fields.date('Maintenance End Date', required=False),
        'order_fleet_id': fields.related('order_id', 'fleet_id', type='many2one', relation='stock.location', string='Default Sale Order Sub Fleet'),
        'is_maintenance': fields.related('product_id', 'is_maintenance', type='boolean', string='Is Maintenance'),
        #'product_type': fields.related('product_id', 'type', type='selection', string='Product Type')
    }
    
    def maintenance_qty_change(self, cr, uid, ids, maintenance_product_qty=False, maintenance_month_qty=False, maintenance_start_date=False, maintenance_end_date=False):
        result = {}
        result['value'] = {}
        print "**************************"
        warning_messages = ""
        
        if maintenance_start_date:
            start = DateTime.strptime(maintenance_start_date, '%Y-%m-%d')
            print start
            print start.day
            if start.day != fixed_month_init_day: 
                warning_messages += "- Start date should should ideally start at day %s of the month; corrected to day %s\n" % (fixed_month_init_day, fixed_month_init_day)
                start = DateTime.DateTime(start.year, start.month, fixed_month_init_day)
                result['value'].update({'maintenance_start_date': start.strftime('%Y-%m-%d')})
                #return result
            

        if maintenance_end_date:
            end = DateTime.strptime(maintenance_end_date, '%Y-%m-%d')
            en_date_check = end + DateTime.RelativeDateTime(days=fixed_days_before_month_end + 1)
            print end
            print en_date_check
            print end.month
            print en_date_check.month
            
            if end.month == en_date_check.month or en_date_check.day != 1:
                warning_messages += "- End date should should ideally end %s days before the end of the month\n" % fixed_days_before_month_end
                #TODO correct end day eventually
                #return result

        
        if maintenance_start_date and maintenance_end_date:
            
            if end < start:
                result['value'].update({'maintenance_end_date': start.strftime('%Y-%m-%d')}) #TODO not good with end days!
                warning_messages += "- End date should be AFTER Start date!\n"
                #return result

            print "qty checking"
            print start
            print end + RelativeDateTime(days=fixed_days_before_month_end + 1)
            maintenance_month_qty = self._get_maintenance_month_qty_from_start_end(cr, uid, start, end)
            result['value'].update({'maintenance_month_qty': maintenance_month_qty})
            if maintenance_month_qty < min_maintenance_months:
                warning_messages += "- we usually try to sell %s months at least!\n" % min_maintenance_months

        
#        if maintenance_start_date and maintenance_month_qty:
#            date = (DateTime.strptime(maintenance_start_date, '%Y-%m-%d') + DateTime.RelativeDateTime(months=maintenance_month_qty)).strftime('%Y-%m-%d')
#            result['value'] = {'maintenance_end_date': date}

        if maintenance_product_qty and maintenance_month_qty: #only set the default fleet at init
            result['value'].update({'product_uom_qty': maintenance_product_qty * maintenance_month_qty})
            
        if len(warning_messages) > 1:
            result['warning'] = {'title': 'Maintenance Dates Warning', 'message': warning_messages}
        print result
        return result
    
    
    def _get_maintenance_month_qty_from_start_end(self, cr, uid, start, end):
        return DateTime.RelativeDateDiff(end + RelativeDateTime(days=fixed_days_before_month_end + 1), start).months
    
    
    def _get_end_date_from_start_date(self, cr, uid, start_date, sub_fleet_id):#, order_sub_fleet_id):
        #sub_fleet_id = sub_fleet_id or order_sub_fleet_id
        print "***"
        print sub_fleet_id
        print "-- 1"
        sub_fleet = self.pool.get('stock.location').browse(cr, uid, sub_fleet_id)
        print sub_fleet
        print "2"
        year = start_date.year
        anniversary_time = DateTime.strptime(sub_fleet.anniversary_time, '%Y-%m-%d')
        print anniversary_time
        month = anniversary_time.month
        day = anniversary_time.days_in_month - fixed_days_before_month_end
        end = DateTime.DateTime(year, month, day, 0, 0, 0.0)
        print "3"
        maintenance_month_qty = DateTime.RelativeDateDiff(end + RelativeDateTime(days=fixed_days_before_month_end + 1), start_date).months
        print "4"
        if maintenance_month_qty < min_maintenance_months:
            print "5"
            end = DateTime.DateTime(year + 1, month, day, 0, 0, 0.0)
        print end
        return end
    
    
    def fleet_id_change(self, cr, uid, ids, order_fleet_id=False, fleet_id=False, product_id=False, maintenance_start_date=False):
        result = {}
        result['value'] = {}
        fleet_id = order_fleet_id or fleet_id
        if fleet_id:
            if not product_id: #only set the default fleet at init
                result['value'] = {'fleet_id': fleet_id}
            
            #retrieve the maintenance anniversary from fleet
            #TODO only for maintenance product?
            if maintenance_start_date:
                print "f1"
                start = DateTime.strptime(maintenance_start_date, '%Y-%m-%d')
                print "f2"
                end_date = self._get_end_date_from_start_date(cr, uid, start, fleet_id)
                result['value'].update({'maintenance_end_date': end_date.strftime('%Y-%m-%d')})
                result['value'].update({'maintenance_month_qty': self._get_maintenance_month_qty_from_start_end(cr, uid, start, end_date)})
        return result
    
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging)
        
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            if product_obj.is_maintenance:
                result['value'].update({'is_maintenance': True})
            else:
                result['value'].update({'is_maintenance': False})
            #result['value'].update({'product_type': product_obj.type})
        return result
    
    
    #deal with invoice on order
    def invoice_line_create(self, cr, uid, ids, context={}):
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        i = 0
        for line in self.browse(cr, uid, ids, context):
            self.pool.get('account.invoice.line').write(cr, uid, [create_ids[i]], {'maintenance_start_date':line.maintenance_start_date, \
                                                                                   'maintenance_end_date':line.maintenance_end_date, \
                                                                                   'maintenance_month_qty':line.maintenance_month_qty, \
                                                                                   'maintenance_product_qty':line.maintenance_product_qty, \
                                                                                   })
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
            if order_line.product_id.is_maintenance or order_line.product_id.type == 'product':
                if order_line.fleet_id and order_line.fleet_id.is_sub_fleet and order_line.fleet_id.location_id.partner_id == order_line.order_id.partner_id:
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
        'maintenance_start_date': default_maintenance_start_date
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