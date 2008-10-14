# -*- encoding: utf-8 -*-
import wizard
import pooler

#msg = ''
#
mailbox_form = """<?xml version="1.0"?>
<form string="Select period">
    <label string="Mail Account Operation" colspan="4"/>  
</form>"""

#
#mailbox_msg = """<?xml version="1.0"?>
#<form string="Select period">
#    <label string="%s" colspan="4"/>
#</form>""" % (msg,)

rename_form ='''<?xml version="1.0"?>
<form string="Rename Folder">
    <field name="old_name" colspan="4"/>
    <field name="new_name" colspan="4"/>
</form>'''

rename_fields = {
    'old_name': {'string': 'Old Name', 'type': 'char', 'size': 64},
    'new_name': {'string': 'New Name', 'type': 'char', 'size': 64}
}

create_form ='''<?xml version="1.0"?>
<form string="Create Folder">
    <field name="folder_name" colspan="4"/>
</form>'''

create_fields = {
    'folder_name': {'string': 'Name', 'type': 'char', 'size': 64},
}

def _create_check(self, cr, uid, data, context):
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')
    mailbox = mailbox_obj.browse(cr, uid, data['ids'][0])
    if mailbox.parent_id:
        raise wizard.except_wizard('Error!', 'Please select Parent Folder')
    return {}

def _check_acc(self, cr, uid, data, context):
    if data['ids'].__len__()>1:
        raise wizard.except_wizard('Error!', 'Please select only one folder')
    return {}

def _delete(self, cr, uid, data, context):
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')
    mailbox = mailbox_obj.browse(cr, uid, data['ids'][0])
    if mailbox.parent_id:
        raise wizard.except_wizard('Error!', 'You can not delete parent folder')
    
    mailbox_obj._delete(cr, uid, data['ids'], context)    
    return {}

def _fill_name(self, cr, uid, data, context):
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')
    mailbox = mailbox_obj.browse(cr, uid, data['ids'][0])
    res = {}
    if mailbox.name:
        res['old_name'] = mailbox.name
    return res

def _create_process(self, cr, uid, data, context):
    name = data['form']['folder_name']
    if not name:
        raise wizard.except_wizard('Error!', 'Please enter folder name')    
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')        
    mailbox_obj.create(cr, uid, data['ids'], context, name)    
    return {}

def _rename_process(self, cr, uid, data, context):
    old_name = data['form']['old_name']
    new_name = data['form']['new_name']
    if not old_name:
        raise wizard.except_wizard('Error!', 'Please enter old folder name')
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')    
    mailbox_obj.rename(cr, uid, data['ids'] , context, old_name, new_name)    
    return {}

class wizard_mailbox(wizard.interface):
            
    states = {       
        'init': {
            'actions': [_check_acc],
            'result': {'type':'form', 'arch':mailbox_form, 'fields':{}, 'state':[('end','Cancel'),('create','Create'),('rename','Rename'),('delete','Delete')]}
        },       
        'create': {
            'actions': [_create_check],
            'result': {'type':'form', 'arch':create_form, 'fields':{},'state':[('end','Cancel'),('create_process','Ok')]}
        },
        'create_process': {
            'actions': [_create_process],
            'result': {'type':'form', 'state':'end'}
        },
        'delete': {
            'actions': [],
            'result': {'type':'form', 'action':_delete, 'state':'end'}
        },
        'rename': {
            'actions': [_fill_name],
            'result': {'type':'form', 'arch':rename_form, 'fields':rename_fields, 'state':[('end','Cancel'),('rename_process','Ok')]}
        },
        'rename_process': {
            'actions': [_rename_process],
            'result': {'type':'form', 'state':'end'}
        },
#        'messsage': {
#            'actions': [],
#            'result': {'type':'form', 'arch':mailbox_msg, 'fields':{},'state':[('end','Ok')]}
#        },
    }
    
wizard_mailbox('webmail.mailbox')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

