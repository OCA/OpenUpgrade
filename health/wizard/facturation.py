# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 E.V.I.. (http://www.vernichon.fr) All Rights Reserved.
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

import wizard
import netsvc
import pooler
import datetime
import time
from osv import fields
from osv import osv
facturer_form = '''<?xml version="1.0"?>
<form string="Facturer">
    <field name="period_id"/>
</form>'''

facturer_fields = {
        'period_id':  {'string':'Periode', 'type':'many2one', 'relation': 'account.period', 'required':True},
}

facturer_select_form = '''<?xml version="1.0"?>
<form string="Résidents à facturer">
    <separator string="Residents" colspan="4"/>
    <field name="residents_ids"  nolabel="1"/>
</form>'''

facturer_select_fields = {
    'residents_ids': {'string': 'Résidents', 'type':'one2many', 'relation':'res.partner'},
}


def _init(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    period_obj = pool.get('account.period')
    data['form']['period_id'] = period_obj.find(cr, uid)[0]
    return data['form']

def _selectionner(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    period_obj = pool.get('account.period')
    data['form']['period_id'] = period_obj.find(cr, uid)[0]
    data['form']['name'] = pooler.get_pool(cr.dbname).get('health.patient').read(cr,uid,data['ids'][0])['name']
    return data['form']
    resident_ids = data['ids']#pooler.get_pool(cr.dbname).get('health.patient').read(cr,uid,data['ids'])
    self.residents_ids=resident_ids
    return {'residents_ids':resident_ids}

def _date(date):
    return datetime.datetime(int(date[0:4]),int(date[5:7]),int(date[8:10]))

def _facturer(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    prd_tm = pool.get('product.product').search(cr, uid, [('default_code','=','tm')])[0]
    cong = pool.get('health.room.tarif').search(cr, uid, [('ref','=','ccong')])[0]
    csp60 = pool.get('health.room.tarif').search(cr, uid, [('ref','=','csp60')])[0]
    csm60 = pool.get('health.room.tarif').search(cr, uid, [('ref','=','csm60')])[0]
    cdp60 = pool.get('health.room.tarif').search(cr, uid, [('ref','=','cdp60')])[0]
    cdm60 = pool.get('health.room.tarif').search(cr, uid, [('ref','=','cdm60')])[0]
    for resident_id in data['ids']:
        resident = pooler.get_pool(cr.dbname).get('health.patient').read(cr,uid,resident_id)
        fact_id= pool.get('health.facturation').search(cr,uid,[('name','=',resident_id),('period_id','=',data['form']['period_id'])])
        if fact_id:
        #    pool.get('health.facturation').unlink(cr,uid,fact_id)
             raise osv.except_osv('Erreur !', 'Résident déjà facturé pour cette periode \n' +resident['name']+' !')
        tm =  pool.get('product.product').read(cr,uid,prd_tm)['list_price']
        fin_per =  _date(pool.get('account.period').read(cr,uid,data['form']['period_id'])['date_stop'])
        deb_per = _date(pool.get('account.period').read(cr,uid,data['form']['period_id'])['date_start'])
        anniversaire = _date(resident['birthdaydate'])
        if resident['girage']:
            dep_id = pool.get('health.tarif.dependance').search(cr, uid, [('name','=',resident['girage'])])[0]
            dep = pool.get('health.tarif.dependance').read(cr, uid,dep_id)['montant']
        else:
            dep=0.0
       
        hospitalisation = 0
        duree_absences = 0
        absences = pool.get('health.absences').search(cr, uid, [('partner_id','=',resident_id)])
        commentaire=""
        for absence in absences:
            abs=pool.get('health.absences').read(cr,uid,absence)
            if abs['au'] and abs['facture'] ==0 :
                if _date(abs['au'])< deb_per :
                    if abs['categorie'] == '1':
                        hospitalisation = hospitalisation+ abs["nbrjour"]
                        commentaire=commentaire+"Absence pour Hospitalisation du "+str(abs['du']) + " au "+str(abs['au'])+" \n"

                    else:
                        duree_absences = duree_absences+abs["nbrjour"]
                        commentaire=commentaire+"Absence pour Convenance personnelle du "+str(abs['du']) + " au "+str(abs['au'])+" \n"
                    widget="image"
                    print "Duree Absences ",duree_absences
                    if duree_absences <=3:
                        duree_absences=0
                        print "Duree Absences <=3 ",duree_absences
                    else:
                        duree_absences=duree_absences-3
                        print "Duree Absences >3 ",duree_absences
                    if hospitalisation <=3:
                        hospitalisation=0
                        print "Duree Absences <=3 ",hospitalisation
                    else:
                        hospitalisation=hospitalisation-3
                        print "Duree Absences >3 ",hospitalisation
                    pool.get('health.absences').write(cr, uid, absence,{'facture':1})


        lim60 = anniversaire.replace(year=anniversaire.year+60)
        chambre=pool.get('health.room').read(cr,uid,resident['room_id'][0])
        if resident['congregation']:
            heb = pool.get('health.room.tarif').read(cr, uid,cong)['prix']
        else:
            if (deb_per - lim60).days < 0 :
                if chambre['type']=='1':
                    heb = pool.get('health.room.tarif').read(cr, uid,csm60)['prix']
                else:
                    heb = pool.get('health.room.tarif').read(cr, uid,cdm60)['prix']
            else:
                if chambre['type']=='1':
                    heb = pool.get('health.room.tarif').read(cr, uid,csp60)['prix']
                else:
                    heb = pool.get('health.room.tarif').read(cr, uid,cdp60)['prix']
        if resident['admission_date']:
            if _date(resident['admission_date'])> deb_per and _date(resident['admission_date'])<= fin_per:
                deb_per =  _date(resident['admission_date'])
       
        if resident['date_liberation']:
            if _date(resident['date_liberation'])>= deb_per and _date(resident['date_liberation'])< fin_per:
                fin_per =  _date(resident['date_liberation'])

        nbrjour =(fin_per-deb_per).days+1
        apa=0.0
        aso=0.0
        al=0.0
        if  resident['apa']:
            apa=1
        if  resident['aidesociale']:
            aso=resident['aidesocialemontant']
        if  resident['aidelogement']:
            al=resident['aidelogementmontant']
        facturation_id=pool.get('health.facturation').create(cr, uid,{'hebergement':heb,'decomptes':nbrjour,'name':resident_id,'chambre':resident['room_id'][0],'period_id':data['form']['period_id'],'ticketmoderateur':tm,'dependance':dep,'aidesociale':aso,'allocation':al,'apa':apa,'absences':duree_absences,'hospitalisation':hospitalisation,'commentaire':commentaire})
        
    return{}


class wizard_facturer(wizard.interface):
    states = {
        'init': {
            'actions': [_init],
            'result': {'type':'form', 'arch':facturer_form, 'fields':facturer_fields, 'state':[('end','Cancel'),('facturer','Facturer')]}
        },
        'facturer': {
            'actions': [_facturer],
            'result': {'type' : 'state', 'state': 'end'}
             
            }
    }
wizard_facturer('facturer')
