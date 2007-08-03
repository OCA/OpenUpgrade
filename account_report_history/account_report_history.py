import time
from osv import fields
from osv import osv
import netsvc
import pooler
from mx import DateTime


class account_report_history(osv.osv):


    def _calc_value(self, cr, uid, ids, name, args, context):
        acc_report_id=self.read(cr,uid,ids,['tmp','period_id'])
        tmp_ids={}
        for a in acc_report_id:
            period_id=pooler.get_pool(cr.dbname).get('account.period').search(cr,uid,[('name','=',a['period_id'])])[0]
            tmp_ids[a['id']] = pooler.get_pool(cr.dbname).get('account.report.report')._amount_get(cr,uid,[a['tmp']],'amount',(),{'periods':range((period_id-((period_id%12)-1)),period_id+1)}).values()[0]
        return tmp_ids

    _name = "account.report.history"
    _description = "Indicator"
    _table = "account_report"
    _auto = False
    _order='name'
    _columns = {
        'period_id': fields.char('Period',size=64, readonly=True, select=True),
        'fiscalyear_id': fields.char('Fiscal Year', size=64, readonly=True, select=True),
        'name': fields.char('Indicator', size=(64), readonly=True, select=True),
        'val': fields.function(_calc_value, method=True, string='Value', readonly=True),
        'tmp' : fields.integer(string='temp',readonly=True)
    }

    def init(self, cr):

        cr.execute('''create or replace view account_report as (select ar.id as tmp,((pr.id*100000)+ar.id) as id,ar.name as name,pr.name as period_id,af.name as fiscalyear_id from account_report_report as ar cross join account_period as pr cross join account_fiscalyear af group by af.name,ar.name,pr.name,pr.id,ar.id)''')

account_report_history()