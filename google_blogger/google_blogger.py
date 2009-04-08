import netsvc
import time
from osv import fields, osv
import re

class res_users(osv.osv):
    _inherit="res.users"
    _description = 'res.users'
    
    _columns = {
        'blogger_email':fields.char('Blogger Email Id', size=100),
        'blogger_password': fields.char('Password', size=100),
                }
res_users()