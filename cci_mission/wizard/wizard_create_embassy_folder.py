import wizard
import pooler
import netsvc
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
    'folder_created': {'string':'Folder Created', 'type':'char', 'readonly':True},
    'folder_rejected': {'string':'Folder Rejected', 'type':'char', 'readonly':True},
    'folder_rej_reason': {'string':'Error Messages', 'type':'text', 'readonly':True},
          }
def _create_embassy_folder(self, cr, uid, data, context):
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
            folder_rej_reason += "ID "+str(data.id)+": Already Has an Folder Linked \n"
            continue
        folder_create = folder_create + 1
        folder_id =obj_pool.get('cci_missions.embassy_folder').create(cr, uid, {
                    'name': data.name,
                    'date': data.date,
                    'partner_id': data.order_partner_id.id,
                    'destination_id': data.destination_id.id,
                    'invoice_note' : data.text_on_invoice
            })
        list_folders.append(folder_id)
        obj_dossier.write(cr, uid,data.id, {'embassy_folder_id' : folder_id})
    return {'folder_created' : str(folder_create) , 'folder_rejected' : str(folder_reject) , 'folder_rej_reason': folder_rej_reason }

class create_embassy_folder(wizard.interface):

    states = {
        'init' : {
            'actions' : [_create_embassy_folder],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Ok')]}
        },
    }

create_embassy_folder("cci_mission.create_embassy_folder")
