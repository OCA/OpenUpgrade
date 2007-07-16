

import wizard
import netsvc
import ir
import pooler


cancel_form = """<?xml version="1.0"?>
<form string="Cancel Order">
	<label string="Are you sure you want to cancel this order ?"/>
</form>"""



cancel_fields = {
}


def _cancel(self,cr,uid,data,context):

    #print pooler.get_pool(cr.dbname).get('lunch.order').read(cr,uid,data['ids'],['cashmove'])
    #print pooler.get_pool(cr.dbname).get('lunch.order').browse(cr,uid,data['ids'])
            
    return pooler.get_pool(cr.dbname).get('lunch.order').lunch_order_cancel(cr,uid,data['ids'],context)

##def _cancel(self,cr,uid,data,context):
##    ref_order=pooler.get_pool(cr.dbname).get('lunch.order')
##
##    for ref in ref_order.browse(cr,uid,data['ids']):
##        if not ref.cashmove: continue
##        ref_order.unlink(cr, uid, [ref.cashmove.id])
##
##    ref_order.write(cr,uid, data['ids'], {'state':'draft'})
##    return {}


    

    
class order_cancel(wizard.interface):


	states = {
		'init': {
			'actions': [],
			'result': {'type':'form', 'arch':cancel_form, 'fields':cancel_fields, 'state':[('end','No'),('cancel','Yes')]}
		},
		'cancel': {
			'actions': [_cancel],
			'result': {'type':'state', 'state':'end'}
		}
	}
order_cancel('lunch.order.cancel')

