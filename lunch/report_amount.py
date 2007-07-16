from osv import fields,osv

class report_lunch_amount(osv.osv):
    
    _name='report.lunch.amount'
    _description = "Amount available by user and box"
    _auto = False
    _columns = {
        'name':fields.char('Name',size=30,required=True),
        'user_cashmove': fields.many2one('res.users','User Name', readonly=True,readonly=True),
        'amount': fields.function(amount_available, method=True, readonly=True, string='Remained Total'),
        'box':fields.many2one('lunch.cashbox','Box Name',size=30,readonly=True),
        }


    
    def init(self, cr):
		cr.execute("""
			create or replace view report_lunch_amount_user as (
				select user_cashmove as user, sum(amount) as sum,box from lunch_cashmove group by user_cashmove, box)""")



report_lunch_amount()
