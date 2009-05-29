# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 EVERLIBRE.  All Rights Reserved.
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

class entreesortie(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(entreesortie, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            '_entree':self._entree,
            '_sortie':self._sortie,
            '_absences':self._absences,
            'age':self.age,
        })
        self.context = context
        return None
    def _entree(self,form):
            res = []
            patient_obj = self.pool.get('health.patient')
            patient_ids = patient_obj.search(self.cr,self.uid,[ ('active','in', ['f','t'])])
            for a in patient_obj.read(self.cr, self.uid, patient_ids, ['name', 'room_id','provenance','date_sortie','motif_sortie','admission_date','girage']):
                if a['admission_date']:
                    anneeadmission=int(a['admission_date'][0:4])
                    moisadmission=int(a['admission_date'][5:7])
                    jouradmission = int(a['admission_date'][8:10])
            
                    anneeperiodedebut=int(form['datedebut'][0:4])
                    anneeperiodefin=int(form['datefin'][0:4])
                    moisperiodedebut=int(form['datedebut'][5:7])
                    moisperiodefin=int(form['datefin'][5:7])
                    jourperiodedebut = int(form['datedebut'][8:10])
                    jourperiodefin = int(form['datefin'][8:10])
                
                    periodefin=datetime.datetime(anneeperiodefin,moisperiodefin,jourperiodefin) 
                    periodedebut=datetime.datetime(anneeperiodefin,moisperiodedebut,jourperiodedebut) 
                    admission=datetime.datetime(anneeadmission,moisadmission,jouradmission) 
                    if a['motif_sortie']:
                        destination=a['motif_sortie'][1]
                    else:
                        destination=""
                    if a['room_id']:
                        chambre=a['room_id'][1]
                    else:
                        chambre = "Non defini"
                    if (admission <= periodefin) and (admission >=periodedebut):
                        res.append({'name':a['name'],'chambre':chambre,'entree':a['admission_date'],'provenance':a['provenance'],'sortie':a['date_sortie'],'destination':destination,'gir':a['girage']})
            res.sort(lambda x, y: cmp(x['name'],y['name']))
            return res
    def _sortie(self,form):
            res = []
            patient_obj = self.pool.get('health.patient')
            patient_ids = patient_obj.search(self.cr,self.uid,[ ('active','in', ['f','t'])])
            for a in patient_obj.read(self.cr, self.uid, patient_ids, ['name', 'active','room_id','provenance','date_sortie','motif_sortie','admission_date','girage']):
                if a['date_sortie']:
                    anneesortie=int(a['date_sortie'][0:4])
                    moissortie=int(a['date_sortie'][5:7])
                    joursortie = int(a['date_sortie'][8:10])
                    anneeperiodedebut=int(form['datedebut'][0:4])
                    anneeperiodefin=int(form['datefin'][0:4])
                    moisperiodedebut=int(form['datedebut'][5:7])
                    moisperiodefin=int(form['datefin'][5:7])
                    jourperiodedebut = int(form['datedebut'][8:10])
                    jourperiodefin = int(form['datefin'][8:10])
                    if a['room_id']:
                        chambre=a['room_id'][1]
                    else:
                        chambre = "Non defini"
                    if a['motif_sortie']:
                        destination=a['motif_sortie'][1]
                    else:
                        destination=""

                    periodefin=datetime.datetime(anneeperiodefin,moisperiodefin,jourperiodefin) 
                    periodedebut=datetime.datetime(anneeperiodefin,moisperiodedebut,jourperiodedebut) 
                    sortie=datetime.datetime(anneesortie,moissortie,joursortie) 
                    if (sortie <= periodefin) and (sortie >=periodedebut):
                        res.append({'name':a['name'],'chambre':chambre,'entree':a['admission_date'],'provenance':a['provenance'],'sortie':a['date_sortie'],'destination':destination,'gir':a['girage']})
            res.sort(lambda x, y: cmp(x['name'],y['name']))
            return res

    def _absences(self,form):
            res = []
            absences_obj = self.pool.get('health.absences')
            abs_ids = absences_obj.search(self.cr,self.uid,[('du','>=',form['datedebut']),('du','<=',form['datefin'])])+absences_obj.search(self.cr,self.uid,[('au','>=',form['datedebut']),('au','<=',form['datefin'])])
            absences = absences_obj.read(self.cr,self.uid,abs_ids)
            patient_obj = self.pool.get('health.patient')
            for ab in absences:
                for a in patient_obj.read(self.cr, self.uid, [ab['partner_id'][0]]):
                    if ab['categorie'] == '1' :
                        motif= 'Hospitalisation'
                    if ab['categorie'] == '2' :
                        motif= 'Convenance Personelle'
                    if ab['categorie'] == '3' :
                        motif= 'Autres'
                    if a['room_id']:
                        chambre=a['room_id'][1]
                    else:
                        chambre = "Non defini"

                    res.append({'name':a['name'],'chambre':chambre,'entree':ab['du'],'sortie':ab['au'],'motif_sortie':motif,'gir':a['girage']})
            res.sort(lambda x, y: cmp(x['name'],y['name']))
            return res
    
    def age(self,annee,annee2):
        return int(annee[0:4])-int(annee2[0:4])

    

report_sxw.report_sxw('report.health.entreesortie.report', 'health.patient','addons/health/report/entreesortie.rml', parser=entreesortie, header=False)

