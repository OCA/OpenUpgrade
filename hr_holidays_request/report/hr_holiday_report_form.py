# -*- encoding: utf-8 -*-
import time
from report import report_sxw
import calendar
import datetime

class hr_holiday_report_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hr_holiday_report_form, self).__init__(cr, uid, name, context)
        self.half=0
        self.hl=0
        self.localcontext.update({
            'time': time,
            'total_days':self._total_days,
            'total_full':self._total_full,
            'total_half':self._total_half,
            'total_hourly':self._total_hourly,       
        
        })
    def _total_days(self,full,half,hours):
        total=0.0
        total+=full
        total+=(float(half)/float(2))
        total+=(float(hours)/float(8))
        return total
    def _total_full(self,object,emp):
        lst=object.date_from1.split('-')
        
        year=int(lst[0])
        month=int(lst[1])
        startdate=str(datetime.date(year,month,1))
        a=calendar.monthrange(year,month)
        enddate=str(datetime.date(year,month,a[1]))
        self.half=0
        full=0
        self.hl=0
        hr_pool = self.pool.get('hr.holidays')
        day_pool = self.pool.get('days.holidays.days')
        hr_ids = hr_pool.search(self.cr,self.uid,[('employee_id', '=',emp.id)])
        for hrid in hr_ids:
            if hrid==object.id:
                continue
            hr_obj=hr_pool.browse(self.cr,self.uid,hrid)
            day_ids = day_pool.search(self.cr,self.uid,[('holiday_id', '=',hrid)])
            for did in day_ids:
                day_obj=day_pool.browse(self.cr,self.uid,did)
                if day_obj.date1>=startdate and day_obj.date1<=enddate and hr_obj.state=='validate':
                    if day_obj.half_day==1:
                        self.half+=1
                    if day_obj.full_day==1:
                        full+=1
                    if day_obj.hourly_leave > 0:
                        self.hl+=day_obj.hourly_leave
        return full
    def _total_half(self,object,emp):
        return self.half
    def _total_hourly(self,object,emp):
        return self.hl
report_sxw.report_sxw('report.hr_holiday_report_form', 'hr.holidays', 'addons/hr_holidays_request/report/hrreport_form.rml' ,parser=hr_holiday_report_form)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

