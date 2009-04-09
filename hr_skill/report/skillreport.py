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

class skillreport(report_sxw.rml_parse):
        def __init__(self, cr, uid, name, context):
                super(skillreport, self).__init__(cr, uid, name, context)
                self.localcontext.update({
                    'time' : time,
                    'get_data' : self._getData,
                    'get_skill':self._getskill,

                     })
        def _getskill(self,ids):
            res=[]
            t_ids=pooler.get_pool(self.cr.dbname).get('hr_skill.evaluation.skill').search(self.cr,self.uid,[('evaluation_id','=',ids)])
            res1=pooler.get_pool(self.cr.dbname).get('hr_skill.evaluation.skill').browse(self.cr,self.uid,t_ids)
            return res1

        def _getData(self,form):
                res=[]
                eval_id=[]
                emp_id=[]
                final=[]
                id = form['s_ids']
                if id:
                    self.cr.execute("select evaluation_id from hr_skill_evaluation_skill where skill_id=%d"%id)
                eval_id.append(self.cr.fetchall())

                for i in range(0,len(eval_id[0])):
                    res.append(eval_id[0][i][0])

                for i in range(0,len(res)):
                    final.append(pooler.get_pool(self.cr.dbname).get('hr_skill.evaluation').browse(self.cr,self.uid,res[i],))
                return final

report_sxw.report_sxw('report.skillreport','hr_skill.evaluation','addons/hr_skill/report/skillreport.rml',parser=skillreport,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

