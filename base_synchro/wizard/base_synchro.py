import wizard
import osv
from datetime import date
import time
import pooler
import xmlrpclib
import re

acc_synchro_form = '''<?xml version="1.0"?>
<form string="Transfer Data To Server">
    <field name="server_url" colspan="4"/>
    <newline/>
    <field name="port" colspan="4"/>
    <newline/>
</form>'''

acc_synchro_upload = '''<?xml version="1.0"?>
<form string="Upload Data">
    <field name="model_id" colspan="4"/>
    <newline/>
    <field name="db_name" colspan="4"/>
    <newline/>
    <field name="user_name" />
    <newline/>
    <field name="password"/>
</form>'''

acc_synchro_download = '''<?xml version="1.0"?>
<form string="Transfer Data To Server">
    <field name="model_id" colspan="4"/>
    <newline/>
    <field name="db_name" colspan="4"/>
    <newline/>
    <field name="user_name" />
    <newline/>
    <field name="password"/>
</form>'''


finish_form ='''<?xml version="1.0"?>
<form string="Upload/Download Complited!">
    <label string="Data Transfered successfully!!!" colspan="4"/>
</form>
'''

class wizard_cost_account_synchro(wizard.interface):

    server_url=""

    def _upload(self, cr, uid, data, context):
        model_id = data['form']['model_id']
        user_name = data['form']['user_name'];
        password = data['form']['password'];
        result = {}
        result['db_name'] = data['form']['db_name'];
        result['server_name']=data['form']['server_url'];
        result['port']=data['form']['port'];
        self.server_url = 'http://%s:%s/xmlrpc/common'%(result['server_name'],result['port']);
        try:
            sock = xmlrpclib.ServerProxy(self.server_url);
            user_id = sock.login(result['db_name'],user_name,password);
        except Exception,e :
            raise wizard.except_wizard('ServerError', 'Unable to connect server !')
        self.server_url = 'http://%s:%s/xmlrpc/object'%(result['server_name'],result['port']);
        sock = xmlrpclib.ServerProxy(self.server_url);
        self._create_structure(cr, uid, result['db_name'], user_id, password, model_id , sock)

        return 'finish'

    def _create_structure(self,cr,uid,db_name,user_id,password,model_id,sock,parent_id_local=False,parent_id_remote=False):
        model_local_ids = pooler.get_pool(cr.dbname).get('ir.model').search(cr,uid,[('id','=',model_id)]);
        model_local = pooler.get_pool(cr.dbname).get('ir.model').read(cr,uid,model_local_ids)[0];
        model_local_fields = pooler.get_pool(cr.dbname).get(model_local['model']).fields_get(cr,uid)
        local_pool = pooler.get_pool(cr.dbname).get(model_local['model'])

        model_data_ids=local_pool.search(cr,uid,[]);
        model_data_read=local_pool.read(cr,uid,model_data_ids)

        model_id=model_local['id']
        transfer_data={
                       'user_id':user_id,
                       'write_date':time.strftime('%Y-%m-%d'),
                       'model_id':model_id,
                       'server_url':str(sock),
                       'db_name':db_name,
                       'action':'u',
                       }
        insert_local_id = pooler.get_pool(cr.dbname).get('base.synchro.obj').create(cr,uid,transfer_data);
        line_ids_list=[]
        for model_data in model_data_read:
            search_list=[];
            for k,v in model_data.items():
                if k != 'id':
                    if type(v)==type(()):
                        search_list.append((k,'=',v[0]))
                    else:
                        search_list.append((k,'=',v))

            model_remote = sock.execute(db_name,user_id,password,model_local['model'],'search',search_list)
            if len(model_remote):
#                del model_data['id']
                a=sock.execute(db_name,user_id,password,model_local['model'],'write',model_remote,model_data)
                acc_sync_obj_line={
                                    'obj_id':insert_local_id,
                                    'local_id':model_data['id'],
                                    'remote_id':model_remote[0],
                                    'method':'w',
                                   }
                insert_local_id_line = pooler.get_pool(cr.dbname).get('base.synchro.obj.line').create(cr,uid,acc_sync_obj_line);
                line_ids_list.append(int(insert_local_id_line))
            else:
