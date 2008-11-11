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
import datetime
import operator
import pooler
import time
from report import report_sxw


class employeereport(report_sxw.rml_parse):
        def __init__(self, cr, uid, name, context):
                super(employeereport, self).__init__(cr, uid, name, context)
                self.localcontext.update({
                    'time': time,
                    'get_data' : self._getData,
                    'get_duration' : self._getDuration,
                    })
        def _getData(self,start_date,end_date):
                employee_ids = self.pool.get('hr.employee').search(self.cr,self.uid,[('started', '>=', start_date),('started', '<=', end_date)])
                res = self.pool.get('hr.employee').browse(self.cr,self.uid,employee_ids)
                return res

        def _getDuration(self,eid):
                    res1 = self.pool.get('hr.employee').read(self.cr,self.uid,eid,)
                    sdate=datetime.datetime.strptime(res1['started'],'%Y-%m-%d')
                    if res1['leavedate']:
                        edate=datetime.datetime.strptime(res1['leavedate'],'%Y-%m-%d')
                    else:
                        edate=datetime.datetime.now()
                    days=str(edate-sdate)
                    days=int(days.split(" ",1)[0])
                    months=days/30
                    month,year=months%12,months/12
                    res= str(year)+"."+str(month)+"years"
                    return res

report_sxw.report_sxw('report.datereport.print','hr.employee','addons/hr_skill/report/datereport.rml', parser=employeereport, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

