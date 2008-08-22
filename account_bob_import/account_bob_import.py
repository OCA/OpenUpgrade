from osv import fields, osv
from osv import orm

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def create(self, cr, uid, vals, *args, **kwargs):
        list_lang = []
        ids_lang = self.pool.get('res.lang').search(cr, uid, [])
        lang = self.pool.get('res.lang').browse(cr, uid, ids_lang)
        for l in lang:
            list_lang.append(l.code)
        d= {}
        if 'lang' in vals and not vals['lang'] in list_lang:
            d['lang']=''
            vals.update(d)
        return super(res_partner,self).create(cr, uid, vals, *args, **kwargs)

res_partner()


class config_bob_import(osv.osv_memory):
    _name = 'config.bob.import'
    _columns = {
        'company_id':fields.many2one('res.company','Company', required=True),
        'path':fields.char('Path for BOB Folder',required=True,size=200),
    }

    def action_create(self, cr, uid,ids, context=None):
#        res=self.read(cr,uid,ids)[0]
#        if 'date1' in res and 'date2' in res:
#            res_obj = self.pool.get('account.fiscalyear')
#            start_date=res['date1']
#            end_date=res['date2']
#            name=res['name']#DateTime.strptime(start_date, '%Y-%m-%d').strftime('%m.%Y') + '-' + DateTime.strptime(end_date, '%Y-%m-%d').strftime('%m.%Y')
#            vals={
#                'name':name,
#                'code':name,
#                'date_start':start_date,
#                'date_stop':end_date,
#            }
#            new_id=res_obj.create(cr, uid, vals, context=context)
#            res_obj.create_period(cr,uid,[new_id])
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'config.path.folder',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
config_bob_import()

def _folders_get(self, cr, uid, context={}):
    acc_type_obj = self.pool.get('config.bob.import')
    ids = acc_type_obj.search(cr, uid, [])
    path=[]
    if ids:
        path=acc_type_obj.read(cr, uid, [ids[len(ids)-1]], ['path'], context)

    if path[-1]['path']=='temp':
        res=[{'name':'jay','j':'vora'},{'name':'Non-jay','j':'non-Vora'}]
        res=[(r['j'], r['name']) for r in res]
    else:
        res=[(0,'')]
    return res
#    return [(r['j'], r['name']) for r in res]

class config_path_folder(osv.osv_memory):
    _name="config.path.folder"
    _columns ={
        'folder': fields.selection(_folders_get,'Folder'),
    }

    def action_back(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'config.bob.import',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

config_path_folder()

