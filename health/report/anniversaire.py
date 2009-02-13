# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 EVI.  All Rights Reserved.
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

class anniversaire(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(anniversaire, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            '_lines':self._lines,
            'age':self.age,
        })
        self.context = context
        return None

    def _lines(self, form):
            res = []
            patient_obj = self.pool.get('health.patient')
            patient_ids = patient_obj.search(self.cr,self.uid,[('category_id','=','Résident')])
            for a in patient_obj.read(self.cr, self.uid, patient_ids, ['name', 'birthdaydate']):
                moisanniv=int(a['birthdaydate'][5:7])
                jouranniv = int(a['birthdaydate'][8:10])
                anneeperiodedebut=int(form['datedebut'][0:4])
                anneeperiodefin=int(form['datefin'][0:4])
                moisperiodedebut=int(form['datedebut'][5:7])
                moisperiodefin=int(form['datefin'][5:7])
                jourperiodedebut = int(form['datedebut'][8:10])
                jourperiodefin = int(form['datefin'][8:10])
                periodefin=datetime.datetime(anneeperiodefin,moisperiodefin,jourperiodefin)
                periodedebut=datetime.datetime(anneeperiodefin,moisperiodedebut,jourperiodedebut)
                anniv=datetime.datetime(anneeperiodefin,moisanniv,jouranniv)
                if (anniv <= periodefin) and (anniv >=periodedebut):
                    age= self.age(form['datedebut'],a['birthdaydate'])
                    res.append({'name':a['name'],'datenaissance':a['birthdaydate'],'age':age})
            res.sort(lambda x, y: cmp(x['name'],y['name']))
            return res

    def age(self,annee,annee2):
        return int(annee[0:4])-int(annee2[0:4])



report_sxw.report_sxw('report.health.anniversaire.report', 'health.patient','addons/health/report/anniversaire.rml', parser=anniversaire, header=False)

