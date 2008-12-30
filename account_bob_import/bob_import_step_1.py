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
from osv import fields, osv
from osv import orm
import time
import os
import base64
import tools
import StringIO
import zipfile
from tools import config, convert, misc

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
        'location': fields.selection([('locally','Locally(This Machine is the Server)'),('remotely','Remotely(This Machine is the Client)')], 'Location', required=True,help="If this machine is the server, select 'locally' as the location.If this is the client machine, create a zip of the 'Bob' folder placed in Root(Drive Letter)://Program Files/Bob.Upload it and follow the further instructions."),
        'path':fields.char('Path for BOB Folder',size=200,help="Supply a path that is a Bob Installation Folder."),
        'zipped_file': fields.binary('Upload a Zip File',filters='*.zip',help="Upload a .zip file containing information of BOB Installation'"),
#        'zipped_file': fields.binary('Upload a Zip File',filters=['*.zip','*.tar','*.tar.gz','*.tar.bz2','*.ar','*.ear','*.jar','*.war']),
    }

    def action_cancel(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }

    def action_create(self, cr, uid,ids, context=None):
        ids=self.search(cr, uid, [])
        path=self.read(cr, uid, [ids[len(ids)-1]],[], context)

        if path[-1]['location']=='locally':
            path_bob=path[-1]['path']
            if not os.path.exists(path_bob):
                raise osv.except_osv(_('User Error'), _('The Path "%s" doesn''\'t exist.Please provide a valid one.') % path[-1]['path'] )

            #if 'Bob.exe' not in os.listdir(path_bob):
            #    raise osv.except_osv(_('User Error'), _('The Path "%s" is not a valid BOB Folder.It doesn''\'t have Bob.exe.') % path[-1]['path'] )
        else:
            zipped_file=path[-1]['zipped_file']
            file_contents=base64.decodestring(zipped_file)

            fp = StringIO.StringIO(file_contents)
            fdata = zipfile.ZipFile(fp, 'r')
            fname = fdata.namelist()
            module_name=fname[0].split("/")[0]

            #if 'Bob/Bob.exe' not in fname:
            #    raise osv.except_osv(_('User Error'), _('The Zip file doesn''\'t contain a valid Bob folder.It doesn''\'t have Bob.exe.'))

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

            self.write(cr,uid,[ids[len(ids)-1]],{'path':rt_path+'/Bob'})

        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'config.path.folder',
#            'res_model':'ir.actions.configuration.wizard',
            'type': 'ir.actions.act_window',
            'target':'new',
        }
config_bob_import()

def _folders_get(self, cr, uid, context={}):
    acc_type_obj = self.pool.get('config.bob.import')
    ids = acc_type_obj.search(cr, uid, ['path'],context)
    path=[]
    res=[]
    seq=0
    if ids:
        path=acc_type_obj.read(cr, uid, [ids[len(ids)-1]], ['path'], context)
        path_bob=path[-1]['path']
        list_folders=os.listdir(path_bob)

#        The structure of BOB folder has non DDHMOT Files as codes
#        Data,Documents, Help, Message,Office, Tools.
        main_folders=['DATA','Documents', 'Help', 'Message','Office', 'Tools']

        for item in list_folders:
            if item not in main_folders:
                if os.path.isdir(path_bob+"/"+item):
                    seq +=1
                    res.append((path_bob+"/"+item,item))
    return res

class config_path_folder(osv.osv_memory):
    _name="config.path.folder"
    _columns ={
        'folder': fields.selection(_folders_get,'Folder',required=True),
    }

    def action_cancel(self,cr,uid,ids,context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'config.bob.import',
                'type': 'ir.actions.act_window',
                'target':'new',
        }
#    def action_cancel(self,cr,uid,ids,context=None):
#        return {
#            'view_type': 'form',
#            "view_mode": 'form',
#            'res_model': 'ir.actions.configuration.wizard',
#            'type': 'ir.actions.act_window',
#            'target':'new',
#        }
    def action_generate(self,cr,uid,ids,context=None):
        # Check for PXVIEW availabilty and convert .db to .csv
        path =  self.pool.get('config.path.folder').read(cr, uid, ids[0],['folder'],context)[0]['folder']
        tmp = path.split('/')
        folder_name = tmp[len(tmp)-1]
        for file in ['DBK.DB','ACCOUN.DB','COMPAN.DB','CONTACTS.DB','PERIOD.DB','VATCAS.DB','VAT.DB','AHISTO.DB']:

            #TODO: improve for using either the capital letters or no
            cmd = 'pxview '+path+'/'+folder_name+file+' -c > ' + config['addons_path']+'/account_bob_import/original_csv/'+file.split('.')[0].lower()+'.csv'
            res = os.system(cmd)
            if res != 0 and file != 'CONTACTS.DB':
                raise osv.except_osv(_('Error Occured'), _('An error occured when importing the file "%s". Please check that pxview is correclty installed on the server.')% file)
        import bob_import_step_2
        bob_import_step_2.run()
        filename = config['addons_path']+'/account_bob_import/account.account.csv'
        config.__setitem__('import_partial', 'bob.pickle')

        #deactivate the parent_store functionnality on account_account for rapidity purpose
        self.pool._init = True

        convert.convert_csv_import(cr, 'account_bob_import', 'account.account.csv', tools.file_open(filename).read())
        #reactivate the parent_store functionnality on account_account
        self.pool.get('account.account')._parent_store_compute(cr)

        filename = config['addons_path']+'/account_bob_import/account.journal.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.journal.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/res.partner.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'res.partner.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/res.partner.bank.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'res.partner.bank.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/res.partner.job.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'res.partner.job.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/account.fiscalyear.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.fiscalyear.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/account.period.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.period.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/account.move.reconcile-1.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.move.reconcile-1.csv', tools.file_open(filename).read())
        filename = config['addons_path']+'/account_bob_import/account.move.reconcile-2.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.move.reconcile-2.csv', tools.file_open(filename).read())

        filename = config['addons_path']+'/account_bob_import/account.move.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.move.csv', tools.file_open(filename).read())

        filename = config['addons_path']+'/account_bob_import/account.move.line.csv'
        convert.convert_csv_import(cr, 'account_bob_import', 'account.move.line.csv', tools.file_open(filename).read())
        self.pool._init = False

        #TODO: modify the name of account_bob_import.account_bob_0 into the name of company
        #TODO: some check to prevent errors: is file empty? add try-catch statements?
        #TODO: chisto and ahisto_matching .csv file

        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }

config_path_folder()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

