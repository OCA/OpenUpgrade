# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 EVERLIBRE.  All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
import datetime

from report import report_sxw

class regimecaisse(report_sxw.rml_parse):
    total=0
    def __init__(self, cr, uid, name, context):
        super(regimecaisse, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            '_lines':self._lines,
            '_lines_resident':self._lines_resident,
            'total':self._total,
        })
        self.context = context
        return None
    def _lines_resident(self,form):
            res = []
            regime_obj = self.pool.get('health.regime')
            patient_obj = self.pool.get('health.patient')
            regime= regime_obj.search(self.cr,self.uid,[],0)
            for a in regime:
                patient_ids=patient_obj.search(self.cr, self.uid, [('regime','=',a),('admission_date','<=',form['date'])])
                regime_record=regime_obj.read(self.cr, self.uid,a)
                if len(patient_ids) >0:
                    res.append({'regime':regime_record['name'],'resident':"",'entree':"",'secu':""})
                    for id in patient_ids:
                        resident_record=patient_obj.read(self.cr, self.uid,id)
                        res.append({'regime':"",'resident':resident_record['name'],'secu':resident_record['numerosecu'],'entree':resident_record['admission_date']})
                        
            return res
    def _total(self,form):
        return self.total
    def _lines(self, form):
            res = []
            regime_obj = self.pool.get('health.regime')
            patient_obj = self.pool.get('health.patient')
            regime= regime_obj.search(self.cr,self.uid,[],0)

            for a in regime:
                patient_ids=patient_obj.search(self.cr, self.uid, [('regime','=',a),('admission_date','<=',form['date'])])
                regime_record=regime_obj.read(self.cr, self.uid,a)
                if len(patient_ids) >0:
                    res.append({'regime':regime_record['name'],'effectifs':len(patient_ids)})
                    self.total=self.total+len(patient_ids)
            return res
    

    

report_sxw.report_sxw('report.health.regimecaisse.report', 'health.patient','addons/health/report/regimecaisse.rml', parser=regimecaisse, header=False)

