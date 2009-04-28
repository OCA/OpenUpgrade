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

class mouvementsemestriel(report_sxw.rml_parse):
    semestre={}
    au=''
    def __init__(self, cr, uid, name, context):
        super(mouvementsemestriel, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'mouvements':self.mouvements,
            'def_semestre':self.def_semestre,
            'semestre':self.semestre,
            
        })
        self.context = context
        return None
    
    def def_semestre(self,form):
        semestre_obj = self.pool.get('health.semestre')
        self.semestre =semestre_obj.read(self.cr,self.uid,form['semestre'])
        date_start=self.semestre['date_start']
        date_stop=self.semestre['date_stop']
        form['du']=date_start[8:10]+"/"+date_start[5:7]+"/"+date_start[0:4] 
        form['au']=date_stop[8:10]+"/"+date_stop[5:7]+"/"+date_stop[0:4]
        
        return []
     
    def mouvements(self,form):
            
            res = []
            patient_obj = self.pool.get('health.patient')
            anneeperiodedebut=int(self.semestre['date_start'][0:4])
            anneeperiodefin=int(self.semestre['date_stop'][0:4])
            moisperiodedebut=int(self.semestre['date_start'][5:7])
            moisperiodefin=int(self.semestre['date_stop'][5:7])
            jourperiodedebut = int(self.semestre['date_start'][8:10])
            jourperiodefin = int(self.semestre['date_stop'][8:10])
        
            periodefin=datetime.datetime(anneeperiodefin,moisperiodefin,jourperiodefin) 
            periodedebut=datetime.datetime(anneeperiodefin,moisperiodedebut,jourperiodedebut)
            patient_ids = patient_obj.search(self.cr,self.uid,[ ('active','in', ['f','t'])])
            for a in patient_obj.read(self.cr, self.uid, patient_ids):
                if a['admission_date']:
                    anneeadmission=int(a['admission_date'][0:4])
                    moisadmission=int(a['admission_date'][5:7])
                    jouradmission = int(a['admission_date'][8:10])
                    if a['date_sortie']:
                        anneesortie=int(a['date_sortie'][0:4])
                        moissortie=int(a['date_sortie'][5:7])
                        joursortie = int(a['date_sortie'][8:10])
                        sortie=datetime.datetime(anneesortie,moissortie,joursortie)
                    else:
                        sortie=datetime.datetime(9999,12,31)
            
                     
                    admission=datetime.datetime(anneeadmission,moisadmission,jouradmission)
                    absences_obj = self.pool.get('health.absences')
                    abs_ids = absences_obj.search(self.cr,self.uid,[('partner_id','=',a['id']),('du','>=',self.semestre['date_start']),('du','<=',self.semestre['date_stop'])])+absences_obj.search(self.cr,self.uid,[('partner_id','=',a['id']),('au','>=',self.semestre['date_start']),('au','<=',self.semestre['date_stop'])])
                    if abs_ids :
                        for abs in  absences_obj.read(self.cr,self.uid,abs_ids):
                            print abs['categorie']
                            if abs['categorie']=='1':
                                raison = "Hospitalisation"
                            elif abs['categorie']=='2':
                                raison = "Convenance Personnelle"
                            else:
                                raison = "Autres raisons"
			    print  abs	
                            if abs["du"] and abs["au"]:
				    absences = "du " + time.strftime('%d/%m/%Y', time.strptime(abs["du"], '%Y-%m-%d'))+" au "+time.strftime('%d/%m/%Y', time.strptime(abs["au"], '%Y-%m-%d'))+" pour " +raison+"\n"
                    else:
                        absences = ''
                    if a['motif_sortie']:
                        destination=a['motif_sortie'][1]
                    else:
                        destination=""
                    if a['numerosecu']:
                        nsecu=a['numerosecu'][1]
                    else:
                        nsecu = ""
                    if a['caisse']:
                        caisse=a['caisse'][1]
                    else:
                        caisse = ""
                    if (admission <= periodefin) and ((sortie >=periodedebut and (sortie <=periodefin)) or sortie==datetime.datetime(9999,12,31)):
                        entree=time.strftime('%d/%m/%Y', time.strptime(a['admission_date'], '%Y-%m-%d'))
                        if sortie==datetime.datetime(9999,12,31):                    
                            res.append({'caisse':caisse,'name':a['name'],'nsecu':a['numerosecu'],'entree':entree,'sortie':'','absences':absences})
                        else:
                            sortie=time.strftime('%d/%m/%Y', time.strptime(a['date_sortie'], '%Y-%m-%d'))
                            res.append({'caisse':caisse,'name':a['name'],'nsecu':a['numerosecu'],'entree':entree,'sortie':sortie,'absences':absences})
                    
            res.sort(lambda x, y: cmp(x['name'],y['name']))
            return res
    

  

    

report_sxw.report_sxw('report.health.mouvementsemestriel.report', 'health.patient','addons/health/report/mouvementsemestriel.rml', parser=mouvementsemestriel, header=False)

