# -*- coding: utf-8 -*-
"""
    Module de gestion des résident pour le EHPAD
"""
##############################################################################
#
# Copyright (c) 2009 EVERLIBRE  All Rights Reserved.
#                    Eric Vernichon
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
from osv import fields, osv
def ecart_date(premier,dernier):
       anneep=int(premier[0:4])
       moisp=int(premier[5:7])
       jourp=int(premier[8:10])
       anneed=int(dernier[0:4])
       moisd=int(dernier[5:7])
       jourd=int(dernier[8:10])
       return (datetime.datetime(anneed,moisd,jourd)-datetime.datetime(anneep,moisp,jourp)).days+1

class health_semestre(osv.osv):
    _name = "health.semestre"
    _description = "Semestre"
    _columns = {
        'name': fields.char('Semestre', size=64, required=True),
        'code': fields.char('Code', size=12),
        'date_start': fields.date('Start of period', required=True, states={'done':[('readonly',True)]}),
        'date_stop': fields.date('End of period', required=True, states={'done':[('readonly',True)]}),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True, states={'done':[('readonly',True)]}, select=True),
    }
    _order = "date_start"
health_semestre()    
class ir_action_window(osv.osv):
    """
    Surcharge ir_action_window
    """
    _inherit = 'ir.actions.act_window'
    def read(self, cr, uid, ids, *args, **kwargs):
        """
            lecture
        """
        res = super(ir_action_window, self).read(cr, uid, ids, *args, **kwargs)
        for r in res:
            mystring = 'id_resident()'
            if  mystring in (r.get('domain', '[]') or ''):
                cat_id = self.pool.get('res.partner.category').search(cr, 
                    uid,[('name','=','Résident')])
                r['domain'] = r['domain'].replace(mystring, str(cat_id))
            mystring = 'id_postulant()' 
            if mystring in (r.get('domain', '[]') or ''):
                cat_id = self.pool.get('res.partner.category'). search(cr, uid,
                    [('name','=','Postulant')])
                r['domain'] = r['domain'].replace(mystring, str(cat_id))
        return res
ir_action_window()

class health_religion(osv.osv):
    """ 
    religions
    """
    _name = 'health.religion'
    _description = 'religion'
    _columns = {
        'name' :fields.char('name', size=256),
        }
health_religion()
class health_situation(osv.osv):
    """
    Situation de famille
    """
    _name = 'health.situation'
    _description = 'situation'
    _columns = {
        'name' :fields.char('name', size=256),
        }
health_situation()

class health_room_tarif(osv.osv):
    """ Tarif de chambre """
    _name = "health.room.tarif"
    _description = "Tarif chambres"
    _columns = {
            'name':fields.char("Type de tarif",size=128),
            'ref':fields.char("reference",size=8),
            'type':fields.selection([('1','Simple'),('2','Double'),('3','Congrégation')],'Type de chambre'),
            'age':fields.selection([('1','Moins de 60 ans'),('2','Plus de 60 ans'),('3','Sans objet')],'Limite d\'âge'),
            'prix':fields.float('Prix'),
            }
health_room_tarif()

class health_room_localisation(osv.osv):
    """
     Type de Chambres
    """
    _name = 'health.room.localisation'
    _description = "Localisation"
    _columns = {
        'name': fields.char("Code",size=128),
        'designation':fields.char("Désignation",size=128),
        'nbrchambre': fields.integer("Nombre de chambre"),
    }

health_room_localisation()
class health_room(osv.osv):
    """
     Chambres
    """
    _name = 'health.room'
    _description = "Chambres"
    _columns = {
        'name': fields.char("Numero de chambre",size=12),
        'localisation':fields.many2one('health.room.localisation','Localisation'), 
        'type':fields.selection([('1','Simple'),('2','Double')],'Type de chambre'),
        'bed': fields.integer("Nombre de lit"),

    }

health_room()


class health_tarif_dependance(osv.osv):
    """
    Tarif Dependance
    """
    _name = 'health.tarif.dependance'
    _description = 'Tarif Dépendance'
    _order = "montant desc"
    _columns = {
        'name': fields.char('GIR', size=256),
        'montant':fields.float('Tarif Dépendance'),
    }
health_tarif_dependance()

class health_drugform(osv.osv):
    """
    forme de medicaments
    """
    _name = 'health.drugform'
    _description = 'Drug Form'
    _columns = {
        'name': fields.char('name', size=256)
    }
health_drugform()

class health_drugfamilly(osv.osv):
    """
    famille de medicament
    """
    _name = 'health.drugfamilly'
    _description = 'Drug Familly'
    _columns = {
        'name': fields.char('name', size=256)
    }
health_drugfamilly()
# 
# LE MODELE PATHOS
#
#reference http://www.fehap.fr/social/personnes_agees/DOC212a4.pdf
# CNAMTS et SNGC - Décembre 2003

class health_pathosprofils(osv.osv):
    """
    Les Profils
    """
    _name = 'health.pathosprofils'
    _description = 'Profils Pathos'
    _table = 'health_pathosprofils'
    _columns = {
            'name': fields.char('Profil',size=2),
            'description': fields.char('Description',size=250),
            'definition':fields.text('Definition'),
        }
