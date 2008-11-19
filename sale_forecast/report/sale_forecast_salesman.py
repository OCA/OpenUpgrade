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


import time
from report import report_sxw
import datetime
import pooler


class sale_forecast_salesman(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_forecast_salesman, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'get_data':self._get_data,
            'get_salesman' : self._get_salesman,

         })
        self.context=context

    def _get_salesman(self,id):
        tids = self.pool.get('res.users').search(self.cr,self.uid,[('id', '=',id)])
        res = self.pool.get('res.users').browse(self.cr,self.uid,tids)
        return res[0]['name']

    def _get_data(self,form):
        d1=form['date_start']
        d2=form['date_end']
        s=form['user_id']
        data={}
        self.cr.execute("select sf.name as date, rs.name as user_name, " \
                        "sfl.user_id,sfl.computation_type,sfl.amount, " \
                        "sfl.computed_amount,sfl.final_evolution " \
                        "FROM  res_users as rs, sale_forecast as sf " \
                        "inner join sale_forecast_line as sfl on sf.id=sfl.forecast_id " \
                        "WHERE sf.name >= %s and sf.name <= %s  " \
                            " AND sfl.user_id= %d " \
                            " AND rs.id= %d " \
                            ,(form['date_start'],form['date_end'],form['user_id'],form['user_id']))

        data=self.cr.dictfetchall()
        return data

report_sxw.report_sxw('report.sale.forecast.salesman', 'sale.forecast.line', 'addons/sale_forecast/report/sale_forecast_salesman.rml',parser= sale_forecast_salesman,header=False)