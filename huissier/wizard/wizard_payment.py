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
import pooler
import wizard
import netsvc
from tools.misc import UpdateableStr
_moves_arch =  UpdateableStr()
_moves_fields = {}

#reprint_form = '''<?xml version="1.0"?>
#<form title="Paiement du lot">
#   <field name="scan_code" colspan="4"/>
#</form>'''

#reprint_fields = {
#   'scan_code': {'string':u'Code client', 'type':'char', 'required':True},
#   'scan_code': {'string': 'client', 'type': 'many2one', 'relation':'res.partner'},

#}
def start (self,cr,uid,data,context):
    print "ds start"*10 
    return {}

def _payer(self,cr,uid,data,context):
    print "Dans payer"
    lots_dossier=pooler.get_pool(cr.dbname).get('huissier.dossier').browse(cr,uid,data['ids'])[0]
    print "DAS DOSSIER"*100,lots_dossier
    res={}
    _moves_arch_lst=['<?xml version=" 1.0"?>,<form string="Paiement des lots">']
    for m in lots_dossier.lot_id:
        _moves_arch_lst.append('<field name="move%s" />' % (m.id,))
     #  _moves_fields['move%s' % m.id] = {'string': '%s - %s - %s -%s' % (m.adj_price, m.desc,m.payer,m.buyer_ref)}
        _moves_arch_lst.append('<group col="6"><label string="adj_price%s"/>\<field name="buyer_ref%s"/>\<field name="payer%s"/>\<label string="name%s"/>' % (m.id, m.id,m.id,m.id))
        _moves_fields['adj_price%s' % m.id] = {'string': 'Prix d adjudication','type': 'float', 'required': True, 'default':m.adj_price}
        _moves_fields['buyer_ref%s' % m.id] = {'string': 'Acheteur', 'type':'many2one','relation': 'res.partner'}
        _moves_fields['payer%s' % m.id] = {'string': 'Paye', 'type':'boolean'}
        _moves_fields['name%s' % m.id] = {'string': 'Description', 'type':'string','default': m.name}
        print _moves_fields
        _moves_arch_lst.append('<newline/>')
        res.setdefault('moves', []).append(m.id)
    _moves_arch_lst.append('</form>')
    _moves_arch.string = '\n'.join(_moves_arch_lst)
    return res

#def _get_value(self, uid, datas):
#   return {}
#def def_payment(self, cr, uid, data, context):
#   pool = pooler.get_pool(cr.dbname)
#   code_client=data['form']['scan_code'] 
#   find_id= pool.get('res.partner').browse(cr,uid,data['form']['scan_code'])
#   pool.get('huissier.lots').write(cr,uid,data['ids'],{'state':'vendu','buyer_ref':find_id.id})
#   return {}

#def ajouter_lots(self, cr, uid, data, context):
#   obj = pooler.get_pool(cr.dbname).get('huissier.lots').search(cr,uid,[('state'='non_vendu')])
#   list_obj = obj.browse(cr, uid, [data['id']])[0]
#   res = {}
#
#   _moves_fields.clear()
#   _moves_arch_lst = ['<?xml version="1.0"?>', '<form string="vente de lots">']
#   for m in list_obj:
#       _moves_arch_lst.append('<field name="number%s" />' % (m.id,))
#       _moves_fields['lot%s' % m.id] = {
#               'string': '%s - %s' % (m.product_id.code, m.product_id.name),
#               'type' : 'float', 'required' : True, 'default' : make_default(quantity)}
#
#
#   for m in pick.move_lines:
#)
class wizard_payment(wizard.interface):
    states = {
        'init': {
            'actions': [_payer], 
            'result': {'type':'form', 'arch':_moves_arch, 'fields':_moves_fields, 'state':[('payer','Payer'), ('end','Annuler')]}
        },
        'payer': {
            'actions': [],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_payment('huissier.lots.payment')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

