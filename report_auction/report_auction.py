from osv import fields,osv

class report_per_seller_customer(osv.osv):
        _name = "report.per.seller.customer"
        _description = "Next production order"
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
        _description = "Next production order"
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
                   limit 4

                  )""")
report_latest_doposit()