health_pathosprofils()
class health_pathoscategetats(osv.osv):
    """
    Les catégories d'états phatologique
    """
    _name = 'health.pathoscategetats'
    _description = 'Catégorie d\'États Pathologique Pathos'
    _table = 'health_pathoscategetats'
    _columns = {
            'name': fields.char('Categorie Etats Pathologique',size=250),
        }
health_pathoscategetats()
class health_pathosetatspatho(osv.osv):
    """
    Les états pathologiques
    """
    _name = 'health.pathosetatspatho'
    _description = 'Etats Patholohgique Pathos'
    _table = 'health_pathosetatspatho'
    _columns = {
            'name': fields.char('Etats Pathologique',size=2),
            'description': fields.char('Description',size=250),
            'definition':fields.text('Definition'),
            'categorie': fields.many2one('health.pathoscategetats', 'Categorie'),   
            'profils': fields.many2many('health.pathosprofils', 'health_profil_rel','name','profil','Profils')
        }
health_pathosetatspatho()

class health_facturation(osv.osv):
    _name = 'health.facturation'
    _description = 'Facturation'
    _table = 'health_facturation'
    def facturer(self, cr, uid, ids, context={}):
        """ Création des factures """
        obj_facture=self.pool.get('account.invoice')
        obj_produit=self.pool.get('product.product')
        prd_tm = obj_produit.search(cr, uid, [('default_code','=','tm')])[0]
        prd_apa = obj_produit.search(cr, uid, [('default_code','=','apa')])[0]
        prd_dep = obj_produit.search(cr, uid, [('default_code','=','dep')])[0]
        prd_as = obj_produit.search(cr, uid, [('default_code','=','as')])[0]
        prd_al = obj_produit.search(cr, uid, [('default_code','=','al')])[0]
        prd_heb = obj_produit.search(cr, uid, [('default_code','=','heb')])[0]
        prd_abp = obj_produit.search(cr, uid, [('default_code','=','abp')])[0]
        prd_abh = obj_produit.search(cr, uid, [('default_code','=','abh')])[0]
        obj_ligne_facture=self.pool.get('account.invoice.line')
        facturations=self.browse(cr,uid,ids)
        for donnee in self.browse(cr, uid, ids, context):
            date_facture=donnee['period_id']['date_start']
            partner_id=donnee.name.id
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('health.patient').browse(cr, uid, partner_id)
            payment_term = p.property_payment_term and p.property_payment_term.id or False
            acc_id = p.property_account_receivable.id
            comment=donnee['commentaire']
            nbjour=donnee['decomptes']
            if donnee['apa']:
                comment="APA versée par le conseil général : "+str(nbjour)+ " * "+str(donnee['dependance'])+" = "+str(float(nbjour)*float(donnee['dependance']))
            if donnee['allocation']:
                comment=comment+"\nAllocataire de l'Aide au logement"
            if donnee['aidesociale']:
                comment=comment+"\nAllocataire de l'Aide Sociale"
            facture={'payment_term':payment_term,'account_id':acc_id,'address_invoice_id':invoice_addr_id,'name':p.name+" - "+donnee.period_id.name,'type':'out_invoice','state':'draft','date_invoice':date_facture,'date_due':date_facture,'partner_id':partner_id,'comment':comment,'period_id':donnee['period_id']['id']}
            invoice_id=obj_facture.create(cr,uid,facture)   
            tm= obj_produit.browse(cr,uid,prd_tm)
            if donnee['hebergement']:
                ligne_facture={'price_unit':donnee['hebergement'],'name':'Hébergement','invoice_id':invoice_id,'product_id':prd_heb,'account_id':obj_produit.browse(cr,uid,prd_heb).product_tmpl_id.property_account_income.id,'quantity':nbjour}
                obj_ligne_facture.create(cr,uid,ligne_facture)
            if donnee['dependance']:
                ligne_facture={'price_unit':donnee['dependance'],'name':'Dépendance','invoice_id':invoice_id,'product_id':prd_dep,'account_id':obj_produit.browse(cr,uid,prd_dep).product_tmpl_id.property_account_income.id,'quantity':nbjour}
                obj_ligne_facture.create(cr,uid,ligne_facture)
            if donnee['hospitalisation']:
                abh=obj_produit.read(cr,uid, prd_abh)
                ligne_facture={'price_unit':abh['list_price'],'name':'Absences pour hospitalisation','invoice_id':invoice_id,'product_id':prd_abh,'account_id':obj_produit.browse(cr,uid,prd_abh).product_tmpl_id.property_account_income.id,'quantity':int(donnee['hospitalisation'])}
                obj_ligne_facture.create(cr,uid,ligne_facture)
            if donnee['absences']:
                abp=obj_produit.read(cr,uid, prd_abp)
                ligne_facture={'price_unit':abp['list_price'],'name':'Absences pour Convenance Personelle','invoice_id':invoice_id,'product_id':prd_abp,'account_id':obj_produit.browse(cr,uid,prd_abp).product_tmpl_id.property_account_income.id,'quantity':int(donnee['absences'])}
                obj_ligne_facture.create(cr,uid,ligne_facture)
            ligne_facture={'price_unit':donnee['ticketmoderateur'],'name':tm.name,'invoice_id':invoice_id,'product_id':prd_tm,'account_id':tm.product_tmpl_id.property_account_income.id,'quantity':nbjour}
            obj_ligne_facture.create(cr,uid,ligne_facture)
        return 0


        


    def on_change_resident(self, cr, uid, ids, partner_id):
        if partner_id:
            res = self.pool.get('health.patient').read(cr,uid,partner_id)
            result = {'value': {
                'chambre': res['room_id'],}
            }
            return result
        
    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False
            
    _columns = {
            'name':fields.many2one('health.patient', 'Resident',  domain="[('category_id','=','Résident')]",required=True), 
            'period_id':fields.many2one('account.period','Période de facturation',required=True),
            'chambre': fields.many2one('health.room', 'Chambres'),
            'hebergement': fields.float('Tarif Hébergement'),
            'datefacturation': fields.date('Date de facture'),
            'decomptes': fields.char('Nb de jours pour la période',size=128),
            'hospitalisation':fields.char('Absences Hospitalisation',size=128),
            'absences':fields.char('Absences convenance personnelle',size=128),
            'absautres':fields.char('Absences Autres',size=128),
            'dependance':fields.float('Tarid Dépendance',size=128),
            'commentaire':fields.text('Commentaire'),
            'ticketmoderateur':fields.float('Ticket Modérateur',size=128),
            'apa':fields.char('A.P.A.',size=128),
            'allocation':fields.char('Allocation Logement',size=128),
            'aidesociale':fields.char('Aide Sociale',size=128),
                }
    _defaults = {
       'period_id': _get_period,
       'datefacturation': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name,period_id)', 'Résident déja facturer pour cette période !')
    ]

