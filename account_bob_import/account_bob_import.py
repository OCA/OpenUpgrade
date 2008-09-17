from osv import fields, osv
from osv import orm
import time
import os
import base64
import tools
import StringIO
import zipfile

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

class check_bob_installation(osv.osv_memory):
    _name="check.bob.installation"
    _columns ={
        'location': fields.selection([('locally','Locally'),('remotely','Remotely')], 'Location', required=True),
    }

    def action_next(self,cr,uid,ids,context=None):
        res_model='remote.bob.location'
        obj_self=self.read(cr,uid,ids)[0]
        if 'location' in obj_self:
            if obj_self['location']=='locally':
                res_model='config.bob.import'

        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': res_model,
                'type': 'ir.actions.act_window',
                'target':'new',
            }

check_bob_installation()

class remote_bob_location(osv.osv_memory):
    _name="remote.bob.location"
    _columns ={
        'company_id':fields.many2one('res.company','Company', required=True),
        'zipped_file': fields.binary('Upload a Zip File',filters=['*.zip']),
#        'zipped_file': fields.binary('Upload a Zip File',filters=['*.zip','*.tar','*.tar.gz','*.tar.bz2','*.ar','*.ear','*.jar','*.war']),
    }

    def action_back(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'check.bob.installation',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

    def action_next(self,cr,uid,ids,context=None):
        # Saving the uploaded zip file, unzipping it, and classifying the bob code folders.
        ids=self.search(cr, uid, [])
        file=self.read(cr, uid, [ids[len(ids)-1]])
        zipped_file=file[-1]['zipped_file']
        file_contents=base64.decodestring(zipped_file)

        fp = StringIO.StringIO(file_contents)
        fdata = zipfile.ZipFile(fp, 'r')
        fname = fdata.namelist()
        module_name=fname[0].split("/")[0]

        if 'Bob/bob.exe' not in fname:
            raise osv.except_osv(_('User Error'), _('The Zip file doesn''\'t contain a valid Bob folder.It doesn''\'t have bob.exe.'))


        root_path=tools.config['root_path']
        rt_path=root_path+'/'+'bob_'+str(time.strftime('%d-%m-%y-%H:%M:%S'))
        os.makedirs(rt_path)

        for name in fname:
            path=name.split('/')
            name1=''
            if len(path)>1:
                name1=str('/'.join(x for x in path[:-1]))

            if not os.path.exists(rt_path+'/'+name1):
                os.makedirs(rt_path+'/'+name1)

            if not os.path.isdir(rt_path+'/'+name):
                outfile = open(rt_path+'/'+name, 'wb')
                outfile.write(fdata.read(name))
                outfile.close()
        fp.close()

        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'config.path.folder',
                'type': 'ir.actions.act_window',
                'target':'new',
            }

remote_bob_location()

class config_bob_import(osv.osv_memory):
    _name = 'config.bob.import'
    _columns = {
        'company_id':fields.many2one('res.company','Company', required=True),
        'path':fields.char('Path for BOB Folder',required=True,size=200),
    }

    def action_cancel(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.module.module.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }

    def action_back(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'check.bob.installation',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

    def action_create(self, cr, uid,ids, context=None):
        ids=self.search(cr, uid, [])
        path=self.read(cr, uid, [ids[len(ids)-1]], ['path'], context)
        path_bob=path[-1]['path']

        if not os.path.exists(path_bob):
            raise osv.except_osv(_('User Error'), _('The Path "%s" doesn''\'t exist.Please provide a valid one.') % path[-1]['path'] )

        if 'bob.exe' not in os.listdir(path_bob):
            raise osv.except_osv(_('User Error'), _('The Path "%s" is not a valid BOB Folder.It doesn''\'t have bob.exe.') % path[-1]['path'] )

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
    res=[(0,'')]
    seq=0
    if ids:
        path=acc_type_obj.read(cr, uid, [ids[len(ids)-1]], ['path'], context)
        path_bob=path[-1]['path']
        list_folders=os.listdir(path_bob)

#        The structure of BOB folder has non DDHMOT Files as codes
#        Data,Documents, Help, Message,Office, Tools.
        main_folders=['Data','Documents', 'Help', 'Message','Office', 'Tools']

        for item in list_folders:
            if item not in main_folders:
                if os.path.isdir(path_bob+"/"+item):
                    seq +=1
                    res.append((seq,item))
    return res

class config_path_folder(osv.osv_memory):
    _name="config.path.folder"
    _columns ={
        'folder': fields.selection(_folders_get,'Folder'),
    }

    def action_back(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'check.bob.installation',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
    def action_cancel(self,cr,uid,ids,context=None):
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'ir.module.module.configuration.wizard',
            'type': 'ir.actions.act_window',
            'target':'new',
        }
    def action_generate(self,cr,uid,ids,context=None):
        # TODO: Check for PXVIEW availabilty and convert .db to .csv
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.module.module.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }

config_path_folder()