#                data = local_pool.read(cr,uid,model_data['id'])[0]
#                fields = local_pool.fields_get(cr, uid)
                default = {}
                if not default:
                    default = {}
                if 'state' not in default:
                    if 'state' in local_pool._defaults:
                        default['state'] = local_pool._defaults['state'](local_pool,cr,uid)
                data = local_pool.read(cr, uid, [model_data['id']], context={})[0]
                fields = local_pool.fields_get(cr, uid)
                for f in fields:
                    ftype = fields[f]['type']
                    if f in default:
                        data[f] = default[f]
                    elif ftype == 'function':
                        del data[f]
                    elif ftype == 'many2one':
                        try:
                            data[f] = data[f] and data[f][0]
                        except:
                            pass
                    elif ftype in ('one2many', 'one2one'):
                        res = []
                        rel = pooler.get_pool(cr.dbname).get(fields[f]['relation'])
                        for rel_id in data[f]:
                            # the lines are first duplicated using the wrong (old)
                            # parent but then are reassigned to the correct one thanks
                            # to the (4, ...)
                            res.append((4, rel.copy(cr, uid, rel_id, context={})))
                        data[f] = res
                    elif ftype == 'many2many':
                        data[f] = [(6, 0, data[f])]
                del data['id']
                for v in local_pool._inherits:
                    del data[local_pool._inherits[v]]
                new_id = sock.execute(db_name,user_id,password,model_local['model'],'create',data)
                acc_sync_obj_line={
                    'obj_id':insert_local_id,
                    'local_id':model_data['id'],
                    'remote_id':new_id,
                    'method':'c',
                   }
                insert_local_id_line = pooler.get_pool(cr.dbname).get('base.synchro.obj.line').create(cr,uid,acc_sync_obj_line);
                line_ids_list.append(int(insert_local_id_line))
#                new_id = sock.execute(db_name,user_id,password,model_local['model'],'create',data)
#            end if analytic_account_remote:\
        insert_local_id_map = pooler.get_pool(cr.dbname).get('base.synchro.obj')
        cr.commit()
#        insert_local_id_map.write(cr,uid,[insert_local_id],{'fields_id':[1,2,3]});

#      Code for download model starts from here

    def _download(self, cr, uid, data, context):

        model_id = data['form']['model_id']
        user_name = data['form']['user_name'];
        password = data['form']['password'];
        result = {}
        result['db_name'] = data['form']['db_name'];
        result['server_name']=data['form']['server_url'];
        result['port']=data['form']['port'];
        self.server_url = 'http://%s:%s/xmlrpc/common'%(result['server_name'],result['port']);
        try:
            sock = xmlrpclib.ServerProxy(self.server_url);
            user_id = sock.login(result['db_name'],user_name,password);
        except Exception,e :
            raise wizard.except_wizard('ServerError', 'Unable to connect server !')
        self.server_url = 'http://%s:%s/xmlrpc/object'%(result['server_name'],result['port']);
        sock = xmlrpclib.ServerProxy(self.server_url);
        self._create_structure_local(cr, uid, result['db_name'], user_id, password, model_id , sock)
        return 'finish'

    def _create_structure_local(self,cr,uid,db_name,user_id,password,model_id,sock,parent_id_local=False,parent_id_remote=False):
        search_model=[('id','=',model_id)];
        model_remote_ids = sock.execute(db_name,user_id,password,'ir.model','search',search_model);
        model_remote = sock.execute(db_name,user_id,password,'ir.model','read',model_remote_ids)[0];
        model_remote_fields = sock.execute(db_name,user_id,password,model_remote['model'],'fields_get')
        local_pool = pooler.get_pool(cr.dbname).get(model_remote['model'])
        model_data_ids=sock.execute(db_name,user_id,password,model_remote['model'],'search',[]);
        model_data_read=sock.execute(db_name,user_id,password,model_remote['model'],'read',model_data_ids)
        transfer_data={
                       'user_id':user_id,
                       'write_date':time.strftime('%Y-%m-%d'),
                       'model_id':model_id,
                       'server_url':str(sock),
                       'db_name':db_name,
                       'action':'d',
                       }
        insert_local_id = pooler.get_pool(cr.dbname).get('base.synchro.obj').create(cr,uid,transfer_data);
        line_ids_list=[]
        for model_data in model_data_read:
            search_list=[];
            for k,v in model_data.items():
                if k != 'id':
                    if type(v)==type(()):
                        search_list.append((k,'=',v[0]))
                    else:
                        search_list.append((k,'=',v))

            model_local = local_pool.search(cr,uid,search_list)
            if len(model_local):
#                del model_data['id']
                a=local_pool.write(cr,uid,model_local,model_data)
                acc_sync_obj_line={
                                    'obj_id':insert_local_id,
                                    'local_id':model_data['id'],
                                    'remote_id':model_local[0],
                                    'method':'w',
                                   }
                insert_local_id_line = pooler.get_pool(cr.dbname).get('base.synchro.obj.line').create(cr,uid,acc_sync_obj_line);
                line_ids_list.append(int(insert_local_id_line))

            else:
                default = {}
                if not default:
                    default = {}
                if 'state' not in default:
                    if 'state' in sock._defaults:
