# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 EVERLIBRE All Rights Reserved.
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
import pooler

dates_form = '''<?xml version="1.0"?>
<form string="Select semestre">
    <field name="semestre" colspan="4"/>
</form>'''

dates_fields = {
    'semestre': {'string': 'semestre', 'type': 'many2one','relation':'health.semestre', 'required': True},
}

class wizard_report(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        semestre_obj = pool.get('health.semestre')
        semestre = semestre_obj.find(cr, uid)[0]
        data['form']['semestre'] =semestre
        return data['form']

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'health.mouvementsemestriel.report', 'state':'end'}
        }
    }
wizard_report('health.mouvementsemestriel.report')

