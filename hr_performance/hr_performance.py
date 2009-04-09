from osv import fields,osv
import datetime
import time
from mx.DateTime import *

class hr_performance(osv.osv):
    
    def create(self, cr, uid, vals, context=None):
        date_from=vals['date_from']
        date_to=vals['date_to']
        d1=date_from.split('-')
        d2=date_to.split('-')
        d1[2]=d1[2].split(' ')
        d2[2]=d2[2].split(' ')
        a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
        b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
        if b<a:
            raise osv.except_osv('Date Error !','From date should be smaller than To date')
        else:
            return super(hr_performance, self).create(cr, uid, vals, context=context)
        
    
    def write(self, cr, uid, ids, vals, context=None):
        
        review_obj=self.browse(cr,uid,ids)
        
        if vals.__contains__('date_from'):
            date_from=vals['date_from']
        else:
            for s in review_obj:
                date_from=s.date_from
                
        if vals.__contains__('date_to'):
            date_to=vals['date_to']
        else :
            for s in review_obj:
                date_to=s.date_to

        d1=date_from.split('-')
        d2=date_to.split('-')
        d1[2]=d1[2].split(' ')
        d2[2]=d2[2].split(' ')
        a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
        b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
        
        if b<a:
            raise osv.except_osv('Date Error !','From date should be smaller than To date')
        return super(hr_performance, self).write(cr, uid, ids, vals, context=context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        res=[]
        search_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
  
        for search_id in search_ids:
            child_ids = self.pool.get('hr.employee').search(cr, uid,[('parent_id','in',search_ids)])
            for b in child_ids:
                res.append(b)
  
        ids1=super(hr_performance,self).search(cr,uid,[('reviewer_id','in',res),('state','=','done')])
                  
        res2 = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        boss = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid),('parent_id','=',False)])
  
        if boss:
            ids2=super(hr_performance,self).search(cr,uid,[('reviewer_id','in',res2)])
        else:
            ids2=super(hr_performance,self).search(cr,uid,[('reviewer_id','in',res2),('state','!=','done')])

        ids=ids1+ids2
  
        if ids:
            args1=args
            if len(args1) > 2:
                args1=args1[0:-2]
                args=[('id','in',ids)]+args1
        else:   
            args=[('id','in',ids)]
              
        return super(hr_performance,self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
          
    def _check_date(self, cr, uid, ids):
        for r in self.browse(cr, uid, ids):
            cr.execute('SELECT id \
                    FROM hr_performance \
                    WHERE (date_from <= %s and %s <= date_to) \
                        AND reviewer_id=%d \
                        AND id <> %d', (r.date_to, r.date_from,
                            r.reviewer_id.id, r.id))
            if cr.fetchall():
                return False
        return True       
     
    def fill_employee_list(self, cr, uid, ids, *args):
        res=[]
        search_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        
        for search_id in search_ids:
            boss = self.pool.get('hr.employee').search(cr, uid,[('parent_id','in',search_ids)])
            for b in boss:
                res.append(b)
                
        for emp_id in res:
            pl_id=self.pool.get('hr.performance.line').create(cr, uid, {
            'employee_id': emp_id,
            'performance_id':ids[0]
            },context={'from_btn':True})
            
            att_ids = self.pool.get('hr.performance.line.attribute').search(cr, uid,[])
            
            for attribute_id in att_ids:
                att_obj=self.pool.get('hr.performance.line.attribute').browse(cr, uid,attribute_id, *args)
                self.pool.get('attribute.line').create(cr, uid, {
                        'attribute_id': attribute_id,
                        'performance_line_id':pl_id,
                        'total_marks':att_obj.total_point,
                        'obtained_marks':0 },context={'from_btn':True})
        return self.write(cr, uid, ids, {'state':'saved'})
    
    def change_sate(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'done'})
        return True
        
    def _employee_get(self,cr,uid,context={}):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        if ids:
            return ids[0]
        return False

    _name="hr.performance"
    _description="Employee Performance "
    _columns={
        'name':fields.char('Description',size=64),  
        'reviewer_id':fields.many2one('hr.employee','Employee',readonly=True),
        'date_from':fields.date('Date From',  required=True,select=True),
        'date_to':fields.date('Date To',required=True,select=True),
        'state':fields.selection([('new','New'),('saved','Saved'),('done','Confirmed')],'State',readonly=True),
        'performance_id':fields.one2many('hr.performance.line','performance_id','Performance'),
        'user_id' : fields.many2one('res.users', 'User', readonly=True)
    }

    _defaults={
      'reviewer_id': _employee_get,
      'state': lambda *a : 'new',
      'user_id': lambda obj, cr, uid, context: uid,
    }
    _constraints = [
        (_check_date, 'You can not have 2 Review that overlaps !', ['date_from','date_to']),
    ] 