health_facturation()
class health_aggir(osv.osv):
    """
    Calcul du girage. reference http://fbevernage.free.fr/geronto/aggir.htm
    """
    _name = 'health.aggir'
    _description = 'Aggir'
    _table = 'health_aggir'
    _columns = {
        'name': fields.many2one('res.partner', 'Resident',
            domain="[('category_id','=','Résident')]"), 
        'coherence':fields.selection([('A','a'),('B','b'),('C','c')],
            'Coherence', readonly=False), # Utiliser pour le calcul de gir
        'orientation':fields.selection([('A','a'),('B','b'),('C','c')],
            'Orientation', readonly=False), # Utiliser pour le calcul de gir
        'toilette':fields.selection([('A','a'),('B','b'),('C','c')],
            'Toilette', readonly=False),# Utiliser pour le calcul de gir
        'habillage':fields.selection([('A','a'),('B','b'),('C','c')],
            'Habillage', readonly=False),# Utiliser pour le calcul de gir
        'alimentation':fields.selection([('A','a'),('B','b'),('C','c')],
            'Alimentation', readonly=False),# Utiliser pour le calcul de gir
        'elimination':fields.selection([('A','a'),('B','b'),('C','c')],
            'Elimination', readonly=False),# Utiliser pour le calcul de gir
        'transferts':fields.selection([('A','a'),('B','b'),('C','c')],
            'Transferts', readonly=False),# Utiliser pour le calcul de gir
        'moveint':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Deplacement Interieur', readonly=False),# pour le calcul de gir
        'deplacementexterieur':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Deplacement Exterieur', readonly=False),
        'communication':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Communiquer pour alerter', readonly=False),
        'gestion':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Gestion', readonly=False),
        'cuisine':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Cuisine', readonly=False),
        'menage':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Menage', readonly=False),            
        'transports':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'transports', readonly=False),            
        'achats':fields.selection([('A','a'),('B','b'),('C','c')],'achats'
            , readonly=False),            
        'traitement':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'suivi de traitement', readonly=False),   
        'activite':fields.selection([('A','a'),('B','b'),('C','c')]
            ,'Activites de temps libre', readonly=False),
        'resultat':fields.char('AG-GIR',size=250),
        'gir':fields.char('GIR',size=1),
    }           
    def calcul_gir(self, cr, uid, ids, context={}):
        """ reference http://fbevernage.free.fr/geronto/Programe.htm"""
        girage = 0
        groupe = 0
        rang = 0
        for gir in self.browse(cr, uid, ids, context):
            chaine = str(gir.coherence)+ str(gir.orientation)\
                    + str(gir.toilette)+str(gir.habillage)\
                    + str(gir.alimentation)\
                    + str(gir.elimination)+str(gir.transferts)\
                    + str(gir.moveint)
            if len(chaine)< 8 :
                chaine = "Veuillez remplir tout les champs"
            else:
                if gir.coherence == "C": #Groupe A
                    groupe = 2000
                if gir.orientation == "C":
                    groupe = groupe+1200
                if gir.toilette == "C":
                    groupe = groupe+40
                if gir.habillage == "C":
                    groupe = groupe+40
                if gir.alimentation == "C":
                    groupe = groupe+60
                if gir.elimination == "C":
                    groupe = groupe+100
                if gir.transferts == "C":
                    groupe = groupe+800
                if gir.moveint == "C":
                    groupe = groupe+200
                if gir.toilette == "B":
                    groupe = groupe+16
                if gir.habillage == "B":
                    groupe = groupe+16
                if gir.alimentation == "B":
                    groupe = groupe+20
                if gir.elimination == "B":
                    groupe = groupe+16
                if gir.transferts == "B":
                    groupe = groupe+120
                if gir.moveint == "B":
                    groupe = groupe+32
                if groupe >= 4380:
                    rang = 1
                if groupe >= 4140 and groupe <= 4379:
                    rang = 2
                if groupe >= 3390 and groupe <= 4139:
                    rang = 3
                if rang == 0 :
                    groupe = 0 # Groupe B
                    if gir.coherence == "C":
                        groupe = 1500
                    if gir.orientation == "C":
                        groupe = groupe+1200
                    if gir.toilette == "C":
                        groupe = groupe+40
                    if gir.habillage == "C":
                        groupe = groupe+40
                    if gir.alimentation == "C":
                        groupe = groupe+60
                    if gir.elimination == "C":
                        groupe = groupe+100
                    if gir.transferts == "C":
                        groupe = groupe+800
                    if gir.moveint == "C":
                        groupe = groupe+80
                    if gir.coherence == "B":
                        groupe = groupe+320
                    if gir.orientation == "B":
                        groupe = groupe+120
                    if gir.toilette == "B":
                        groupe = groupe+16
                    if gir.habillage == "B":
                        groupe = groupe+16
                    if gir.alimentation == "B":
                        groupe = groupe+0
                    if gir.elimination == "B":
                        groupe = groupe+16
                    if gir.transferts == "B":
                        groupe = groupe+120
                    if gir.moveint == "B":
                        groupe = groupe+40
                    if groupe >= 2016:
                        rang = 4
                    else:
                        rang = 0
                    if rang == 0:
                        groupe = 0 # Groupe C
                        if gir.toilette == "C":
                            groupe = groupe+40
                        if gir.habillage == "C":
                            groupe = groupe+40
                        if gir.alimentation == "C":
                            groupe = groupe+60
                        if gir.elimination == "C":
                            groupe = groupe+160
                        if gir.transferts == "C":
                            groupe = groupe+1000
                        if gir.moveint == "C":
                            groupe = groupe+400

                        if gir.toilette == "B":
                            groupe = groupe+16
                        if gir.habillage == "B":
                            groupe = groupe+16
                        if gir.alimentation == "B":
                            groupe = groupe+20
                        if gir.elimination == "B":
                            groupe = groupe+20
                        if gir.transferts == "B":
                            groupe = groupe+200
                        if gir.moveint == "B":
                            groupe = groupe+40
                        if groupe >= 1700:
                            rang = 5
                        if groupe >= 1432 and groupe <= 1699:
                            rang = 6
                        if rang == 0:
                            groupe = 0 # Groupe D
                            if gir.alimentation == "C":
                                groupe = groupe+2000
                            if gir.elimination == "C":
                                groupe = groupe+400
                            if gir.transferts == "C":
                                groupe = groupe+2000
                            if gir.moveint == "C":
                                groupe = groupe+200
                                
                            if gir.alimentation == "B":
                                groupe = groupe+200
                            if gir.elimination == "B":
                                groupe = groupe+200
                            if gir.transferts == "B":
                                groupe = groupe+200
                            if groupe >= 2400:
                                rang = 7
                            if rang == 0:
                                groupe = 0 # Groupe E
                                if gir.coherence == "C":
                                    groupe = 400
                                if gir.orientation == "C":
                                    groupe = groupe+400
                                if gir.toilette == "C":
                                    groupe = groupe+400
                                if gir.habillage == "C":
                                    groupe = groupe+400
                                if gir.alimentation == "C":
                                    groupe = groupe+400
                                if gir.elimination == "C":
                                    groupe = groupe+800
                                if gir.transferts == "C":
                                    groupe = groupe+800
                                if gir.moveint == "C":
                                    groupe = groupe+200   
                    
                                if gir.toilette == "B":
                                    groupe = groupe+100
                                if gir.habillage == "B":
                                    groupe = groupe+100
                                if gir.alimentation == "B":
                                    groupe = groupe+100
                                if gir.elimination == "B":
                                    groupe = groupe+100
                                if gir.transferts == "B":
                                    groupe = groupe+100
                                if groupe >= 1200:
                                    rang = 8
                                if rang == 0:
                                    groupe = 0 # Groupe F
                                    if gir.coherence == "C":
                                        groupe = 200
                                    if gir.orientation == "C":
                                        groupe = groupe+200
                                    if gir.toilette == "C":
                                        groupe = groupe+500
                                    if gir.habillage == "C":
                                        groupe = groupe+500
                                    if gir.alimentation == "C":
                                        groupe = groupe+500
                                    if gir.elimination == "C":
                                        groupe = groupe+500
                                    if gir.transferts == "C":
                                        groupe = groupe+500
                                    if gir.moveint == "C":
                                        groupe = groupe+200                   
                                    if gir.coherence == "B":
                                        groupe = groupe + 100
                                    if gir.orientation == "B":
                                        groupe = groupe+100
                                    if gir.toilette == "B":
                                        groupe = groupe+100
                                    if gir.habillage == "B":
                                        groupe = groupe+100
                                    if gir.alimentation == "B":
                                        groupe = groupe+100
                                    if gir.elimination == "B":
                                        groupe = groupe+100
                                    if gir.transferts == "B":
                                        groupe = groupe+100                   
                                    if groupe >= 800:
                                        rang = 9
                                    if rang == 0:
                                        groupe = 0 # Groupe G
                                        if gir.coherence == "C":
                                            groupe = 150
                                        if gir.orientation == "C":
                                            groupe = groupe+150
                                        if gir.toilette == "C":
                                            groupe = groupe+300
                                        if gir.habillage == "C":
                                            groupe = groupe+300
                                        if gir.alimentation == "C":
                                            groupe = groupe+500
                                        if gir.elimination == "C":
                                            groupe = groupe+500
                                        if gir.transferts == "C":
                                            groupe = groupe+400
                                        if gir.moveint == "C":
                                            groupe = groupe+200       
                                        if gir.toilette == "B":
                                            groupe = groupe+200
                                        if gir.habillage == "B":
                                            groupe = groupe+200
                                        if gir.alimentation == "B":
                                            groupe = groupe+200
                                        if gir.elimination == "B":
                                            groupe = groupe+200
                                        if gir.transferts == "B":
                                            groupe = groupe+200
                                        if gir.moveint == "B":
                                            groupe = groupe+100
                                        if groupe >= 650:
                                            rang = 10
                                            if rang == 0:
                                                groupe = 0 # Groupe H
                                                if gir.toilette == "C":
                                                    groupe = groupe+3000
                                                if gir.habillage == "C":
                                                    groupe = groupe+3000
                                                if gir.alimentation == "C":
                                                    groupe = groupe+3000
                                                if gir.elimination == "C":
                                                    groupe = groupe+300
                                                if gir.transferts == "C":
                                                    groupe = groupe+1000
                                                if gir.moveint == "C":
                                                    groupe = groupe+1000
                                                if gir.toilette == "B":
                                                    groupe = groupe+2000
                                                if gir.habillage == "B":
                                                    groupe = groupe+2000
                                                if gir.alimentation == "B":
                                                    groupe = groupe+2000
                                                if gir.elimination == "B":
                                                    groupe = groupe+2000
                                                if gir.transferts == "B":
                                                    groupe = groupe+2000
                                                if gir.moveint == "B":
                                                    groupe = groupe+1000
                                                if groupe >= 4000:
                                                    rang = 11
                                                if groupe >= 2000 and \
                                                        groupe <= 3999:
                                                    rang = 12 
                                                if groupe < 2000:
                                                    rang = 13 
                if rang == 1:
                    girage = 1
                if rang > 1 and rang < 8:
                    girage = 2
                if rang > 7 and rang < 10:
                    girage = 3
                if rang > 9 and rang < 12:
                    girage = 4
                if rang == 12:
                    girage = 5
                if rang == 13:
                    girage = 6
                if groupe >= 4380:
                    rang = 1
                if groupe >= 4140 and groupe <= 4379:
                    rang = 2
                if groupe >= 3390 and groupe <= 4139:
                    rang = 3
                if rang != 0 :
                    if rang == 1:
                        girage = 1
                    if rang > 1 and rang < 8:
                        girage = 2
                    if rang > 7 and rang < 10:
                        girage = 3
                    if rang > 9 and rang < 12:
                        girage = 4
                    if rang == 12:
                        girage = 5
                    if rang == 13:
                        girage = 6
            self.write(cr, uid, ids, {'resultat':chaine})
            self.write(cr, uid, ids, {'gir':str(girage)})
        return 1
