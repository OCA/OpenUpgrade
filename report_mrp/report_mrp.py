from osv import fields,osv

class report_next_production_order(osv.osv):
    _name = "report.next.production.order"
    _description = "Next production order"
    _auto = False
    _columns = {
       'name': fields.char('Name', size=64, required=True),
       'priority': fields.selection([('0','Not urgent'),('1','Normal'),('2','Urgent'),('3','Very Urgent')], 'Priority'),
       'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('type','<>','service')]),
       'product_qty': fields.float('Product Qty', required=True),
       'date_planned': fields.date('Planned date', required=True),
       'state': fields.selection([('draft','Draft'),('picking_except', 'Picking Exception'),('confirmed','Waiting Goods'),('ready','Ready to Produce'),('in_production','In Production'),('cancel','Canceled'),('done','Done')],'State', readonly=True)

    }
#    _order = 'date_planned desc, priority desc';
    def init(self, cr):
        cr.execute("""
            create or replace view report_next_production_order as (
                select
                    l.id as id,
                    l.name as name,
                    l.priority as priority,
                    l.product_id as product_id,
                    l.product_qty as product_qty,
                    l.date_planned as date_planned,
                    l.state as state
                from
                   mrp_production  l

            )""")
report_next_production_order()
class report_procurement_exception(osv.osv):
    _name = "report.procurement.exception"
    _description = "Procurement Exception"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'origin': fields.char('Origin', size=64),
        'priority': fields.selection([('0','Not urgent'),('1','Normal'),('2','Urgent'),('3','Very Urgent')], 'Priority', required=True),
        'date_planned': fields.date('Date Promised', required=True),
        'date_close': fields.date('Date Closed'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Quantity', required=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'move_id': fields.many2one('stock.move', 'Reservation', ondelete='cascade'),
        'close_move': fields.boolean('Close Move at end', required=True),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'procure_method': fields.selection([('make_to_stock','from stock'),('make_to_order','on order')], 'Procurement Method', states={'draft':[('readonly',False)], 'confirmed':[('readonly',False)]}, readonly=True),

        'purchase_id': fields.many2one('purchase.order', 'Purchase Order'),
        'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Order Line'),

        'property_ids': fields.many2many('mrp.property', 'mrp_procurement_property_rel', 'procurement_id','property_id', 'Properties'),

        'message': fields.char('Latest error', size=64),
        'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('exception','Exception'),('running','Running'),('cancel','Cancel'),('done','Done')], 'State')
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_procurement_exception as (
                select
                    l.id as id,
                    l.name as name,
                    l.origin as origin,
                    l.priority as priority,
                    l.product_id as product_id,
                    l.product_qty as product_qty,
                    l.date_planned as date_planned,
                    l.date_close as date_close ,
                    l.move_id as move_id,
                    l.state as state,
                    l.location_id as location_id,
                    l.procure_method as procure_method,
                    l.close_move as close_move,
                    l.purchase_id as purchase_id,
                    l.product_uom as product_uom,
                    l.purchase_line_id as purchase_line_id,
                    l.message as message
                from
                   mrp_procurement  l

            )""")

report_procurement_exception()

class report_deliveries_outpicking(osv.osv):
    _name = "report.deliveries.outpicking"
    _description = "Deliveries Outpicking"
    _auto=False
    _columns = {
        'name': fields.char('Picking Name', size=64, required=True, select=True),
        'origin': fields.char('Origin', size=64),
        'type': fields.selection([('out','Sending Goods'),('in','Getting Goods'),('internal','Internal')], 'Shipping Type', required=True, select=True),
        'active': fields.boolean('Active'),
        'note': fields.text('Notes'),

        'location_id': fields.many2one('stock.location', 'Location'),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location'),

        'move_type': fields.selection([('direct','Direct Delivery'),('one','All at once')],'Delivery Method', required=True),
        'state': fields.selection([
            ('draft','draft'),
            ('auto','waiting'),
            ('confirmed','confirmed'),
            ('assigned','assigned'),
            ('done','done'),
            ('cancel','cancel'),
            ], 'State', readonly=True),
        'date':fields.datetime('Date create'),

        'move_lines': fields.one2many('stock.move', 'picking_id', 'Move Lines'),

        'auto_picking': fields.boolean('Auto-Picking'),
        'work': fields.boolean('Work todo'),
        'loc_move_id': fields.many2one('stock.location', 'Move to Location'),
        'address_id': fields.many2one('res.partner.address', 'Partner'),
        'lot_id': fields.many2one('stock.lot', 'Consumer Lot Created'),
        'move_lot_id': fields.many2one('stock.move.lot', 'Moves Created'),
        'invoice_state':fields.selection([
            ("invoiced","Invoiced"),
            ("2binvoiced","To be invoiced"),
            ("none","No invoice")], "Invoice state"),
        }
    #    def init(self, cr):
#        cr.execute("""
#            create or replace view report_deliveries_outpicking as (
#                select
#                    l.id as id,
#                    l.name as name,
#                    l.origin as origin,
#                    l.location_id as location_id,
#                    l.state as state
#
#                from
#                   stock_picking  l
#
#            )""")


report_deliveries_outpicking()

class report_workcenter_load(osv.osv):
    _name="report.workcenter.load"
    _description="Workcenter Load"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter', required=True),
        'cycle': fields.float('Nbr of cycle'),
        'hour': fields.float('Nbr of hour'),
        'sequence': fields.integer('Sequence', required=True),
        'production_id': fields.many2one('mrp.production', 'Production Order', select=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_workcenter_load as (
                SELECT
                    SUM(mrp_production_workcenter_line.hour) AS hour,
                    SUM(mrp_production_workcenter_line.cycle) AS cycle,
                    mrp_workcenter.name AS name,
                    mrp_workcenter.id AS id
                FROM mrp_production_workcenter_line, mrp_production, mrp_workcenter
                WHERE (mrp_production_workcenter_line.production_id=mrp_production.id)
                AND (mrp_production_workcenter_line.workcenter_id=mrp_workcenter.id)
                GROUP BY mrp_production_workcenter_line.workcenter_id, mrp_workcenter.name, mrp_workcenter.id

            )""")
report_workcenter_load()
