import time
import tools
from osv import fields,osv,orm

import mx.DateTime
import base64
#AVAILABLE_STATES = [
#    ('draft','Unreviewed'),
#    ('open','Open'),
#    ('cancel', 'Refuse Bug'),
#    ('done', 'Done'),
#    ('pending','Pending')
#]
class crm_case_category2(osv.osv):
    _name = "crm.case.category2"
    _description = "Category2 of case"
    _rec_name = "name"
    _columns = {
        'name': fields.char('Case Category2 Name', size=64, required=True),
        'section_id': fields.many2one('crm.case.section', 'Case Section'),
    }

crm_case_category2()

class crm_case_stage(osv.osv):
    _name = "crm.case.stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _columns = {
        'name': fields.char('Stage Name', size=64, required=True),
        'section_id': fields.many2one('crm.case.section', 'Case Section'),
                }

crm_case_stage()

class crm_cases(osv.osv):
     
    _name = "crm.case"
    _inherit = "crm.case"
    def get_section(self, cr, uid, context={}):
         user = self.pool.get('crm.case.section').search(cr, uid, [('name', '=', 'Bug Tracking')])
         return user[0] 
    _columns = {
        'stage_id': fields.many2one ('crm.case.stage', 'Stage', domain="[('section_id','=',section_id)]"),
        'category2_id': fields.many2one('crm.case.category2','Category Name', domain="[('section_id','=',section_id)]"),
        'duration': fields.time('Duration',size=16),
        'note': fields.text('Note'),
        'partner_name': fields.char('Employee Name', size=64),
        'partner_name2': fields.char('Employee Email', size=64),
        'partner_phone': fields.char('Phone', size=16),
        'partner_mobile': fields.char('Mobile', size=16),
#        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),
         
        
                }
#    _defaults = {
#             'section_id' :get_section,
#                 }


crm_cases()