health_aggir()
class health_drug(osv.osv):
    """
    Medicaments
    """
    _name = 'health.drug'
    _description = 'Drugs'
    _table = 'health_drug'
    _columns = {
         'name': fields.char('name', size=256, required=True),
        'famille': fields.many2one('health.drugfamilly','familly'),
        'cip': fields.char('CIP', size=8),
        'ucd': fields.char('UCD', size=8),
        'atc': fields.char('ATC', size=8),
        'vidal': fields.boolean('vidal'),
        'volume': fields.float('Volume'),
        'categ_id': fields.many2one('product.category','Category',required=True, change_default=True),
        'forme': fields.many2one('health.drugform', 'Forme'),
        'description': fields.text('Description', translate=True),
        'uom_id': fields.many2one('product.uom', 'Unite', required=True),
        'commentaire':fields.text('Commentaires'),
    }
health_drug()

class health_category(osv.osv):
    """
     Categorie  de personnel : infirmier, a.s. , a.s.h
    """
    _name = 'health.category'
    _description = 'category'
    _columns = {
        'name': fields.char('name', size=64, required=True),
        }
health_category()


class health_care(osv.osv):
    """
    Soins
    """
    _name = 'health.care'
    _description = 'soins'
    _columns = {
        'name': fields.char('Soins', size=256),
    }
