from osv import fields,osv
import tools
import ir
import pooler
from mx.DateTime import RelativeDateTime, DateTime, localtime, RelativeDateTimeDiff
import time
from mx import DateTime

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line" 
    _columns = {
        'maintenance_month_qty': fields.float('Maintenance Month Quantity', required=False),
        'maintenance_product_qty': fields.float('Maintenance Product Quantity', required=False), 
        'fleet_id': fields.many2one('stock.location', 'Fleet'),
        'maintenance_start_date':fields.date('Maintenance Start Date', required = False),
        'maintenance_end_date':fields.date('Maintenance End Date', required = False),
        'is_maintenance': fields.related('product_id', 'is_maintenance', type='boolean', string='Is Maintenance'),
        'account_analytic_lines': fields.one2many('account.analytic.line', 'invoice_line_id', 'Analytic Lines'),
    }
        
account_invoice_line()

class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'
    
    _columns = {
        'invoice_line_id':fields.many2one('account.invoice.line', 'Invoice Line'),
    }
    
account_analytic_line()


class account_move_line(osv.osv):
    _inherit="account.move.line"
    
#    def create(self, cr, uid, vals, context={}):
#        import traceback
#        traceback.print_stack
#        print vals
#        raise 'e'

    def create_analytic_lines(self, cr, uid, ids, context={}):
        super(account_move_line, self).create_analytic_lines(cr, uid, ids, context)
        for move_line in self.browse(cr, uid, ids, context):
            print "--------"
            print move_line
            if move_line.analytic_lines and len(move_line.analytic_lines) == 1: #TODO and product maintenance
                print move_line
                analytic_line = move_line.analytic_lines[0] #we assume their is only one analytic line for a maintenance product
                
                
                for invoice_line in move_line.invoice_id.invoice_line:
                    if invoice_line.product_id and invoice_line.product_id.is_maintenance:
                        #TODO
    
                    
                        #TODO ca ne tient pas compte du maintenance_qty, or tres important
                        month_qty = int(analytic_line.unit_amount)
                        splitted_amount = float(analytic_line.amount) / float(month_qty)
                        print "product_qty:"
                        print month_qty
                        
                        start_date = DateTime.now() #TODO pick from invoice line!!!
                        
                        self.pool.get('account.analytic.line').write(cr, uid, analytic_line.id, {'date':start_date, 'unit_amount':1, 'amount':splitted_amount})
                        
                        for i in range(1, month_qty):
                            start_date += DateTime.RelativeDateTime(months=1)
                            self.pool.get('account.analytic.line').copy(cr, uid, analytic_line.id, {'date': start_date}) #TODO check month_qty
                    

                
                
        return True
                

account_move_line()


#class account_invoice(osv.osv):
#    
#    
#    def action_move_create(self, cr, uid, ids, *args):
#        # first run parent method which will create analytic lines based on _get_analytic_lines and GL account moves
#        print "eeeeeeeeeeeeeeeee"
#        print ids
#        moves = super(account_invoice, self).action_move_create(cr, uid, ids, args)
#        for move in moves:
#            if move['analytic_lines'] and len(move['analytic_lines']) == 1: #TODO and product maintenance
#                #TODO ca ne tient pas compte du maintenance_qty, or tres important
#                month_qty = int(move['analytic_lines'][0][2]['unit_amount'])
#                move['analytic_lines'][0][2]['amount'] = float(move['analytic_lines'][0][2]['amount']) / float(month_qty)
#                for i in range(1, month_qty):
#                    move['analytic_lines'].append(il['analytic_lines'][0])
#                    self.pool.get('stock.move').write(cr, uid, move.id, {'location_dest_id':order_line.fleet_id.id})
#            print il
#            print "---"
#        print result
#        return result
#        
#
#
#     #TODO sert a rien
#    def _get_analytic_lines(self, cr, uid, id):
#        inv = self.browse(cr, uid, [id])[0]
#        cur_obj = self.pool.get('res.currency')
#
#        company_currency = inv.company_id.currency_id.id
#        if inv.type in ('out_invoice', 'in_refund'):
#            sign = 1
#        else:
#            sign = -1
#
#        iml = super(account_invoice, self)._get_analytic_lines(cr, uid, id)
#        print iml
#        print "WE WILL RULE THE WORLD!!!!!!!"
#        
#        for il in iml:
#            #TODO tester si le produit est de type maintenance
#            if il['analytic_lines'] and len(il['analytic_lines']) == 1: #and product maintenance
#                #TODO ca ne tient pas compte du maintenance_qty, or tres important
#                month_qty = int(il['analytic_lines'][0][2]['unit_amount'])
#                il['analytic_lines'][0][2]['amount'] = float(il['analytic_lines'][0][2]['amount']) / float(month_qty)
#                for i in range(1, month_qty):
#                    il['analytic_lines'].append(il['analytic_lines'][0])
#            print il
#            print "---"
#            print il['analytic_lines']
#            #TODO 
#            
#        print iml
#            
#        return iml
#        
#
#account_invoice()