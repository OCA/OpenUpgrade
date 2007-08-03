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
            period_val=pooler.get_pool(cr.dbname).get('account.period').read(cr,uid,[a['period_id'][0]])[0]
            period_id=pooler.get_pool(cr.dbname).get('account.period').search(cr,uid,[('date_start','<=',period_val['date_start']),('fiscalyear_id','=',period_val['fiscalyear_id'][0])])
            tmp_ids[a['id']] = pooler.get_pool(cr.dbname).get('account.report.report').read(cr,uid,[a['tmp']],context={'periods':period_id})[0]['amount']
        return tmp_ids

    _name = "account.report.history"
    _description = "Indicator"
    _table = "account_report"
    _auto = False
    _order='name'
    _columns = {
        'period_id': fields.many2one('account.period','Period', readonly=True, select=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear','Fiscal Year', readonly=True, select=True),
        'name': fields.many2one('account.report.report','Indicator', readonly=True, select=True),
        'val': fields.function(_calc_value, method=True, string='Value', readonly=True),
        'tmp' : fields.integer(string='temp',readonly=True)
    }


    def init(self, cr):

        cr.execute('''create or replace view account_report as (select ar.id as tmp,((pr.id*100000)+ar.id) as id,ar.id as name,pr.id as period_id,pr.fiscalyear_id as fiscalyear_id from account_report_report as ar cross join account_period as pr group by ar.id,pr.id,pr.fiscalyear_id)''')

account_report_history()