health_care()

class health_evenement_type(osv.osv):
    """
     Type evenements pour la releve
    """
    _name = 'health.evenement.type'
    _description = "Type Evenement"
    _columns = {
        'name': fields.char('Type Evenement',size=64, required=True),
        'creator':fields.many2one('res.users', 'Users'),
        }
    _order = 'name desc'
    _defaults = {
        'creator':  lambda obj,cr,uid,context: uid,
    }
health_evenement_type()
#~ class health_aide(osv.osv):
    #~ """
     #~ Aide
    #~ """
    #~ _name = 'health.aide'
    #~ _description = 'Aide'
    #~ _columns = {
        #~ 'name': fields.many2one('res.partner', 'Provenance'),
        #~ 'type': fields.selection([('1','APA'),('2','Aide Sociale'),('3','Aide au logement')],'Désignation'),
        #~ 'resident': fields.many2one('res.partner', 'Resident'),
        #~ 'montant': fields.float('montant'),
        #~ 'destinataire': fields.selection([('1','ehpad'),('2','résident')],'Destinataire'),
        #~ 'du': fields.date("du"),
        #~ 'au': fields.date("au"),
       
    #~ }
    #~ def name_get(self, cr, uid, ids, context={}):
        #~ if not len(ids):
            #~ return []
        #~ res = []
        #~ print context
        #~ print ids
        
        #~ for r in self.read(cr, uid, ids, ['name']):
            #~ print r
            #~ if context.get('contact_display', 'contact')=='partner':
                #~ res.append((r['id'], r['partner_id'][1]))
            #~ else:
                #~ addr = str(r['name'][1] or '')
                #~ res.append((r['id'], addr or '/'))
        #~ return res


