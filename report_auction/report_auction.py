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
                        l.id as id
                        l.name as name,
                        l.partner_id as partner_id
                    from auction_deposit l
                  )""")



report_per_seller_customer()