from osv import fields,osv;
import tools;
import ir;
import pooler;
import re;


class base_synchro_server(osv.osv):
    '''Class to store the information regarding server'''
    _name = "base.synchro.server";
    _description = "Register Class";

    _columns = {
                'name': fields.char('Server URL', size=64),
                'login': fields.char('User Name',size=50,),
                'password': fields.char('Password',size=64,invisible=True,required=True),
                'obj_id' : fields.one2many('base.synchro.obj','server_id','Models',ondelete='cascade')
               }

    def _validate_server(self,cr,uid,ids,server_name):
        pat = re.compile('@|:');
        pat_list = pat.split(server_name)
        if((len(pat_list))!=3):
            print "invalid server name"
            raise osv.except_osv('Invalid Server name !','Invalid Server Name! It must be like "dbname@servername:port" ! ')
            return False
        else:
            print "valid server name"
            ret_dict = {}
            ret_dict['db_name'] = pat_list[0];
            ret_dict['server_name']=pat_list[1];
            ret_dict['port']=pat_list[2];
            return True

#End class base_synchro_server
base_synchro_server();


class base_synchro_obj(osv.osv):
    '''Class to store the operations done by wizart'''
    _name = "base.synchro.obj";
    _description = "Register Class";
    _rec_name='server_id'
    _columns = {
                'server_id':fields.many2one('base.synchro.server','Models', ondelete='cascade', select=True),
                'model_id': fields.many2one('ir.model', 'Model Name',required=True),
                'action':fields.selection((('d','Download'),('u','Upload')),'Action', required=True),
                'sequence': fields.integer('Sequence'),
                'synchronize_date':fields.date('Synchronization Date'),
                'line_id':fields.one2many('base.synchro.obj.line','obj_id','Ids Affected',ondelete='cascade'),

               }
    _order = 'sequence'
#End class base_synchro_obj
base_synchro_obj();


class base_synchro_obj_line(osv.osv):
    '''Class to store the operations done by wizart'''
    _name = "base.synchro.obj.line";
    _description = "Register Class";
    _rec_name='obj_id'

    _columns = {
                'obj_id': fields.many2one('base.synchro.obj', 'Ids Affected', ondelete='cascade', select=True),
                'local_id': fields.integer('Local Id',readonly=True),
                'remote_id':fields.integer('Remote Id',readonly=True),
                'method':fields.selection((('c','Create'),('w','Write')),'Action', readonly=True),
               }
#class base_synchro_obj_line(osv.osv):
base_synchro_obj_line();