#~ health_aide()

class health_patient_evenement(osv.osv):
    """
        Evenement Patient
    """
    _name = 'health.patient.evenement'
    _description = 'evenement'
    _columns = {
        'date': fields.datetime('Date', size=16),
        'description': fields.text('Description', required=True),
        'partner_id': fields.many2one('res.partner', 'Patient'),
        'user_id': fields.many2one('res.users', 'User'),
        'type_evenements': fields.many2one('health.evenement.type','Type Evenement'),
    }
    _order = 'date desc'
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj,cr,uid,context: uid,
    }
health_patient_evenement()
            
class health_prescription(osv.osv):
    """
        Prescription
    """
    _name = 'health.prescription'
    _description = 'prescription'
    _columns = {
        'du': fields.date("du"),
        'au': fields.date("au"),
        'heure': fields.char("heure",size=5),
        'prescripteur': fields.many2one('res.partner', 'Medecin Traitant',domain="[('category_id','=','MEDECINS')]"),
        'medicament':fields.many2one('health.drug','Medicaments'),
        'commentaire':fields.text('Commentaires'),
        'nbrprise':fields.char('Nbre par prise',size=8),
        'user_id': fields.many2one('res.users', 'Saisie Par'),
        'partner_id': fields.many2one('res.partner', 'Patient'),
        
    }
    _order = 'du desc'
    _defaults = {
        'user_id':  lambda obj,cr,uid,context: uid,
        'du':lambda *a: time.strftime('%Y-%m-%d'),
        'heure': lambda *a: time.strftime('%H:%M'),
    }
    
        
health_prescription()



class health_tarif_absences(osv.osv):
    """
    Tarif Absences
    """
    _name = 'health.tarif.absences'
    _description = 'Tarif Absences'
    _order = "montant desc"
    _columns = {
        'name': fields.selection([('1','Hospitalisation'),('2','Convenance Personnelle'),('3','Autres')],'Raison d\'absences'),
        'montant':fields.float('Tarif Absences'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Le type d\'absence doit être unique !')
    ]

health_tarif_absences()

class health_regime(osv.osv):
    """
        Regime de sécurité sociale
    """
    _name = 'health.regime'
    _description = 'Regime'
    _columns = {
            'name': fields.char('Regime de sécurité sociale',size=128),
            'code': fields.char('Code Regime',size=12),
            'parent_id': fields.many2one('health.regime','parent'),
            'child_ids': fields.one2many('health.regime', 'parent_id', 'Childs Category'),
            }
health_regime()

class health_exit(osv.osv):
    """
        Raison de sortie
    """
    _name = 'health.exit'
    _description = 'type de sortie'
    _columns = {
            'name': fields.char('raison',size=128),
        }
health_exit()
class health_absences(osv.osv):
    """
        Absences
    """
    def _compte_jour(self, cr, uid, ids, name, args, context):
        res={}
        for id in ids:
            du=self.read(cr, uid, id,['du'])
            au=self.read(cr, uid, id,['au'])
            if au['au']:
                res[id]=ecart_date(du['du'],au['au'])
            else:
                res[id]=0.0
        return res

    _name = 'health.absences'
    _description = 'absences'
    _columns  = {
        'du': fields.date("du"),
        'au': fields.date("au"),
        'categorie':fields.selection([('1','Hospitalisation'),('2','Convenance Personnelle'),('3','Autres')],'Category', readonly=False),'commentaire':fields.text('Commentaires'),
        'user_id': fields.many2one('res.users', 'Saisie Par'),
        'partner_id': fields.many2one('res.partner', 'Résident',  domain="[('category_id','=','Résident')]"),
        'nbrjour':fields.function(_compte_jour, method=True, string='Nombre de jours',type='float'),
        'facture':fields.boolean('Facturé'),
        
}
    _order = 'du desc'
    _defaults = {
        'user_id':  lambda obj,cr,uid,context: uid,
        'du':lambda *a: time.strftime('%Y-%m-%d'),
        'facture': lambda *a:0
    }
    def create(self, cr, uid, *args, **argv):
        if args[0]['categorie'] == '1' and not args[0]['au']:
            patient=self.pool.get('health.patient').read(cr, uid, args[0]['partner_id'])
            patient=self.pool.get('health.patient').write(cr, uid, args[0]['partner_id'],{'hospitalisation':1})
        return super(health_absences, self).create(cr, uid, *args, **argv)
