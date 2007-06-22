from osv import fields,osv

class report_per_seller_customer(osv.osv):
        _name = "report.per.seller.customer"
        _description = "Customer per seller"
        _auto = False
        _columns = {
                    'name': fields.char('Depositer Inventory', size=64, required=True),
                    'partner_id': fields.many2one('res.partner', 'Seller',relate=True, required=True, change_default=True),
        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_per_seller_customer as (
                    SELECT
                        l.id as id,
                        l.name as name,
                        l.partner_id as partner_id
                    from auction_deposit l
                  )""")
report_per_seller_customer()

class report_latest_doposit(osv.osv):
        _name = "report.latest.doposit"
        _description = "Latest 10 Deposits"
        _auto = False
        _columns = {
            'name': fields.char('Depositer Inventory', size=64, required=True),
            'partner_id': fields.many2one('res.partner', 'Seller', required=True, change_default=True),
            'date_dep': fields.date('Deposit date', required=True),
            'method': fields.selection((('keep','Keep until sold'),('decease','Decrease limit of 10%'),('contact','Contact the Seller')), 'Withdrawned method', required=True),
            'tax_id': fields.many2one('account.tax', 'Expenses'),
            'info': fields.char('Description', size=64),
            'lot_id': fields.one2many('auction.lots', 'bord_vnd_id', 'Objects'),
            'specific_cost_ids': fields.one2many('auction.deposit.cost', 'deposit_id', 'Specific Costs'),
            'total_neg': fields.boolean('Allow Negative Amount'),
        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_latest_doposit as (
                    SELECT
                       l.id as id,
                       l.name as name,
                       l.partner_id as partner_id,
                       l.date_dep as date_dep,
                       l.method as method,
                       l.tax_id as tax_id,
                       l.info as info

                   from auction_deposit l
                   order by l.create_date desc
                   limit 3

                  )""")
report_latest_doposit()

class report_latest_objects(osv.osv):
        _name = "report.latest.objects"
        _description = "Latest 10 Objects"
        _auto = False
        _columns = {
                'partner_id': fields.many2one('res.partner', 'Seller', required=True, change_default=True),
                'auction_id': fields.many2one('auction.dates', 'Auction Date'),
                'bord_vnd_id': fields.many2one('auction.deposit', 'Depositer Inventory', required=True),
                'obj_desc': fields.text('Object Description'),
                'obj_num': fields.integer('Catalog Number'),
                'obj_ret': fields.float('Price retired'),
                'obj_comm': fields.boolean('Commission'),
                'obj_price': fields.float('Adjudication price'),

        }
        def init(self, cr):
            cr.execute("""
                create or replace view report_latest_objects as (
                    SELECT
                       l.id as id,
                       m.partner_id as partner_id,
                       l.auction_id as auction_id,
                       l.obj_desc as obj_desc,
                       l.obj_num as obj_num,
                       l.obj_ret as obj_ret,
                       l.obj_comm as obj_comm,
                       l.obj_price as obj_price

                   from auction_lots l,auction_deposit m
                   where l.bord_vnd_id = m.id
                   order by l.create_date desc
                   limit 3

                  )""")
report_latest_objects()
