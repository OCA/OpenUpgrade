import wizard
import osv
from datetime import date
import time
import pooler
import xmlrpclib
import re
import tools

acc_synchro_form = '''<?xml version="1.0"?>
<form string="Transfer Data To Server">
    <field name="server_url" colspan="4"/>
    <newline/>
    <newline/>
</form>'''

finish_form ='''<?xml version="1.0"?>
<form string="Synchronization Complited!">
    <label string="Data Transfered successfully!!!" colspan="4"/>
</form>
'''



class wizard_cost_account_synchro(wizard.interface):

    server_url=""

    def _validate_server(self,cr,uid,server_name):
        pat = re.compile('@|:')
        pat_list = pat.split(server_name)
        ret_dict = {}
        ret_dict['db_name'] = pat_list[0];
        ret_dict['server_name']=pat_list[1];
        ret_dict['port']=pat_list[2];
        return ret_dict

    def _fields_list(self,cr,uid,field_list,remove_list=None):
        tmp={}
        print "tmp before::::::::::",tmp
        for field in field_list:
            print "field :",field
            if field_list[field]['type'] not in remove_list:
                tmp[field] = field_list[field]

        print "tmppppppppppppppppppp",tmp
        return tmp

    def _upload_download(self, cr, uid, data, context):

        port=tools.config['port']
        port=int(port)
        local_url = 'http://%s:%d/xmlrpc/'%(tools.config['smtp_server'],port)
        rpcproxy1 = xmlrpclib.ServerProxy(local_url+'object');
        url_id = data['form']['server_url']
        url=rpcproxy1.execute(cr.dbname,uid,'admin','base.synchro.server','read',[url_id])
        objid=url[0]['obj_id']
        models = rpcproxy1.execute(cr.dbname,uid,'admin','base.synchro.obj','read',url[0]['obj_id'])
        url_split=self._validate_server(cr,uid,url[0]['name'])
        user_name = url[0]['login'];
        password = url[0]['password'];
        result = {}
        result['db_name'] = url_split['db_name'];
        result['server_name']=url_split['server_name'];
        result['port']=url_split['port'];
        self.server_url = 'http://%s:%s/xmlrpc/common'%(result['server_name'],result['port']);
        try:
            rpcproxy2 = xmlrpclib.ServerProxy(self.server_url);
            user_id = rpcproxy2.login(result['db_name'],user_name,password);
        except Exception,e :
            raise wizard.except_wizard('ServerError', 'Unable to connect server !')
        print "server2 connected successfully:::::::::"
        self.server_url = 'http://%s:%s/xmlrpc/object'%(result['server_name'],result['port']);
        rpcproxy2 = xmlrpclib.ServerProxy(self.server_url);

        for model in models:
            if (model['action']=='u'):
                self._create_structure(cr, uid, rpcproxy1,rpcproxy2,model,['admin',password],[cr.dbname,result['db_name']],[uid,user_id],url)
            elif (model['action']=='d'):
                self._create_structure(cr, uid, rpcproxy2,rpcproxy1,model,[password,'admin'],[result['db_name'],cr.dbname],[user_id,uid],url)
        return 'finish'

    def _create_structure(self,cr,uid, rpcproxy1,rpcproxy2,model,password,db_name,user_id,url):
        model_local_fields=rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'fields_get')
        model_local_fields=self._fields_list(cr, uid, model_local_fields, ['function','one2many','many2many'])
        model_data_ids=rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'search',[])
        model_data_read=rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'read',model_data_ids,model_local_fields.keys())
        for model_data in model_data_read:
            model_remote = rpcproxy2.execute(db_name[1],user_id[1],password[1],model['model_id'][1],'name_search',model_data['name'],[],'=')
            if len(model_remote):
#                del model_data['id']
                tmp_data=rpcproxy2.execute(db_name[1],user_id[1],password[1],model['model_id'][1],'read',[model_remote[0][0]],model_local_fields.keys())
                search_list=[];
                for k,v in model_data.items():
                    if k != 'id':
                        if type(v)==type(()):
                            search_list.append((k,'=',v[0]))
                        elif type(v)==type([]) and len(tmp_data[0][k]):
                                search_list.append((k,'=',v[0]))
                                model_data[k]=tmp_data[0][k][0]
                        else:
                            search_list.append((k,'=',v))

                a=rpcproxy2.execute(db_name[1],user_id[1],password[1],model['model_id'][1],'write',[model_remote[0][0]],model_data)
                acc_sync_obj_line={
                                    'obj_id':model['id'],
                                    'local_id':model_data['id'],
                                    'remote_id':model_remote[0][0],
                                    'method':'w',
                                   }
                insert_local_id_line = pooler.get_pool(cr.dbname).get('base.synchro.obj.line').create(cr,uid,acc_sync_obj_line);
            else:

                default = {}
                if not default:
                    default = {}
                if 'state' not in default:
                    if 'state' in rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'default_get',['state']):
                        default['state'] = rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'default_get',['state'])['state']
                data=rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'read',[model_data['id']])[0]
                fields=rpcproxy1.execute(db_name[0],user_id[0],password[0],model['model_id'][1],'fields_get')
                fields=self._fields_list(cr, uid, fields, ['function','one2many','many2many'])
                for f in fields:

                    ftype = fields[f]['type']
                    if f in default:
                        data[f] = default[f]
                    elif ftype == 'function':
                        del data[f]
                    elif ftype == 'many2one':
                        try:
                            res = False
                            relation=fields[f]['relation']
                            res2 = rpcproxy1.execute(db_name[0],user_id[0],password[0],relation,'name_search',data[f][1])
                            res3 = rpcproxy2.execute(db_name[1],user_id[1],password[1],relation,'name_search',data[f][1])
                            if res3:
                                data[f] = res3[0][0]
                            else:
                                cr_data=rpcproxy1.execute(db_name[0],user_id[0],password[0],relation,'read',[res2[0][0]])
                                for tk,tv in cr_data[0].items():
                                    if tk != 'id':
                                        if type(tv)==type([]) and len(cr_data[0][tk]):
                                            cr_data[0][tk]=cr_data[0][tk][0]
                                del cr_data[0]['id']
                                new_id = rpcproxy2.execute(db_name[1],user_id[1],password[1],relation,'create',cr_data[0])
                                cr.commit();
                                data[f] = new_id
                        except:
                            pass
                    elif ftype in ('one2many', 'one2one'):
                        continue
                for dk,dv in data.items():
                    if dk != 'id':
                        if type(dv)==type([]) and len(data[dk]):
                            data[dk]=data[dk][0]
                del data['id']
                new_id = rpcproxy2.execute(db_name[1],user_id[1],password[1],model['model_id'][1],'create',data)
                acc_sync_obj_line={
                    'obj_id':model['id'],
                    'local_id':model_data['id'],
                    'remote_id':new_id,
                    'method':'c',
                   }
                insert_local_id_line = pooler.get_pool(cr.dbname).get('base.synchro.obj.line').create(cr,uid,acc_sync_obj_line);


    acc_synchro_fields = {
        'server_url': {'string':'Server URL', 'type':'many2one', 'relation':'base.synchro.server','required':True},
            }

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':acc_synchro_form, 'fields':acc_synchro_fields, 'state':[('end','Cancel'),('upload_download','Synchronize')]}
        },
        'upload_download': {
            'actions': [],
            'result':{'type':'choice', 'next_state': _upload_download}
        },
        'finish': {
            'actions': [],
            'result':{'type':'form', 'arch':finish_form,'fields':{},'state':[('end','Ok')]}
        },

    }
wizard_cost_account_synchro('account.analytic.account.transfer')


