import wizard
import time
import netsvc
import pooler

info = '''<?xml version="1.0"?>
<form string="info">
    <label string="The model has been saved. You will be able to reuse this model."/>
</form>'''

form1 = '''<?xml version="1.0"?>
<form string="Create Model">
    <label string="Activate the model?"/>
</form>'''

def activate(self, cr, uid, data, context):
        print "data:::",data
        pooler.get_pool(cr.dbname).get('account.analytic.plan.instance').write(cr,uid,data['ids'],{'model':True})
        return 'info'


class create_model(wizard.interface):


    states = {

       'init': {
            'actions': [],
            'result': {'type':'form','arch':form1, 'fields':{}, 'state':[('end','No'),('yes','Yes')]}
        },

        'yes': {
            'actions': [],
            'result': {'type':'action','action':activate,'state':'info'}
                },
         'info': {
            'actions': [],
            'result': {'type':'form', 'arch':info, 'fields':{}, 'state':[('end','OK')]}
        },



             }

create_model('create.model')