######                        change required
                        default['state'] = local_pool._defaults['state'](local_pool,cr,uid)
                data = sock.execute(db_name,user_id,password,model_remote['model'],'read',[model_data['id']], context={})[0]
######                        change required
                fields = local_pool.fields_get(cr, uid)
                for f in fields:
                    ftype = fields[f]['type']
                    if f in default:
                        data[f] = default[f]
                    elif ftype == 'function':
                        del data[f]
                    elif ftype == 'many2one':
                        try:
                            data[f] = data[f] and data[f][0]
                        except:
                            pass
                    elif ftype in ('one2many', 'one2one'):
                        res = []
                        rel = pooler.get_pool(cr.dbname).get(fields[f]['relation'])
                        for rel_id in data[f]:
                            # the lines are first duplicated using the wrong (old)
                            # parent but then are reassigned to the correct one thanks
                            # to the (4, ...)
                            res.append((4, rel.copy(cr, uid, rel_id, context={})))
                        data[f] = res
                    elif ftype == 'many2many':
                        data[f] = [(6, 0, data[f])]
                del data['id']
                for v in local_pool._inherits:
                    del data[local_pool._inherits[v]]
                new_id = local_pool.create(cr,uid,data)
#                new_id = sock.execute(db_name,user_id,password,model_local['model'],'create',data)
            #end if analytic_account_remote:\
        insert_local_id_map = pooler.get_pool(cr.dbname).get('base.synchro.obj')
        cr.commit()
#      Code for download model ends from here

    def _get_dbname(self, cr, uid, context):

        db_service=self.server_url+'db';
        try:
            sock = xmlrpclib.ServerProxy(db_service)
        except Exception,e:
            raise wizard.except_wizard('ServerError', 'Unable to connect server !')
        return [(dbnm,dbnm) for dbnm in sock.list()]

    acc_synchro_fields = {
        'server_url': {'string':'Server URL', 'type':'char', 'size':64 ,'required':True},
        'port':{'string':'Port No.','type':'char','size':5,'required':True},
     }

    acc_synchro_download_upload_field = {
        'model_id': {'string':'Model Name', 'type':'many2one', 'relation':'ir.model','required':True},
        'db_name':{'string':'Database','type':'selection','selection':_get_dbname,'required':True},
        'user_name' : {'string':'User Name','size':64,'type':'char','required':True},
        'password' : {'string':'Password','size':64,'type':'char','invisible':True,'required':True},
    }


    def _init_wizard(self, cr, uid, data, context):
        return {'server_url':'192.168.0.14','port':'8069'}

    def _assign_server_upload(self, cr, uid, data, context):
        self.server_url = 'http://%s:%s/xmlrpc/'%(data['form']['server_url'],data['form']['port']);
        print "in upload :::::",self.server_url
        return {'user_name':'admin','password':'admin'}

    def _assign_server_download(self, cr, uid, data, context):
        self.server_url = 'http://%s:%s/xmlrpc/'%(data['form']['server_url'],data['form']['port']);
        print "in download :::::",self.server_url
        return {'user_name':'admin','password':'admin'}
        return {}

    states = {
        'init': {
            'actions': [_init_wizard],
            'result': {'type':'form', 'arch':acc_synchro_form, 'fields':acc_synchro_fields, 'state':[('end','Cancel'),('upload','Upload'),('download','Download')]}
        },
        'upload': {
            'actions': [_assign_server_upload],
            'result':{'type':'form', 'arch':acc_synchro_upload, 'fields':acc_synchro_download_upload_field, 'state':[('end','Cancel'),('upload_ok','Upload')]}
        },
        'upload_ok': {
            'actions': [],
            'result':{'type':'choice', 'next_state': _upload}
        },
        'download': {
            'actions': [_assign_server_download],
            'result':{'type':'form', 'arch':acc_synchro_download, 'fields':acc_synchro_download_upload_field, 'state':[('end','Cancel'),('download_ok','Download')]}
        },
        'download_ok': {
            'actions': [],
            'result':{'type':'choice', 'next_state':_download}
        },
        'finish':{
            'actions': [],
            'result':{'type':'form', 'arch':finish_form,'fields':{},'state':[('end','OK')]}
        }
    }
wizard_cost_account_synchro('account.analytic.account.transfer')