#    
#    def write(self, cr, uid, ids, vals, context=None):
#        print "Write ",vals,ids
#        for id in ids:
#            abs=self.pool.get('health.absences').read(cr, uid, id)
#            if abs['categorie'] == '1' and vals['au']:
#                print "hospit"
#                print abs
#                patient=self.pool.get('health.patient').read(cr, uid, abs['partner_id'][0])
#                patient=self.pool.get('health.patient').write(cr, uid, abs['partner_id'][0],{'hospitalisation':0})
#        
#        return super(health_absences,self).write( cr, uid, ids, vals, context)
        

health_absences()

class health_patient(osv.osv):
    """
        residents
        
    """
    _name = 'health.patient'
    _inherit = "res.partner"
    _table = "res_partner"
    _description = "Resident"
    _columns = {
        'nomusage': fields.char('Nom d\'usage ',size=128),
        'nom': fields.char('Nom',size=128),
        'nomreligieux': fields.char('Nom Religieux',size=128),
        'prenom': fields.char('Prénom',size=128),
        'photo':fields.binary('Photo Résident'),
        'admission_date': fields.date('Date d\'admission',size=32),
        'date_sortie': fields.date('Date de sortie',size=32),
        'motif_sortie': fields.many2one('health.exit','Raison de sortie'),
        'date_liberation': fields.date('Date de libération de la chambre',size=32),
        'birthdaydate':fields.date('Date de naissance',size=32),
        'lieunaissance':fields.char('Lieu de naissance', size=256),
        'numerosecu':fields.char('Numero de securite sociale', size=256),
        'ncpaiement': fields.char('Numero de centre de paiement',size=256),
        'religion':fields.many2one('health.religion', 'Religion'),
        'situation':fields.many2one('health.situation', 'Situation de famille'),
        'medecin':fields.many2one('res.partner', 'Medecin Traitant',domain="[('category_id','=','MEDECINS')]"), 
        'prescriptions':fields.one2many('health.prescription','partner_id', 'prescriptions'),
        'absences':fields.one2many('health.absences','partner_id','Absences'),
        'care':fields.many2many('health.care','health_care_rel','name','soins','Soins'),
        'evenements': fields.one2many('health.patient.evenement', 'partner_id','evenements'),
        'cmu':fields.boolean('CMU'),
        'livretremis':fields.boolean('Livret Remis'),
        'note': fields.text('notes'),
        'pharmacie':fields.many2one('res.partner', 'Pharmacie',\
            domain="[('category_id','=','PHARMACIES')]"),
        'kine':fields.many2one('res.partner', 'Kine',\
            domain="[('category_id','=','KINESITHERAPEUTES')]"),
        'psy':fields.many2one('res.partner', 'psy',\
            domain="[('category_id','=','PSYCHOLOGUES')]"),
        'ergo':fields.many2one('res.partner', 'Ergonome',\
            domain="[('category_id','=','ERGONOMES')]"),
        'provenance':fields.char( 'Provenance',size=256),
        'laboratoire':fields.many2one('res.partner', 'Laboratoire',\
            domain="[('category_id','=','LABORATOIRES')]"),
        'hopital':fields.many2one('res.partner', 'Hopital',\
            domain="[('category_id','=','HOPITAUX')]"),
        'hospitalisation':fields.boolean('En Hospitalisation'),
        'hopitalant':fields.many2one('res.partner', 'Hopital Ant.',\
            domain="[('category_id','=','HOPITAUX')]"),
        'ambulance':fields.many2one('res.partner', 'Ambulance',\
            domain="[('category_id','=','AMBULANCES')]"),
        'assure':fields.many2one('res.partner', 'Assuree'),
        'obseque':fields.char('Obseques',size=256),
        'obsinformations':fields.char('Informations', size=256),    
        'incineration':fields.boolean('Incineration'),
        'pacemaker':fields.boolean('Pace Maker / C.I.'),
        'doncorps':fields.boolean('Don du corps'),
        'donorganes':fields.boolean('Don d\'organe'),
        'invalidite':fields.char('Invalidite',size=256),
        'invadu': fields.date('du',size=32),
        'invaau': fields.date('au',size=32),
        'respcivil':fields.char('Responsabilite Civile',size=256),
        'respdu': fields.date('du',size=32),
        'respau': fields.date('au',size=32),
        'caisse':fields.many2one('res.partner', 'Caisse',domain="[('category_id','=','CAISSE PRIMAIRES')]"),
        'caissedu': fields.date('du',size=32),
        'caisseau': fields.date('au',size=32),
        'aldtaux':fields.float('TAUX A.L.D'),
        'alddu': fields.date('du',size=32),
        'aldau': fields.date('au',size=32),
        'mutuelle':fields.many2one('res.partner', 'Mutuelle',domain="[('category_id','=','MUTUELLES')]"),
        'mutndossier':fields.char('Nr de dossier',size=64),
        'mutdu': fields.date('du',size=32),
        'mutau': fields.date('au',size=32),
        'cmu':fields.many2one('res.partner', 'C.M.U', domain="[('category_id','=','C.M.U.')]"),
        'cmundossier':fields.char('Nr de dossier',size=64),
        'cmudu': fields.date('du',size=32),
        'cmuau': fields.date('au',size=32),
        'aidesociale':fields.many2one('res.partner', 'Aide Sociale', domain="[('category_id','=','AIDES SOCIALES')]"),
        'aidesocialendossier':fields.char('N° de dossier',size=64),
        'aidesocialemontant': fields.float('montant'),
        'aidesocialedestinataire': fields.selection([('1','ehpad'),('2','résident')],'Destinataire'),
        'aidesocialedu': fields.date("du"),
        'regime':fields.many2one('health.regime', 'Regime'),
        'aidesocialeau': fields.date("au"),
        'apa':fields.many2one('res.partner', 'APA', domain="[('category_id','=','APA DEPARTEMENTS')]"),
        'apandossier':fields.char('Nr de dossier',size=64),
        'apamontant': fields.float('montant'),
        'apadestinataire': fields.selection([('1','ehpad'),('2','résident')],'Destinataire'),
        'apadu': fields.date("du"),
        'apaau': fields.date("au"),
        'aidelogement':fields.many2one('res.partner', 'Aide Au logement', domain="[('category_id','=','AIDES LOGEMENT')]"),
        'aidelogementndossier':fields.char('N° de dossier',size=64),
        'aidelogementmontant': fields.float('montant'),
        'aidelogementdestinataire': fields.selection([('1','ehpad'),('2','résident')],'Destinataire'),
        'aidelogementdu': fields.date("du"),
        'aidelogementau': fields.date("au"),
        'girage':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6')],'GIR Facturation'),
        'room_id': fields.many2one('health.room', 'Chambres'),
        'congregation': fields.boolean('Congregation'),
        
    }
    def write(self, cr, uid, ids, vals, context=None):
        if ids:
            if type(ids) == list:
                ids=ids[0]
            
                
            patient=self.pool.get('health.patient').read(cr, uid, ids)

            if vals.has_key('nom') :
                nom=vals['nom']
            if not vals.has_key('nom') and patient['nom']:
                nom=patient['nom']
            else:
                nom=vals['nom']
            
            if not vals.has_key('prenom') and patient['prenom']:
                prenom=patient['prenom']
            else:
                if not vals.has_key('prenom'):
                    prenom="Prénom"
                else:
                    prenom=vals['prenom']
            if not vals.has_key('nomusage') and patient['nomusage']:
                nomusage=patient['nomusage']
            else:
                nomusage=nom
                vals.update({'nomusage':nomusage})

            if not nomusage==nom:
                name=nomusage.upper()+"/"+nom.upper()+" "+prenom.capitalize()
            else:
                name=nom.upper()+" "+prenom.capitalize()
            vals.update({'name':name})
            vals.update({'hospitalisation':0})
            res=super(health_patient,self).write( cr, uid, ids, vals, context)            
            patient=super(health_patient,self).read( cr, uid, ids)
            partner=self.pool.get('res.partner').read( cr, uid, ids)
            obj_propriete = self.pool.get('ir.property')
            recherche="health.patient,"+str(patient['id'])
            propriete_patient=obj_propriete.search( cr, uid,[('res_id','like',"health.patient,"+str(patient['id']))])
            propriete_partner=obj_propriete.search( cr, uid,[('res_id','like',"res.partner,"+str(patient['id']))])
            if propriete_patient:#le résident a un un compte comptable
                prop=obj_propriete.read(cr,uid,propriete_patient)[0]
                prop['res_id']= prop['res_id'].replace('health.patient','res.partner')
                if not propriete_partner: #Le partenaire a déja un compte comptable
                    #obj_propriete.unlink(cr,uid,propriete_partner)
                    obj_propriete.create(cr,uid,{'fields_id':prop['fields_id'][0] ,'res_id':prop['res_id'],'name':prop['name'],'company_id':prop['company_id'][0],'value':prop['value']})
            if patient['absences'] :
                for abs in patient['absences']:
                    absenc=self.pool.get('health.absences').read(cr, uid, abs)
                    if absenc['categorie'] == '1' and not absenc['au']:
                        super(health_patient,self).write( cr, uid, ids,{'hospitalisation':1})
        return res 


    def create(self, cr, uid, *args, **argv):
        args[0]['name'] = args[0]['nom']
        id=super(health_patient, self).create(cr, uid, args[0])
        if args[0].has_key("prenom"):
            prenom =  args[0]['prenom']
        else:
            prenom=None
        nom = args[0]['nom']
        
        if args[0]['nomusage']:
            nomusage = args[0]['nomusage']
        else:
            nomusage = args[0]['nom']
            args[0].update({'nomusage':nomusage})


        if not nomusage==nom:
            name=nomusage+"/"+nom
        else:
            name=nom
        
        if nom:
            if prenom:
                args[0].update({'name':name.upper()+" "+prenom.capitalize()})
            else:
                args[0].update({'name':name.upper()})
        super(health_patient,self).write( cr, uid, id,args[0])
        return id

       
    def desactive(self, cr, uid, ids,name, context={}):
        result = {'value':{'active':False}}
        return result

    def set_name(self, cr, uid, ids, nom,prenom, context={}):
        if nom:
            if prenom:
                result = {'value': {
                                    'name': nom.capitalize()+" "+prenom.capitalize(),}
                    }
            else:
                result = {'value': {
                                    'name': nom.capitalize(),}
                                                }
        return result
    

health_patient()

