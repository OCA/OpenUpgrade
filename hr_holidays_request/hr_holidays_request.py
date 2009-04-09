# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from mx import DateTime
import time
import pooler
import netsvc
from osv import fields, osv
import datetime
import calendar
def _manager_get(obj,cr,uid,context={}):
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
    if ids:
        boss = obj.pool.get('hr.employee').read(cr, uid, ids)[0]['parent_id']
        if boss:
            return boss[0]
    return False
    
class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    _description = "Holidays"
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if len(args)==2:
            if (args[0]==['state', '=', 'confirm'] and args[1]==['employee_id',"=",[]]) or (args[0]==('state', '=', 'confirm') and args[1]==('employee_id',"=",[])):
                res=[]
                ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
                for id in ids:
                    boss = self.pool.get('hr.employee').search(cr, uid,[('parent_id','=',id)])
                    for b in boss:
                        res.append(b)
                        boss1 = self.pool.get('hr.employee').search(cr, uid,[('parent_id','=',b)]) 
                        for b1 in boss1:
                            boss.append(b1)
                args[1]=['employee_id','in',res]
        
        return super(hr_holidays,self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
    def copy(self, cr, uid, id, default=None, context={}):
        raise osv.except_osv('Duplicate Error !','Can not create duplicate record')
        return False
    def unlink(self, cr, uid, ids, context={}, check=True):
        for id in ids:
            selfobj=self.browse(cr,uid,id)
            if selfobj.state=="validate" or selfobj.state=="refuse":
                raise osv.except_osv('Data Error !','Can not Delete Validated or refused record')
        return super(hr_holidays, self).unlink(cr, uid, ids, context=context)
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        slobj=self.browse(cr,uid,ids)
        if vals.__contains__('date_from1'):
            d=vals['date_from1']
        else:
            for s in slobj:
                d=s.date_from1
        if vals.__contains__('date_to1'):
            dd=vals['date_to1']
        else :
            for s in slobj:
                dd=s.date_to1
        
        d1=d.split('-')
        d2=dd.split('-')
        d1[2]=d1[2].split(' ')
        d2[2]=d2[2].split(' ')
        a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
        b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
        if b<a:
            raise osv.except_osv('Date Error !','From date should be smaller than To date')
        return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
    def create(self, cr, uid, vals, context=None):
        d=vals['date_from1']
        dd=vals['date_to1']
        d1=d.split('-')
        d2=dd.split('-')
        d1[2]=d1[2].split(' ')
        d2[2]=d2[2].split(' ')
        a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
        b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
        if b<a:
            raise osv.except_osv('Date Error !','From date should be smaller than To date')
        else:
            return super(hr_holidays, self).create(cr, uid, vals, context=context)
    _columns = {
        'name' : fields.char('Description', required=True, readonly=True, size=64, states={'draft':[('readonly',False)],'draft1':[('readonly',False)]}),
        'state': fields.selection([('draft1', 'draft'),('draft', 'draft'), ('confirm', 'Requested'), ('refuse', 'Refused'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'State', readonly=True),
        'date_from' : fields.datetime('Vacation start day'),
        'date_to' : fields.datetime('Vacation end day'),
        'date_from1' : fields.date('From', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_to1' : fields.date('To', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'employee_id' : fields.many2one('hr.employee', 'Employee', select=True, readonly=True, required=True),
        'user_id':fields.many2one('res.users', 'User_id', states={'draft':[('readonly',False)],'draft1':[('readonly',False)]}, select=True, readonly=True),
        'manager_id' : fields.many2one('hr.employee', 'Holiday manager', invisible=False, readonly=True),
        'notes' : fields.text('Notes', readonly=True,states={'draft':[('readonly',False)],'draft1':[('readonly',False)]}),
        'contactno':fields.char("Contact no",size=64 , required=True, readonly=True,states={'draft':[('readonly',False)],'draft1':[('readonly',False)]}),
        'holiday_id':fields.one2many('days.holidays.days','holiday_id',"Holiday's days list", readonly=True,states={'draft':[('readonly',False)],'validate':[('readonly',False)]}),
        'total_half':fields.integer("Total Half Leave", readonly=True),
        'total_full':fields.integer("Total Full Leave", readonly=True),
        'total_hour':fields.integer("Total Hours", readonly=True),
        'number_of_days': fields.float('Number of Days in this Holiday Request'),
        'holiday_status' : fields.many2one("hr.holidays.status", "Holiday's Status"),
          }
    _defaults = {
        'manager_id' : _manager_get,
        'state' : lambda *a: 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'date_from1': lambda *a: time.strftime('%Y-%m-%d'),
        'date_to1': lambda *a: time.strftime('%Y-%m-%d'),
            }
    _order = 'date_from1 desc'

    def _onchange_from_date(self, cr, uid, ids, date_from1,date_to1):
        if date_from1>date_to1:
            return{'value':{'date_to1':date_from1}}
            
        else:
            return {'value':{}}
            
    def days_chaeck(self,cr,uid,ids,s1):
        print s1
        
        seaobj=self.pool.get('days.holidays.days').browse(cr,uid,s1)
        if seaobj.holiday_id.id:
            if not seaobj.holiday_id.id==ids[0]:
                
                if seaobj.holiday_id.state=='refuse':
                    return True
                else:
                    raise osv.except_osv('Day Error !','Can not create more leaves for one day ')
            else:
                return True
        else:
            return True
        
    def create_days(self, cr, uid, ids, *args):
        selfobj=self.browse(cr, uid, ids, None)
        for s in selfobj:
            d=s.date_from1
            dd=s.date_to1
            d1=d.split('-')
            d2=dd.split('-')
            d1[2]=d1[2].split(' ')
            d2[2]=d2[2].split(' ')
            a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
            b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
            temp=a
            if a>b:
                raise osv.except_osv('Date Error !','From date should be smaller than To date')
            t12=datetime.timedelta(days=1)
            dobj=self.pool.get('days.holidays.days')
            delobject=dobj.search(cr, uid, [('holiday_id', '=', ids[0])])
            for d in delobject:
                dobj.unlink(cr, uid,d)
            cr.execute("select name from public_holidays_days" )
            t=[]
            t=cr.fetchall()
            fd=1
            pd=0
            while (temp<=b):
                searchobject=self.pool.get('days.holidays.days').search(cr,uid,[('date1','like', temp.strftime("%Y-%m-%d")),('user_id',"=",uid)])
                
                for s1 in  searchobject:
                    if self.days_chaeck(cr, uid, ids, s1):
                        continue
                    else:
                        return False
                for t1 in t:
                    day=calendar.weekday(int(temp.strftime("%Y")),int(temp.strftime("%m")),int(temp.strftime("%d")))

                    if t1[0]==temp.strftime("%Y-%m-%d") :
                        if t1[0]==a.strftime("%Y-%m-%d") or t1[0]==b.strftime("%Y-%m-%d") : 
                            pd=1
                            fd=0
                            break
                        else:
                            pd=1
                            fd=1
                    else:
                        pd=0
                        fd=1
                    if day==6:
                        if temp.strftime("%Y-%m-%d")==a.strftime("%Y-%m-%d") or temp.strftime("%Y-%m-%d")==b.strftime("%Y-%m-%d") :
                            fd=0
                            pd=1
                        else:
                            fd=1
                            pd=1
                self.write(cr, uid, ids, {'state':'draft1'})    
                self.pool.get('days.holidays.days').create(cr,uid,{
                      'name':temp,
                      'date1':temp,
                      'half_day':0,
                      'full_day':fd,
                      'hourly_leave':0,
                      'holiday_id':ids[0],
                      'public_h':pd,
                      'holiday_status':0,
                      'user_id':uid,
                      'state':'draft',
                      
                          })
                
                temp+=t12
                
                
        return True
    def days_count(self, cr, uid, ids, *args):
        selfobj=self.browse(cr, uid, ids, None)
        for s in selfobj:
           
            d=s.date_from1
            dd=s.date_to1
            d1=d.split('-')
            d2=dd.split('-')
            d1[2]=d1[2].split(' ')
            d2[2]=d2[2].split(' ')
            a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
            b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
            if b >= a:
                t1=datetime.timedelta(days=1)
                temp=b-a+t1
                
                if temp == t1:
                    return False
                elif temp >t1:
                    return True
                else:
                    return False
            else:
                raise osv.except_osv('Date Error !','From date should be smaller than To date')
            
    def set_to_draft(self, cr, uid, ids, *args):

         self.write(cr, uid, ids, {
             'state':'draft'
             })
         return True
    def write_data(self,cr,uid,ids,*args):
        selfobj=self.browse(cr, uid, ids, None)
        full=0
        half=0
        hl=0
        for s in selfobj:
            sid=self.pool.get('hr.holidays.history').create(cr,uid,{'validated_id':uid,'name':s.name,'state':s.state,'date_from1':s.date_from1,'date_to1':s.date_to1,'employee_id':s.employee_id.id,'user_id':s.user_id.id,'manager_id':s.manager_id.id,'notes':s.notes,'contactno':s.contactno,'total_half':s.total_half,'total_full':s.total_half})
            for s1 in s.holiday_id:
                self.pool.get('days.holidays.days').write(cr,uid,s1.id,{'state':s.state})
                ss1=self.pool.get('days.holidays.days').browse(cr,uid,s1.id)
                
                if ss1.full_day:
                    full+=1
                if ss1.half_day:
                    half+=1
                if ss1.hourly_leave >0:
                    hl+=ss1.hourly_leave
                self.pool.get('days.holidays.days.history').create(cr,uid,{'user_id':ss1.user_id.id,'state':ss1.state,'name':ss1.name,'date1':ss1.name,'half_day':ss1.half_day,'full_day':ss1.full_day,'hourly_leave':ss1.hourly_leave,'holiday_id':sid,'public_h':ss1.public_h,'holiday_status':ss1.holiday_status})
            self.write(cr, uid, ids, {'total_hour':hl})
            self.write(cr, uid, ids, {'total_half':half})
            self.write(cr, uid, ids, {'total_full':full})
            self.pool.get('hr.holidays.history').write(cr, uid, sid, {'total_half':half})
            self.pool.get('hr.holidays.history').write(cr, uid, sid, {'total_full':full})
            self.pool.get('hr.holidays.history').write(cr, uid, sid, {'total_hour':hl})
            
    def holidays_validate(self, cr, uid, ids, *args):
        
            self.write(cr, uid, ids, {'state':'validate'})
            self.write_data(cr, uid, ids)
            return True
    
    def holidays_confirm(self, cr, uid, ids, *args):
        selfobject=self.browse(cr, uid, ids, None)
        full=0
        half=0
        hl=0
        for selfobj in selfobject:
            
            recids=self.pool.get('days.holidays.days').search(cr,uid,[('holiday_id','=', selfobj.id)])
            
            if recids==[]:
                raise osv.except_osv('Day Error !','Create Day list')
            for rec in recids:
                if self.days_chaeck(cr, uid, ids, rec):
                    recobj=self.pool.get('days.holidays.days').browse(cr,uid,rec)
                    self.pool.get('days.holidays.days').write(cr,uid,rec,{'state':'confirm'})
                    flg=0
                    if recobj.half_day==1:
                        half+=1
                        flg=1
                    if recobj.full_day==1:
                        full+=1
                        flg=1
                    if recobj.public_h==1:
                        flg=1
                    if recobj.hourly_leave > 0:
                        hl+=recobj.hourly_leave
                        flg=1
                    if flg==0:
                        raise osv.except_osv('Leave Error !','Select Leave type')
                else:
                    return False
            
            self.write(cr, uid, ids, {
                     'state':'confirm',
                     'total_half':half,
                     'total_full':full,
                     'total_hour':hl
                     })
            return True
            

    def holidays_refuse(self, cr, uid, ids, *args):
        
        self.write(cr, uid, ids, {'state':'refuse'})
        self.write_data(cr, uid, ids)
        return True


    def holidays_cancel(self, cr, uid, ids, *args):
        
        self.write(cr, uid, ids, {
            'state':'cancel'
            })
        return True

    def holidays_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state':'draft'
            })
        selfobj=self.browse(cr, uid, ids, None)
        for s in selfobj:
            for s1 in s.holiday_id:
                self.pool.get('days.holidays.days').write(cr,uid,s1.id,{'state':draft})
        
        
        return True

hr_holidays()

class holiday_history(osv.osv):
    _name = 'hr.holidays.history'
    _description = "Holidays history"
    _columns = {
                'validated_id':fields.many2one('res.users', 'Validated By', readonly=True),
                'name' : fields.char('Description',  readonly=True, size=64),
                'state': fields.selection([('draft', 'draft'), ('confirm', 'Requested'), ('refuse', 'Refused'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'State', readonly=True),
                'date_from1' : fields.date('From', readonly=True),
                'date_to1' : fields.date('To', readonly=True),
                'employee_id' : fields.many2one('hr.employee','Employee',readonly=True),
                'user_id':fields.many2one('res.users', 'Employee_id',readonly=True),
                'manager_id' : fields.many2one('hr.employee', 'Holiday manager', readonly=True),
                'notes' : fields.text('Notes',readonly=True),
                'contactno':fields.char("Contact no",size=64,readonly=True),
                'holiday_id':fields.one2many('days.holidays.days.history','holiday_id',"Holiday's days list",readonly=True),
                'total_half':fields.integer("Total Half Leave", readonly=True),
                'total_full':fields.integer("Total Full Leave", readonly=True),
                'total_hour':fields.integer("Total Hours", readonly=True),
                }
holiday_history()

class  holiday_days(osv.osv):
    
    _name='days.holidays.days'
    _description = "Holidays history"
    _columns = {
                 'name':fields.char("Date",size=64),
                 'date1':fields.date('Date', readonly=True,required=True),
                 'half_day' : fields.boolean('Half Leave', readonly=True,states={'draft':[('readonly',False)]}),
                 'full_day' : fields.boolean('Full Leave', readonly=True,states={'draft':[('readonly',False)]}),
                 'hourly_leave':fields.float("Hourly Leave", readonly=True,states={'draft':[('readonly',False)]}),
                 'holiday_id':fields.many2one("hr.holidays","Holiday Ref"),
                 'public_h':fields.boolean('Public Holiday',readonly=True),
                 'holiday_status':fields.many2one("hr.holidays.status", "Holiday's Status"),
                 'user_id':fields.many2one('res.users', 'User_id',readonly=True),
                 'state': fields.selection([('draft1', 'draft'),('draft', 'draft'), ('confirm', 'Requested'), ('refuse', 'Refused'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'State', readonly=True),
                 }
    _order = 'date1'
    _defaults = {
                 'state' : lambda *a: 'refuse',
                 }
    
    def _onchange_half_day(self, cr, uid, ids, half_day,full_day,hourly_leave,public_h):
       if public_h==1:
           return {'value':{'full_day':1,'half_day':0,'hourly_leave':0}}
       if half_day==1 and full_day==1:
           full_day=0
       if half_day==1 and hourly_leave>0:
           hourly_leave=0
       return {'value':{'full_day':full_day,'hourly_leave':hourly_leave}}
    def _onchange_full_day(self, cr, uid, ids, half_day,full_day,hourly_leave,public_h):
       if public_h==1:
           return {'value':{'full_day':1,'half_day':0,'hourly_leave':0}}
       if half_day==1 and full_day==1:
           half_day=0
       if half_day==1 and hourly_leave>0:
           hourly_leave=0
       return {'value':{'half_day':half_day,'hourly_leave':hourly_leave}}
    def _onchange_hourly_leave(self, cr, uid, ids, half_day,full_day,hourly_leave,public_h):
       if public_h==1:
           return {'value':{'full_day':1,'half_day':0,'hourly_leave':0}}
       if half_day==1 and hourly_leave>0:
           half_day=0
       if full_day==1 and hourly_leave>0:
           full_day=0
       return {'value':{'full_day':full_day,'half_day':half_day}}
holiday_days()

class  public_holiday_days(osv.osv):
    _name='public.holidays.days'
    _description = "Public Holidays"
    _columns = {
                 'name':fields.date('Date',required=True),
                 'reason':fields.text("Reason",required=True),
                 }
public_holiday_days()
class  holiday_days_history(osv.osv):
    def _holidaystatus_get(self, cr, uid, context={}):
        obj = self.pool.get('hr.holidays.status')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name'], context)
        res = [(r['id'], r['name']) for r in res]
        return res 
    _name='days.holidays.days.history'
    _description = "Holidays history"
    _columns = {
                 'name':fields.char("Date",size=64,readonly=True),
                 'date1':fields.date('Date',readonly=True),
                 'half_day' : fields.boolean('Half Leave',readonly=True),
                 'full_day' : fields.boolean('Full Leave',readonly=True),
                 'hourly_leave':fields.float("Hourly Leave",readonly=True),
                 'holiday_id':fields.many2one("hr.holidays.history","Holiday Ref",readonly=True),
                 'public_h':fields.boolean('Public Holiday',readonly=True),
                 'holiday_status':fields.selection(_holidaystatus_get, "Holiday's Status",readonly=True),
                 'user_id':fields.many2one('res.users', 'User_id',readonly=True),
                 'state': fields.selection([('draft1', 'draft'),('draft', 'draft'), ('confirm', 'Requested'), ('refuse', 'Refused'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'State', readonly=True),
                 }
holiday_days_history()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

