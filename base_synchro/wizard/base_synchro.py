
import wizard
import osv
from datetime import date
import time
import pooler
import xmlrpclib
import re

acc_synchro_form = '''<?xml version="1.0"?>
<form string="Transfer Data To Server">
    <field name="model_id" colspan="4"/>
    <newline/>
    <field name="server_url" colspan="4"/>
    <newline/>
    <label/>
    <label string="like :: dbname@servername:port"/>
    <newline/>
    <field name="user_name" />
    <field name="password"/>
</form>'''

acc_synchro_fields = {
    'model_id': {'string':'Model Name', 'type':'many2one', 'relation':'ir.model', 'required':True },
    'server_url': {'string':'Server URL', 'type':'char', 'size':64 , 'required':True},
    'user_name' : {'string':'User Name','size':64,'type':'char','required':True},
    'password' : {'string':'Password','size':64,'type':'char','invisible':True,'required':True},
}
wrong_server_name_form ='''<?xml version="1.0"?>
<form string="Wrong Server Name">
    <label string="Type server name like :: terp@tinyerp.com:8069 !!!" colspan="4"/>
</form>
'''

finish_form ='''<?xml version="1.0"?>
<form string="Finish">
    <label string="Data Transfered successfully!!!" colspan="4"/>
</form>
'''

not_connect_to_server = '''<?xml version="1.0"?>
<form string="Connection Not Available">
    <label string="Unable to connect to server !!!" colspan="4"/>
</form>
'''

class wizard_cost_account_synchro(wizard.interface):

    def _transfer(self, cr, uid, data, context):
        try:
            model_id = data['form']['model_id']
            user_name = data['form']['user_name'];
            password = data['form']['password'];
            result=self._validate_server(data['form']['server_url'])
            if not result:
                return 'wrong_server_name'
            server_url = 'http://%s:%s/xmlrpc/common'%(result['server_name'],result['port']);

            sock = xmlrpclib.ServerProxy(server_url);

            user_id = sock.login(result['db_name'],user_name,password);

            server_url = 'http://%s:%s/xmlrpc/object'%(result['server_name'],result['port']);
            sock = xmlrpclib.ServerProxy(server_url);
            self._create_structure(cr, uid, result['db_name'], user_id, password, model_id , sock)
        except Exception,e:

            if hasattr(e,'args'):
                print "Items::",e.args;
                if len(e.args) == 2:
                    if e.args[0] == -2:
                        return 'wrong_server_name'
                    #end if e.args[0] == -2:
                else:
                    return 'wrong_server_name'
                #end if len(e.args) == 2:
            #end if hasattr(e,'args'):

            return 'wrong_server_name'
        return 'finish'

    def _create_structure(self,cr,uid,db_name,user_id,password,model_id,sock,parent_id_local=False,parent_id_remote=False):
        model_local_ids = pooler.get_pool(cr.dbname).get('ir.model').search(cr,uid,[('id','=',model_id)]);
        model_local = pooler.get_pool(cr.dbname).get('ir.model').read(cr,uid,model_local_ids)[0];
        model_local_fields = pooler.get_pool(cr.dbname).get(model_local['model']).fields_get(cr,uid)
        local_pool = pooler.get_pool(cr.dbname).get(model_local['model'])
#        fields_list=[];
#        for k,v in model_local_fields.items():
#            if v['type']=='function' or v['type']=='one2many' or v['type']=='many2many' or v['type']=='many2one' :
#                continue
#            else:
#                fields_list.append(k);
#
#        print "Fields selected ::::",fields_list

        model_data_ids=local_pool.search(cr,uid,[]);
        model_data_read=local_pool.read(cr,uid,model_data_ids)

        model_id=model_local['id']
        transfer_data={
                       'local_id':'1',
                       'remote_id':'1',
                       'user_id':user_id,
                       'write_date':time.strftime('%Y-%m-%d'),
                       'model_id':model_id,
                       'server_url':str(sock),
                       'db_name':db_name,

                       }
        insert_local_id = pooler.get_pool(cr.dbname).get('base.synchro.obj').create(cr,uid,transfer_data);
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
#                print "DATA WRITTEN  :::::::::::::::: ",a;
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

                print "Data before wrte::",data
                new_id = sock.execute(db_name,user_id,password,model_local['model'],'create',data)
#                new_id = sock.execute(db_name,user_id,password,model_local['model'],'create',data)
            #end if analytic_account_remote:\

    def _validate_server(self,server_name):
        pat = re.compile('@|:');
        pat_list = pat.split(server_name)
        if((len(pat_list))!=3):
            return False
        else:
            ret_dict = {}
            ret_dict['db_name'] = pat_list[0];
            ret_dict['server_name']=pat_list[1];
            ret_dict['port']=pat_list[2];
            return ret_dict
        #end if server_name.startwith('http'):
    #end def _validate_server(self,server_name):


    def _init_wizard(self, cr, uid, data, context):
        return {'server_url':'apos@192.168.0.11:8069','user_name':'admin','password':'admin'}

    states = {
        'init': {
            'actions': [_init_wizard],
            'result': {'type':'form', 'arch':acc_synchro_form, 'fields':acc_synchro_fields, 'state':[('end','Cancel'),('transfer','Transfer')]}
        },
        'transfer': {
            'actions': [],
            'result':{'type':'choice', 'next_state': _transfer}
        },
        'wrong_server_name': {
            'actions': [],
            'result':{'type':'form', 'arch':wrong_server_name_form,'fields':{},'state':[('end','OK')]}
        },
        'finish':{
            'actions': [],
            'result':{'type':'form', 'arch':finish_form,'fields':{},'state':[('end','OK')]}
                  }
    }
wizard_cost_account_synchro('account.analytic.account.transfer')


