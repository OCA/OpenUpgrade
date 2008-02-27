import wizard
import pooler
import time
import datetime

form = """<?xml version="1.0"?>
<form string="Select Crtiteria For Partners" colspan="4">
    <field name="date_from" />
    <field name="date_to" />
    <field name="amount" />
    <field name="member_state" colspan="4" />
</form>
"""

fields = {
    'date_from': {'string':'Start of period', 'type':'date', 'required':True},
    'date_to': {'string':'End of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'amount': {'string':'Amount', 'type':'float', 'required':True, 'default': lambda *a: 0.0},
    'member_state':{'string':'Current Membership state','type':'selection','selection':[('none', 'Non Member'),('canceled','Canceled Member'),('old','Old Member'),('waiting','Waiting Member'),('invoiced','Invoiced Member'),('associated','Associated Member'),('free','Free Member'),('paid','Paid Member')]},
}

class show_partners(wizard.interface):

    def _get_defaults(self, cr, uid, data, context):
        today=datetime.datetime.today()
        from_date=today-datetime.timedelta(30)
        data['form']['date_from'] = from_date.strftime('%Y-%m-%d')
        data['form']['member_state']='free'
        return data['form']

    def _open_window_selected_partners(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'base', 'action_partner_form')
        cr.execute("select distinct(partner_id) from account_move_line where credit>=%f and (date between to_date(%s,'yyyy-mm-dd') and to_date(%s,'yyyy-mm-dd'))",(data['form']['amount'],data['form']['date_from'],data['form']['date_to']))
        entry_lines = cr.fetchall()
        entry_ids=[x[0] for x in  entry_lines]
        a_id = pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, entry_ids, ['membership_state'])

        list_ids=[]
        for i in range(0,len(a_id)):
            if a_id[i]['membership_state']==data['form']['member_state']:
                list_ids.append(a_id[i]['id'])

        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id])[0]
        result['domain'] = [('id', 'in', list_ids)]
#        result['context'] = ({'id': entry_ids})
        return result

    states = {
        'init' : {
            'actions' : [_get_defaults],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Cancel'),('choose','Choose')]}
        },
        'choose': {
            'actions': [],
            'result': {'type': 'action', 'action':_open_window_selected_partners, 'state':'end'}
        }

    }
show_partners("membership_show_partners")