hr_performance()

class hr_performance_line(osv.osv):
    
    def _get_total(self, cr, uid, ids, name, arg, context={}):
     res = {}
     for self_obj in self.browse(cr,uid,ids):
         total=0
         for re_po in self_obj.attribute_line:
             total+=re_po.obtained_marks
         res[self_obj.id]=total
     return res   
    
    def _get_performance(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for self_obj in self.browse(cr,uid,ids):
             total_obtained=0
             total_marks=0
             for re_po in self_obj.attribute_line:
                 total_obtained+=re_po.obtained_marks
                 total_marks+=re_po.total_marks
             if total_marks > 0:
                 res[self_obj.id]=(total_obtained*100)/(total_marks)
             else:  
                 res[self_obj.id]=0
        return res
    
    _name="hr.performance.line"
    _description="Performance Review Points"
    _columns={
        'name':fields.char('Description',size=64),  
        'employee_id':fields.many2one('hr.employee','Employee',readonly=True,required=True),
        'attribute_line':fields.one2many('attribute.line','performance_line_id','Attributes'),
        'performance_id':fields.many2one('hr.performance','Review Point'),
        'total':fields.function(_get_total,method=True,string='Total'),
        'performance':fields.function(_get_performance,method=True,string='Performance in (%)'),
    } 
hr_performance_line()

class hr_performance_line_attribute(osv.osv):
    _name="hr.performance.line.attribute"
    _description="Review Attributes"
    _columns={
        'name':fields.char('Attribute Name', size=1024, select=True, required=True),
        'note':fields.text('Description'),
        'total_point':fields.integer('Total Point',required=True)
    }
    _sql_constraints = [
        ('uniq_name', 'unique (name)', 'The name of the Attribute must be unique !')
    ]
hr_performance_line_attribute() 

class attribute_line(osv.osv):    
    def change_obtain_marks(self,cr,uid,ids,tot_mark,obtain_mark):
        if obtain_mark > tot_mark or obtain_mark < 0:
            raise osv.except_osv('Validation Error !','Obtained Marks Should be from  0 to '+ str(int(tot_mark)) +'')
        return {}
            
    def write(self, cr, uid, ids, vals, context=None):
        for self_obj in self.browse(cr,uid,ids):
          if vals.__contains__('obtained_marks'):  
            if vals['obtained_marks'] > self_obj.total_marks or vals['obtained_marks'] < 0:
                raise osv.except_osv('Validation Error !','Obtained Marks Should be from  0 to '+ str(int(self_obj.total_marks)) +'')
            return super(attribute_line, self).write(cr, uid, ids, vals, context=context)
        
    _name="attribute.line"
    _description="Attributes Lines"
    _columns={
        'name':fields.char('Description',size=64),  
        'attribute_id':fields.many2one('hr.performance.line.attribute','Attribute',readonly=True,required=True),
        'total_marks':fields.float('Total Marks',digits=(4,2),readonly=True),
        'obtained_marks':fields.float('Obtained Marks',digits=(4,2),required=True),
        'description':fields.text('Description'),
        'performance_line_id':fields.many2one('hr.performance.line','Performance Line',readonly=True),
    }
attribute_line()  



       