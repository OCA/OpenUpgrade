# -*- encoding: utf-8 -*-
import wizard
import pooler

class wizard_proposition_products(wizard.interface):

    new_prices_prog = '''<?xml version="1.0"?>
    <form string="Select Prices Progression">
        <field name="prices_progression" colspan="4"/>
    </form>'''
    
    prices_prog_form = '''<?xml version="1.0"?>
    <form string="Create Group">
        <field name="prices_progression" colspan="4"/>
    </form>'''
    
    message ='''<?xml version="1.0"?>
    <form string="Create Prices Progression">
        <label align="0.0" colspan="4" string="test"/>
    </form>'''
    
    error_message = '''<?xml version="1.0"?>
    <form string="Error!!!">
        <label align="0.0" colspan="4" string="error test"/>
    </form>'''
    
    def _select_prices_prog(self, cr, uid, data, context):

        """
        if context.has_key('group_id'):
            group_id = context['group_id']
        else :
            group_id = data['form']['group']
        pool=pooler.get_pool(cr.dbname)
        camp_obj = pool.get('dm.campaign')
        for r in camp_obj.browse(cr,uid,data['ids']):
            if not r.campaign_group_id:
                camp_obj.write(cr,uid,r.id,{'campaign_group_id':group_id})
        """
        return {}

    def _new_prices_prog(self, cr, uid, data, context):
        pool=pooler.get_pool(cr.dbname)
        group_id = pool.get('dm.campaign.group').create(cr,uid,{'name':data['form']['group']})
        context['group_id'] = group_id
        self._add_group(cr,uid,data,context)
        return {}

    def _get_prices_progs(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        prices_prog_obj=pool.get('dm.campaign.proposition.prices_progression')
        ids=prices_prog_obj.search(cr, uid, [])
        res=[(prices_prog.id, prices_prog.name) for prices_prog in prices_prog_obj.browse(cr, uid, ids)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res

    def _next(self, cr, uid, data, context):
        if not data['form']['prices_progression']:
            return 'error'
        return 'select'


    prices_prog_fields = {
                    
        'prices_progression': {'string': 'Select Prices Progression', 'type': 'selection', 'selection':_get_prices_progs, }
        
        }
    
    new_prices_prog_fields = {
        'prices_progression': {'string': 'Prices Progression Name', 'type': 'char', 'size':64, 'required':True }
        }    
    
    states = {
        'init': {
            'actions': [],
#            'result': {'type':'form', 'arch':prices_prog_form, 'fields':prices_prog_fields, 'state':[('end','Cancel'),('name_prices_prog','Create New Prices Progression'),('next','Select Prices Progression'),]}
            'result': {'type':'form', 'arch':prices_prog_form, 'fields':prices_prog_fields, 'state':[('end','Cancel'),('next','Select Prices Progression'),]}
            },
        'name_prices_prog': {
            'actions': [],
            'result': {'type':'form', 'arch':new_prices_prog, 'fields':new_prices_prog_fields, 'state':[('end','Cancel'),('new','Create Prices Progression')]}
            },
        'new': {
            'actions': [_new_prices_prog],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        'next': {
            'actions': [],
            'result': {'type': 'choice', 'next_state': _next}
        },
        'error': {
            'actions': [],
            'result': {'type': 'form', 'arch': error_message, 'fields':{} ,'state': [('end','Cancel'),('init','Select Prices Progression')]}
        },        
        'select': {
            'actions': [_select_prices_prog],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        }
wizard_proposition_products("wizard_proposition_products")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
