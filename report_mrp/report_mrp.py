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

class report_source(osv.osv):
    _name="report.source"
    _description="source move"
    _auto = False
    _columns = {
        'date': fields.char('Name', size=64, required=True),
        'sprice': fields.float('Source Move', required=True),

       }
    def init(self, cr):
        cr.execute("""
            create or replace view report_source as (
                select
                    stock_move.id as id,
                    to_char(stock_move.create_date,'YYYY:IW') as date,
                    sum((select product_template.standard_price
                    from product_product inner join product_template on product_product.product_tmpl_id = product_template.id
                    where product_product.id = product_id) * stock_move.product_qty) as sprice
                    from stock_move inner join stock_location on
                        stock_location.id = stock_move.location_id
                        and stock_location.usage = 'internal'
                    where stock_move.state = 'done'
                     group by stock_move.id , stock_move.create_date


            )""")

report_source()

class report_dest(osv.osv):
    _name="report.dest"
    _description="dest move"
    _auto = False
    _columns = {
        'date': fields.char('Name', size=64, required=True),
        'dprice': fields.float('Source Move', required=True),

       }
    def init(self, cr):
        cr.execute("""
            create or replace view report_dest as (
                select
                    stock_move.id as id,
                     to_char(stock_move.create_date,'YYYY:IW') as date,
                    sum((select product_template.standard_price
                    from product_product inner join product_template on product_product.product_tmpl_id = product_template.id
                    where product_product.id = product_id) * stock_move.product_qty) as dprice


                    from stock_move inner join stock_location on
                        stock_location.id = stock_move.location_dest_id
                        and stock_location.usage = 'internal'
                    where stock_move.state = 'done'
                     group by stock_move.id ,stock_move.create_date

            )""")

report_dest()
class report_in_out_picking(osv.osv):
    _name="report.in.out.picking"
    _description="Workcenter Load"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'quantity': fields.float('Quantity (UOM)', required=True),

       }
    def init(self, cr):
        cr.execute("""
            create or replace view report_in_out_picking as (
                   select
                   min(report_dest.id) as id,
                   sum(report_dest.dprice)-sum(report_source.sprice) as quantity,
                   report_dest.date as name
               from report_dest,report_source
               group by name

            )""")
report_in_out_picking()
