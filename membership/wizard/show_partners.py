import wizard
import pooler
import time
import datetime

form = """<?xml version="1.0"?>
<form string="Select Crtiteria For Partners" colspan="4">
    <field name="select" />
</form>
"""

fields = {
    'select':{'string':'Select Criteria','type':'selection','selection':[('lines', 'Entry Lines'),('crm','Cases Sections and State')]},
}

lines_form = """<?xml version="1.0"?>
<form string="Select Crtiteria For Partners-Entry Lines" colspan="4">
    <field name="date_from" />
    <field name="date_to" />
    <field name="amount" />
    <field name="member_state" colspan="4" />
</form>
"""

lines_fields = {
    'date_from': {'string':'Start of period', 'type':'date', 'required':True},
    'date_to': {'string':'End of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'amount': {'string':'Amount', 'type':'float', 'required':True, 'default': lambda *a: 0.0},
    'member_state':{'string':'Current Membership state','type':'selection','selection':[('none', 'Non Member'),('canceled','Canceled Member'),('old','Old Member'),('waiting','Waiting Member'),('invoiced','Invoiced Member'),('associated','Associated Member'),('free','Free Member'),('paid','Paid Member')],'required':True},
}


crm_form = """<?xml version="1.0"?>
<form string="Select Crtiteria For Partners-CRM cases and sections" colspan="4">
    <field name="section" />
    <field name="state" />
</form>
"""

crm_fields = {
     'section': {'string': 'Section', 'type': 'many2one', 'relation': 'crm.case.section','required':True},
     'state':{'string':'State','type':'selection','selection':[('draft','Draft'),('open','Open'),('cancel', 'Cancel'),('done', 'Close'),('pending','Pending')],'required':True},
}


class show_partners(wizard.interface):

    def _defaults(self, cr, uid, data, context):
        data['form']['select']='lines'
        return data['form']

    def _defaults_lines(self, cr, uid, data, context):
        today=datetime.datetime.today()
        from_date=today-datetime.timedelta(30)
        data['form']['date_from'] = from_date.strftime('%Y-%m-%d')
        data['form']['member_state']='free'
        return data['form']

    def _defaults_crm(self, cr, uid, data, context):
        data['form']['state']='open'
        return data['form']

    def _check(self, cr, uid, data, context):
        if data['form']['select']=='crm':
            return 'crm'
        else:
            return 'entry_lines'


    def _open_window_selected_partners(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'base', 'action_partner_form')
        list_ids=[]

        if data['form']['select']=='lines':
            cr.execute("select distinct(partner_id) from account_move_line where credit>=%f and (date between to_date(%s,'yyyy-mm-dd') and to_date(%s,'yyyy-mm-dd')) and (partner_id is not null)",(data['form']['amount'],data['form']['date_from'],data['form']['date_to']))
            entry_lines = cr.fetchall()

            entry_ids=[x[0] for x in  entry_lines]
            a_id = pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, entry_ids, ['membership_state'])

            for i in range(0,len(a_id)):
                if a_id[i]['membership_state']==data['form']['member_state']:
                    list_ids.append(a_id[i]['id'])
        else:
            cr.execute("select distinct(partner_id),section_id,state from crm_case where section_id=%d and state=%s and (partner_id is not null)",(data['form']['section'],data['form']['state']))
            p_ids=cr.fetchall()
            list_ids=[x[0] for x in p_ids]


        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id])[0]
        result['domain'] = [('id', 'in', list_ids)]
#        result['context'] = ({'id': entry_ids})
        return result

    states = {
        'init' : {
            'actions' : [_defaults],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Cancel'),('go','Go')]}
        },
        'go': {
            'actions': [],
            'result': {'type':'choice','next_state':_check}
        },
        'entry_lines': {
            'actions': [_defaults_lines],
            'result': {'type':'form','arch':lines_form,'fields':lines_fields,'state':[('end','Cancel'),('choose','Choose')]}
        },
        'crm': {
            'actions': [_defaults_crm],
            'result': {'type':'form','arch':crm_form,'fields':crm_fields,'state':[('end','Cancel'),('choose','Choose')]}
        },
        'choose': {
            'actions': [],
            'result': {'type': 'action', 'action':_open_window_selected_partners, 'state':'end'}
        }

    }
show_partners("membership_show_partners")
