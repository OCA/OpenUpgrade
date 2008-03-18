import time
import tools
from osv import fields,osv,orm

import mx.DateTime
import base64
AVAILABLE_STATES = [
    ('draft','Draft'),
    ('unreviewed','Unreviewed'),
    ('open','Open'),
    ('cancel', 'Cancel'),
    ('done', 'Close'),
    ('pending','Pending')
]
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
    
    
    
    _name = "crm.cases"
    _inherit = "crm.case"
    def get_section(self, cr, uid, context={}):
         user = self.pool.get('crm.case.section').search(cr, uid, [('name', '=', 'Bug Tracking')])
         return user[0] 
    _columns = {
        'stage_id': fields.many2one ('crm.case.stage', 'Stage', domain="[('section_id','=',section_id)]"),
        'category2_id': fields.many2one('crm.case.category2','Category Name', domain="[('section_id','=',section_id)]"),
        'duration': fields.time ('Duration', type=float),
        'note': fields.text('Note'),
        'partner_name': fields.char('Employee Name', size=64),
        'partner_name2': fields.char('Last Name', size=64),
        'partner_phone': fields.char('Phone', size=16),
        'partner_mobile': fields.char('Mobile', size=16),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),
         
        
                }
    _defaults = {
             'section_id' :get_section,
                 }
    def menu_create1(self, cr, uid, ids, name, menu_parent_id=False, context={}):
        menus = {}
        menus[-1] = menu_parent_id
        for section in self.browse(cr, uid, ids, context):
            for (index, mname, mdomain, latest) in [
                (0,'',"[('section_id','=',"+str(section.id)+")]", -1),
                (1,'My ',"[('section_id','=',"+str(section.id)+"),('user_id','=',uid)]", 0),
                (2,'My Unclosed ',"[('section_id','=',"+str(section.id)+"),('user_id','=',uid), ('state','<>','cancel'), ('state','<>','done')]", 1),
                (3,'My Open ',"[('section_id','=',"+str(section.id)+"),('user_id','=',uid), ('state','=','open')]", 2),
                (4,'My Pending ',"[('section_id','=',"+str(section.id)+"),('user_id','=',uid), ('state','=','pending')]", 2),
                (5,'My Unreviewed ',"[('section_id','=',"+str(section.id)+"),('user_id','=',uid), ('state','=','draft'), ('state','=','unreviewed')]", 2),
                (6,'All ',"[('section_id','=',"+str(section.id)+"),]", 0),
                (7,'All Unclosed ',"[('section_id','=',"+str(section.id)+"),('state','<>','cancel'), ('state','<>','done')]", 6),
                (8,'All Open ',"[('section_id','=',"+str(section.id)+"),('state','=','open')]", 7),
                (9,'All Pending ',"[('section_id','=',"+str(section.id)+"),('state','=','pending')]", 7),
                (10,'All Unreviewed ',"[('section_id','=',"+str(section.id)+"),('state','=','draft'), ('state','=','unreviewed')]", 7),
                
            ]:
                view_mode = 'tree,form'
                icon = 'STOCK_JUSTIFY_FILL'
                if index==0:
                    view_mode = 'form,tree'
                    icon = 'STOCK_NEW'
                menu_id=self.pool.get('ir.ui.menu').create(cr, uid, {
                    'name': mname+name,
                    'parent_id': menus[latest],
                    'icon': icon
                })
                menus[index] = menu_id
                action_id = self.pool.get('ir.actions.act_window').create(cr,uid, {
                    'name': mname+name+' Cases',
                    'res_model': 'crm.cases',
                    'domain': mdomain,
                    'view_type': 'form',
                    'view_mode': view_mode,
                })
                self.pool.get('ir.values').create(cr, uid, {
                    'name': 'Open Cases',
                    'key2': 'tree_but_open',
                    'model': 'ir.ui.menu',
                    'res_id': menu_id,
                    'value': 'ir.actions.act_window,%d'%action_id,
                    'object': True
                })
        return True
    #end def
    def case_unreview(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state # to fill the browse record cache
        self.write(cr, uid, ids, {'state':'unreviewed', 'active':True})
        return True

crm_cases()
