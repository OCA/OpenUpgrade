from osv import fields,osv

class report_commission_month(osv.osv):
    _name = "report.commission.month"
    _description = "Commission of month"
    _auto = False
    _columns = {
        'name': fields.char('Salesagent Name',size=64, readonly=True),
        'sono':fields.integer('Sales Order No', readonly=True),
        'invno':fields.integer('Invice Number', readonly=True),
        'inv_total':fields.integer('Invioce Total', readonly=True),
        'in_date': fields.date('Date of Invoice', readonly=True),
        'comrate': fields.float('CommmissionRate(%)', readonly=True),
        'commission': fields.float('Commission of sales agent', readonly=True),
        'state': fields.char('Invoice State', size=64,readonly=True),
        'pdate': fields.date('Invoice Paid Date', readonly=True),

    }
    _order = 'name,sono,state'

    def init(self, cr):
        print "In init of commision month ..";
        cr.execute(""" create or replace view report_commission_month as (select min(A.id) as id,A.name as name,S.name as sono,I.number as invno
              ,(L.quantity * L.price_unit) as inv_total,substring(I.date_invoice for 10) as in_date,
              ((1-R.price_discount)*100) as comrate,((sum(L.quantity * L.price_unit)*(1-R.price_discount)))
              as commission,I.state from


sale_agent A,
res_partner P,
account_invoice I,
product_pricelist_item R,
account_invoice_line L,
sale_order_line SL,
product_pricelist_version PV,
sale_order S,
product_pricelist PP where
R.price_version_id=PV.id AND A.comprice_id = PV.pricelist_id AND I.origin=S.name AND SL.order_id=s.id AND R.price_discount > 0 AND S.partner_id = P.id AND P.agent_id=A.id AND I.partner_id=P.id AND I.id=L.invoice_id
group by L.quantity , L.price_unit,R.price_discount,I.state,I.id,A.name,P.name,I.state,I.date_invoice,
S.name,I.number,A.id
) """)
report_commission_month()

