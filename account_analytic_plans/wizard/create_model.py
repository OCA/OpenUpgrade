import wizard
import time
import netsvc
import pooler

info = '''<?xml version="1.0"?>
<form string="Distribution Model Saved">
	<label string="This distribution model has been saved.\nYou will be able to reuse it later."/>
</form>'''

def activate(self, cr, uid, data, context):
	plan_obj = pooler.get_pool(cr.dbname).get('account.analytic.plan.instance')
	plan = plan_obj.browse(cr, uid, data['id'], context)
	if (not plan.name) or (not plan.code):
		raise wizard.except_wizard('Error', 'Please put a name and a code before saving the model !')
	pids = plan_obj.search(cr, uid, [('name','=',plan.name),('code','=',plan.code),('plan_id','<>',False)], context)
	if pids:
		raise wizard.except_wizard('Error', 'A model having this name and code already exist !')
	pids  =  pooler.get_pool(cr.dbname).get('account.analytic.plan').search(cr, uid, [], context=context)
	if (not pids):
		raise wizard.except_wizard('Error', 'No analytic plan defined !')
	plan_obj.write(cr,uid,[data['id']],{'plan_id':pids[0]})
	return 'info'


class create_model(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type':'action','action':activate,'state':'info'}
				},
		'info': {
			'actions': [],
			'result': {'type':'form', 'arch':info, 'fields':{}, 'state':[('end','OK')]}
		},
	}
create_model('create.model')


