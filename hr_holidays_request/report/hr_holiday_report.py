# -*- encoding: utf-8 -*-
import time
from report import report_sxw
import calendar
import datetime

class hr_holiday_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hr_holiday_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line' : self._getShop,
            
        })
    def _getShop(self,form):
        if form['active1']:
            startdate=str(datetime.date(form['year'],form['month'],1))
            a=calendar.monthrange(form['year'],form['month'])
            enddate=str(datetime.date(form['year'],form['month'],a[1]))
            
        elif form['active2']:
            
            startdate=form['fromdate']
            enddate=form['todate']
        ls=[]
        res={}
        half=0
        full=0
        hl=0
        total=0.0
        for li in form['emp_ids'][0][2]:
            hr_pool = self.pool.get('hr.holidays')
            day_pool = self.pool.get('days.holidays.days')
            hr_ids = hr_pool.search(self.cr,self.uid,[('employee_id', '=',li)])
            for hrid in hr_ids:
                hr_obj=hr_pool.browse(self.cr,self.uid,hrid)
                day_ids = day_pool.search(self.cr,self.uid,[('holiday_id', '=',hrid)])
                for did in day_ids:
                    day_obj=day_pool.browse(self.cr,self.uid,did)
                    if day_obj.date1>=startdate and day_obj.date1<=enddate and hr_obj.state=='validate':
                        if day_obj.half_day==1:
                            half+=1
                        if day_obj.full_day==1:
                            full+=1
                        if day_obj.hourly_leave > 0:
                            hl+=day_obj.hourly_leave
            emp=self.pool.get('hr.employee').browse(self.cr,self.uid,li)
            user=self.pool.get('res.users').browse(self.cr,self.uid,emp.user_id.id)
            res['emp_name']=emp.name
            res['total_full']=full
            res['total_half']=half
            res['total_hour']=hl
            res['user_name']=user.login
            total+=full
            total+=(float(half)/float(2))
            total+=(float(hl)/float(8))
            res['total']=total
            total=0.0
            half=0
            full=0
            hl=0
            ls.append(res)
            res={}
        
        return ls
                    
                
        
report_sxw.report_sxw('report.hr.holiday.req.report', 'hr.holidays', 'addons/hr_holidays_request/report/hrreport.rml' ,parser=hr_holiday_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

