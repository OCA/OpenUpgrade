from osv import fields, osv
import pooler

class dept_type(osv.osv):
    _name = "dept.type"
    _description = "Department Type"
    _order = "dname"
    _rec_name = 'dname'
    _columns = {
                'deptid': fields.integer('ID',size=64, required=True),
                'dname': fields.char('Department Name', size=64, required=True),
                'street': fields.char('Street',size=64),
                'city': fields.char('City',size=64),
                'zip': fields.integer('Zip Code',size=64),
                'state': fields.char('State',size=64),
                'country': fields.char('Country',size=64),
                'desc': fields.text('Description'),
                }
dept_type()

class employee_type(osv.osv):
    _name = "employee.type"
    _description = "employee Type"
    _rec_name = 'name'
    _columns = {
        'eid': fields.integer('ID',size=64, required=True),
        'name': fields.char('Name', size=64, required=True),
        'designation':fields.char('Designation',size=64),
        'dept_id':fields.many2one('dept.type','Department', required=True),
        'email':fields.char('Email',size=64),
        'state': fields.selection([
            ('draft','Not Validate'),
            ('valid','Valid Email Address'),
            ('notvalid','Invilade Email Address'),
            ('dnserror','DNS Error During Check'),
            ('noresponse','No Resopnse During Check'),],
        'status', select=True, readonly=True),
        'resume':fields.binary('Resume'),
        'address': fields.one2many('res.partner.address', 'emp_id', 'Contacts'),
           
        
    }
#    def onchange_emp_name(self, cr, uid, ids, part):
#          res = {} 
#          print "PART_____________",part
#          if part:
#                data=self.pool.get('employee.type').browse(cr,uid,[part])[0]
#                res['name']=data.ename
#                return {'value': res}
#          else:
#              return True
         
    def chech_email_new(self, cr, uid, ids, *args):
        return pooler.get_pool(cr.dbname).get('employee.type').write(cr, uid, ids,{'state':'valid'})

employee_type()   






class res_partner_address(osv.osv):
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner',),
        'emp_id': fields.many2one('employee.type', 'Employee', required=True, ondelete='cascade', select=True),
#        'email_ids':fields.one2many('email.list', 'partner_id', 'Email List'),
        }
   

res_partner_address()
#class res_partner_address(osv.osv):
#    _inherit = 'res.partner.address'
#    _name = 'res.partner.address'
#    _columns = {
#                'partner_id': fields.many2one('employee.type', 'Employee', required=True, ondelete='cascade', select=True),                
#                }
#    
#res_partner_address()

