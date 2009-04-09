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

import wizard
import netsvc

palais_form = '''<?xml version="1.0"?>
<form title="Paid ?">
    <field name="date1"/>
    <field name="date2"/>
</form>'''

palais_fields = {
    'date1': {'string':u'Début de période', 'type':'date', 'required':True},
    'date2': {'string':u'Fin de période', 'type':'date', 'required':True},
}

def _get_value(self,cr,uid,datas,context):
    return {'date1':time.strftime('%Y-%m-%d'), 'date2':time.strftime('%Y-%m-%d')}

class wizard_palais(wizard.interface):
    states = {
        'init': {
            'actions': [_get_value], 
            'result': {'type':'form', 'arch':palais_form, 'fields':palais_fields, 'state':[('palais','Imprimer le listing'), ('end','Annuler')]}
        },
        'palais': {
            'actions': [],
            'result': {'type':'print', 'report':'huissier.palais', 'state':'end'}
        }
    }
wizard_palais('huissier.palais')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

