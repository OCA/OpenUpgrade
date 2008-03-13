
import time
import netsvc
from osv import fields, osv, orm

from mx import DateTime

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('cancelled', 'Cancel'),
    ('done', 'Close'),
    ('pending','Pending')
]

AVAILABLE_PRIORITIES = [
    ('5','Lowest'),
    ('4','Low'),
    ('3','Normal'),
    ('2','High'),
    ('1','Highest')
]
def _links_get(self, cr, uid, context={}):
    obj = self.pool.get('res.request.link')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['object', 'name'], context)
    return [(r['object'], r['name']) for r in res]

class crm_meeting(osv.osv):
    _name = 'crm.meeting'
    _description = 'Daily Meetings'
    _rec_name = "name"
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name' : fields.char('Meeting Name(Title)', size=64, required=True),
        'priority': fields.selection(AVAILABLE_PRIORITIES, 'Priority'),
        'crm_id11': fields.many2one('res.partner', 'Partner', required=True),
        'agenda': fields.text('Agenda'),
#        'section_id': fields.many2one('crm.case.section', 'Department', required=True, select=True),
        'creat_date': fields.datetime('Opened' ,readonly=True),
        'date_deadline': fields.date('Deadline'),
        'date_closed': fields.datetime('Closed', readonly=True),
        'user_id11': fields.many2one('employee.type', 'Responsible Person', required=True),
        'designation': fields.char('Designation', size=64),
        'history_line': fields.one2many('crm.case.history', 'case_id', 'Communication'),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),
        'date_action_last': fields.datetime('Last Action', readonly=1),
        'date_action_next': fields.datetime('Next Action'),
        'question_yesterday': fields.text('Problems in Detail'),
        'question_today': fields.text('Suggestions'),
        'question_blocks': fields.text('Conclusion'),
        'ref' : fields.reference('Reference', selection=_links_get, size=128),
        'ref2' : fields.reference('Reference 2', selection=_links_get, size=128),
        'work_ids': fields.one2many('history.type', 'task_id', 'History'),
    }
    _defaults = {
#        'user_id11': lambda s,cr,uid,c={}: uid,
        'state': lambda *a: 'draft',
        'priority': lambda *a: AVAILABLE_PRIORITIES[2][0],
      #  'creat_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def onchange_user_id(self, cr, uid, ids, user_id11): 
          res = {} 
          print "ids::::name::::",ids,user_id11
          if user_id11:
              id = self.pool.get('employee.type').read(cr, uid, [user_id11])
              if id:
                  res = {'designation':id[0]['designation']}
              print "id:::::::;",id,res
          else:
             res = {'designation':0}   
          print "*************************************",res
          return {'value': res}
  #######################################33    


    def do_done(self, cr, uid, ids, *args):
        tasks= self.browse(cr,uid,ids)
        for t in tasks:
            self.write(cr, uid, [t.id], {'state': 'done', 'date_closed':time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    def do_cancel(self, cr, uid, ids, *args):
        tasks= self.browse(cr,uid,ids)
        for t in tasks:
            self.write(cr, uid, [t.id], {'state': 'cancelled'})
        return True
    
    def do_open(self, cr, uid, ids, *args):
        tasks= self.browse(cr,uid,ids)
        for t in tasks:
            self.write(cr, uid, [t.id], {'state': 'open','date_start':time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def do_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def do_pending(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

crm_meeting()

class history_type(osv.osv):
   _name = "history.type"
   _description = "History Details" 
   _columns = {
        'name': fields.char('Summary', size=128),
        'date': fields.datetime('Date'),
        'task_id': fields.many2one('crm.meeting', 'History', ondelete='cascade'),
        'hours': fields.float('Hours spent'),
        'user_id11': fields.many2one('employee.type', 'Done by', required=True),
                }
   _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }
   _order = "date desc"
history_type()

    