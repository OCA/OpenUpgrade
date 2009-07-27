import wizard
import netsvc
import pooler

take_form = """<?xml version="1.0"?>
<form title="Confirm">
    <separator string="Repeat lines" colspan="4"/>
    <newline/>
</form>
"""

take_fields = {
#    'confirm_en': {'string':'Catalog Number', 'type':'integer'},
}
def _repeat_line(self,cr,uid,data,context={}):
    res={}
    pool = pooler.get_pool(cr.dbname)
#    pool.get('labo.sample').write(cr,uid,data['ids'],{'sample_id':True})
    return {}

class repeate_line_of_request(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {
                    'type' : 'form',
                    'arch' : take_form,
                    'fields' : take_fields,
                    'state' : [('end', 'Cancel'),('repeat', 'Repeat ')]}
        },
            'repeat' : {
            'actions' : [_repeat_line],
            'result' : {'type' : 'state', 'state' : 'end'}
        },
}
repeate_line_of_request('request.line.repeat')
