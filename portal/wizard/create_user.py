# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import pooler
from random import choice
import string
import tools

first_form = '''<?xml version="1.0"?>
<form string="User creation ">
    <separator string="Create user on portal :" colspan="4"/>
    <newline/>
    <group cols="1" colspan="4">
    <field name="portal_id"/>
    </group>
    <newline/>
    <field name="send_mail"/>   <field name="mail_subject"/>
    <newline/>
    <field name="send_mail_existing"/>  <field name="mail_subject_existing"/>
    <separator colspan="4"/>
    <group cols="1" colspan="4">
    <field name="mail_from"/>
    <newline/>
    <field name="mail"/>
    </group>
</form>'''
first_fields = {
    'portal_id': {'string':'Portal', 'type':'many2one', 'required':True, 'relation': 'portal.portal'},
    'send_mail': {'string':'Send mail for new user', 'type':'boolean',},
    'send_mail_existing': {'string':'Send reminder for existing user', 'type':'boolean', },
    'mail_subject': {'string':'Subject', 'type':'char', 'default':lambda *a: "New user account.","size":256},
    'mail_subject_existing': {'string':'Subject', 'type':'char', 'default':lambda *a: "User account info.","size":256},
    'mail_from': {'string':'From', 'type':'char',"size":256},
    'mail': {'string':'Body', 'type':'text','default':lambda *a: """ Your login: %(login)s, Your password: %(passwd)s
    """},
}

second_form = '''<?xml version="1.0"?>
<form string="User creation">
    <separator string="Results :" colspan="4"/>
    <field name="note" colspan="4" nolabel="1"/>
</form>'''
second_fields = {
    'note' : {'string':'Log','type':'text'}
    }

def genpasswd():
    chars = string.letters + string.digits
    return ''.join([choice(chars) for i in range(6)])


def _create_user(self, cr, uid, data, context):
    pool= pooler.get_pool(cr.dbname)
    portal= pool.get('portal.portal').browse(cr,uid,data['form']['portal_id'])
    user_ref= pool.get('res.users')
    out="login,password\n"
    skipped= 0
    existing= ""
    created= ""
    for partner in pool.get('res.partner').browse(cr,uid,data['ids']):
        for addr in partner.address:
            if not addr.email:
                skipped+= 1
                continue
            user = user_ref.search(cr,uid,[('login',"=",addr.email)])


            if user:
                user = user_ref.browse(cr,uid,user[0])
                existing+= "- %s (Login: %s,  Password: %s)\n"%(user.name,addr.email,user.password)
                mail= data['form']['mail']%{'login':addr.email, 'passwd':user.password}
                if data['form']['send_mail_existing']:
                    if not data['form']['mail_from']: raise wizard.except_wizard('Error !', 'Please provide a "from" email address.')
                    tools.email_send(data['form']['mail_from'],[addr.email] ,data['form']['mail_subject_existing'] ,mail )
                continue

            passwd= genpasswd()
            out+= addr.email+','+passwd+'\n'
            user_ref.create(cr,uid,{'name': addr.name or 'Unknown',
                                    'login': addr.email,
                                    'password': passwd,
                                    'address_id': addr.id,
                                    'action_id': portal.home_action_id and portal.home_action_id.id or portal.menu_action_id.id,
                                    'menu_id': portal.menu_action_id.id,
                                    'groups_id': [(4,portal.group_id.id)],
                                    'company_id': portal.company_id.id,
                                   })
            mail= data['form']['mail']%{'login':addr.email, 'passwd':passwd}
            if data['form']['send_mail']:
                if not data['form']['mail_from']: raise wizard.except_wizard('Error !', 'Please provide a "from" email address.')
                tools.email_send(data['form']['mail_from'],[addr.email] ,data['form']['mail_subject'] ,mail )
            created+= "- %s (Login: %s,  Password: %s)\n"%(addr.name or 'Unknown',addr.email,passwd)

    note= ""
    if created:
        note+= 'Created users:\n%s\n'%(created)
    if existing:
        note+='Already existing users:\n%s\n'%(existing)
    if skipped:
        note+= "%d contacts where ignored (an email address is missing).\n"%(skipped)
    return {'note': note}

class wizard_report(wizard.interface):
    states = {
        'init': {'actions': [],
                 'result': {'type':'form',
                            'arch':first_form,
                            'fields':first_fields,
                            'state':[('end','_Cancel'),('create','_Next')]}
                 },

        'create':{'actions': [_create_user],
               'result': {'type':'form',
                          'arch':second_form,
                          'fields':second_fields,
                          'state':[('end','_Ok')]}
               },

}
wizard_report('portal.create_user')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

