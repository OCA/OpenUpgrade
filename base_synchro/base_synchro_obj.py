from osv import fields,osv;
import tools;
import ir;
import pooler;

class base_synchro_obj(osv.osv):
    '''Class to store the operations done by wizart'''
    _name = "base.synchro.obj";
    _description = "Register Class";
    _columns = {
                'local_id': fields.char('Local Id',size=50,readonly=True),
                'remote_id':fields.char('Remote Id',size=50,readonly=True),
                'user_id':fields.char('User Id',size=50,readonly=True),
                'write_date':fields.date('Write Date',size=50,readonly=True),
                'model_id':fields.char('Model ID',size=50,readonly=True),
                'server_url': fields.char('Server URL', size=50, readonly=True),
                'db_name':fields.char('Database Name', size=50,readonly=True),
               }
#End class base_synchro_obj
base_synchro_obj();
