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

reprint_form = '''<?xml version="1.0"?>
<form title="Paid ?">
    <field name="start"/>
    <field name="stop"/>
</form>'''

reprint_fields = {
    'start': {'string':u'De', 'type':'integer', 'required':True},
    'stop': {'string':u'a', 'type':'integer', 'required':True},
}

#def _get_value(self, uid, datas):
#   return {}


class wizard_reprint(wizard.interface):
    states = {
        'init': {
#           'actions': [_get_value], 
            'actions': [], 
            'result': {'type':'form', 'arch':reprint_form, 'fields':reprint_fields, 'state':[('reprint','Imprimer'), ('end','Annuler')]}
        },
        'reprint': {
            'actions': [],
            'result': {'type':'print', 'report':'huissier.labels.reprint', 'state':'end'}
        }
    }
wizard_reprint('huissier.labels.reprint')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

