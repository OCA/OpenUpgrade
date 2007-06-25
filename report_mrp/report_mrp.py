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

class report_in_out_picking(osv.osv):
    _name="report.in.out.picking"
    _description="Workcenter Load"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_qty': fields.float('Quantity (UOM)', required=True),
        'd_name': fields.char('Location Name', size=64, required=True),
        'd_id': fields.many2one('stock.location', 'Dest. Location', required=True),

       }
    def init(self, cr):
        cr.execute("""
            create or replace view report_in_out_picking as (
                select
                    m.id as id,
                    m.name as name ,
                    m.location_dest_id as d_id,
                    sum(m.product_qty) as product_qty,
                    l.name as d_name
                from
                    stock_move m ,
                    stock_location l,
                    stock_picking p
                where
                    m.location_dest_id=l.id and m.picking_id=p.id and p.type='internal'
                group by m.id,m.name,l.name,m.location_dest_id


            )""")
report_in_out_picking()
