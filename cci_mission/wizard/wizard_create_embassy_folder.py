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
import netsvc

preform = """<?xml version="1.0"?>
<form string="Choose Site">
    <field name="site_id" width="400"/>
</form>
"""
prefields = {
    'site_id': {'string':'Site', 'type':'many2one', 'relation':'cci_missions.site' ,'required':True},
          }

form = """<?xml version="1.0"?>
<form string="Create Embassy Folder">
    <field name="folder_created"/>
    <newline />
    <field name="folder_rejected"/>
    <newline />
    <field name="folder_rej_reason" width="400"/>
</form>
"""
fields = {
    'folder_created': {'string':'Embassy Folder Created', 'type':'char', 'readonly':True},
    'folder_rejected': {'string':'Embassy Folder Rejected', 'type':'char', 'readonly':True},
    'folder_rej_reason': {'string':'Error Messages', 'type':'text', 'readonly':True},
          }
def _create_embassy_folder(self, cr, uid, data, context):
    site_id = data['form']['site_id']
    obj_pool = pooler.get_pool(cr.dbname)
    obj_dossier = obj_pool.get(data['model'])
    data_dossier = obj_dossier.browse(cr,uid,data['ids'])
    list_folders = []
    folder_create = 0
    folder_reject = 0
    folder_rej_reason = ""
    for data in data_dossier:
        if data.embassy_folder_id:
            folder_reject = folder_reject + 1
            folder_rej_reason += "ID "+str(data.id)+": Already Has an Embassy Folder Linked. \n"
            continue
        folder_create = folder_create + 1
        folder_id =obj_pool.get('cci_missions.embassy_folder').create(cr, uid, {
                    'site_id': site_id,
                    'partner_id': data.order_partner_id.id,
                    'destination_id': data.destination_id.id,
            })

        list_folders.append(folder_id)
        obj_dossier.write(cr, uid,data.id, {'embassy_folder_id' : folder_id})
    return {'folder_created' : str(folder_create) , 'folder_rejected' : str(folder_reject) , 'folder_rej_reason': folder_rej_reason , 'folder_ids' : list_folders }

class create_embassy_folder(wizard.interface):
    def _open_folder(self, cr, uid, data, context):
        mission_datas = pooler.get_pool(cr.dbname).get('cci_missions.embassy_folder').read(cr,uid,data['form']['folder_ids'],fields=['crm_case_id'])
        crm_ids = ','.join([str(x['crm_case_id'][0]) for x in mission_datas if x['crm_case_id'] and x['crm_case_id'][0]])
        val = {
            'domain': "[('id','in', ["+crm_ids+"])]",
            'name': 'Folder',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cci_missions.embassy_folder',
            'view_id': False,
            'context' : "{}",
            'type': 'ir.actions.act_window'
            }
        return val

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' ,   'arch' : preform,
                    'fields' : prefields,
                    'state' : [('end','Cancel'),('go','Next')]}
        },
        'go' : {
            'actions' : [_create_embassy_folder],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Ok'),('open','Open')]}
        },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_folder, 'state':'end'}
        }
    }

create_embassy_folder("cci_mission.create_embassy_folder")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

