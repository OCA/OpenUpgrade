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

import wizard
import netsvc

import pooler
from tools.misc import UpdateableStr


# Dossier

dossier_form = '''<?xml version="1.0"?>
<form title="Choix du dossier ?">
    <field name="dossier_id" domain="[('state','=','draft')]"/>
</form>'''

dossier_fields = {
    'dossier_id': {'string':'Dossier', 'type':'many2one', 'relation':'huissier.dossier', 'required':True},
}

def _get_value(self, uid, datas, *args, **kwargs):
    return {'partner_id':False}

_lot_arch = UpdateableStr()
_lot_fields = {
    'partner_id': {'string':'Acheteur','relation':'res.partner','type':'many2one','required':True}
}

def _to_xml(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

_all_lots = []

def _get_lots(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    lot_obj = pool.get('huissier.lots')
    dids = lot_obj.search(cr, uid, [('dossier_id','=',data['form']['dossier_id']),('state','=','draft')])
    _arch = """<?xml version="1.0"?>
<form string="Lot" height="500" width="1000">
    <field name="partner_id" colspan="4"/>
    """
    _arch_lst = []
    _all_lots = []
    for lot in lot_obj.browse(cr, uid, dids, context=context):
        _arch_lst.append('<field name="lot_%s" nolabel="1" height="60" width="30" colspan="2"/>' % (lot.id))
        _arch_lst.append('<group col="2" colspan="2">')
        _arch_lst.append('<label string="%s" align="0.0" colspan="2"/>' % _to_xml(str(lot.number)+' - '+lot.name))
        _arch_lst.append('<label string="Adjudication: %.2f, A Payer: %.2f" align="0.0" colspan="2"/>' % (lot.adj_price or 0.0, lot.price_wh_costs or 0.0))
        _arch_lst.append('</group>')
        _lot_fields['lot_'+str(lot.id)]  = {'string': 'Lot '+str(lot.number),'type':'boolean'}
        _all_lots.append('lot_'+str(lot.id))
    _arch = _arch+'\n'.join(_arch_lst)+"""</form>"""
    _lot_arch.string = _arch
    return {'partner_id':False, 'attest_ids':[]}

def _process(self, cr, uid, data, context):
    attestation_ids = []
    kk = data['form'].keys()
    kk.sort()
    key3 = False
    for key in kk:
        if key.startswith('lot_'):
            if  data['form'][key]:
                pool = pooler.get_pool(cr.dbname)
                lot_obj = pool.get('huissier.lots')
                lot_obj.write(cr, uid, int(key[4:]), {'state':'vendu', 'buyer_ref':data['form']['partner_id']})
                attestation_ids.append(int(key[4:]))
                key3 = key

    if key3:
        return {'attest_ids': attestation_ids, key3:False}

    return {'attest_ids': attestation_ids}

class wizard_reprint(wizard.interface):
    states = {
        'init': {
            'actions': [], 
            'result': {'type':'form', 'arch':dossier_form, 'fields':dossier_fields, 'state':[('end','Annuler'),('continue','Continuer')]}
        },
        'valid': {
            'actions': [_process],
            'result': {'type':'print', 'report':'huissier.lots_attestation2', 'state':'continue'}
        },
        'continue': {
            'actions': [_get_lots],
            'result': {
                'type':'form', 
                'arch': _lot_arch,
                'fields': _lot_fields,
                'state': [
                    ('valid','       Valider       ')
                    #('valid','       Valider       ','gtk-ok', True)
                ],
            }
        }
    }
wizard_reprint('huissier.caisse')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

