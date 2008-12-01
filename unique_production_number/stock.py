from osv import fields, osv
import tools
import ir
import pooler


class stock_move(osv.osv):
    _inherit = "stock.move"

    def _check_unique_product_lot(self, cr, uid, ids):
         for move in self.browse(cr, uid, ids):
             if move.state == 'done' and move.product_id.unique_production_number and move.product_qty > 1:
                return False
         return True

    _columns = {
        'new_prodlot_code': fields.char('Production Tracking Code To Create', size=64),
    }
        
    _constraints = [
        (_check_unique_product_lot,
            """_(The product associated to the move require a unique (per instance) production number, 
            you should split the move assign a different number to every move)""",
            ['prodlot_id'])]
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('new_prodlot_code'):
            if self.pool.get('stock.production.lot').search(cr,uid,[('name', '=', vals['new_prodlot_code'])]):
                raise osv.except_osv(_('Error, newly entered production code already exists !') + " code: %s" % vals['new_prodlot_code'],
                    _('Please assign this product the existing production code or type an other new code'))
            prodlot_id = self.pool.get('stock.production.lot').create(cr, uid, {
                'name': vals['new_prodlot_code'],
                'product_id': vals['product_id'],
            })
            vals['prodlot_id'] = prodlot_id
        return super(stock_move, self).write(cr, uid, ids, vals, context)

    
stock_move()


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        records = super(stock_picking, self).read(cr, uid, ids, fields, context, load)
        for record in records:
            if record.has_key('move_lines'):
                additional_move_lines = []
                for move_id in record['move_lines']:
                    move = self.pool.get('stock.move').browse(cr, uid, move_id, context)
                    if move.product_id.unique_production_number and move.product_qty > 1:
                        while move.product_qty > 1:
                            new_move_id = self.pool.get('stock.move').copy(cr, uid, move.id, {'product_qty': 1, 'state': move.state, 'prodlot_id': None})
                            print new_move_id
                            additional_move_lines.append(new_move_id)
                            move.product_qty -= 1;
                        self.pool.get('stock.move').write(cr, uid, [move.id], {'product_qty': 1})
                
                record['move_lines'] += additional_move_lines
        
        return records
        
stock_picking()