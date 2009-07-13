# -*- encoding: utf-8 -*-
##############################################################################
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

sur_form = '''<?xml version="1.0"?>
<form string="Dissociate selected analytic lines">
    <label string="Are you sure you want to 
    dissociate those lines from invoice ?"/>
</form>'''
sur_form2 = '''<?xml version="1.0"?>
<form string="Analytic lines dissociated">
    <label string="The selected analytic lines 
    have been dissociated from their invoice."/>
</form>'''

sur_fields = {
}

class wiz_dissociate_aal(wizard.interface):
    """dissociate AA line from invoice """
    def _dissociate_line(self, cr, uid, data, context):
        """dissociate AA line from invoice """
        try :
            pool = pooler.get_pool(cr.dbname)
            ids = pool.get('account.analytic.line').browse(cr, uid, data['ids'])
            ids2=[]
            for id in ids:
                ids2.append(id.id)
            #we use an sql request as the orm does not allows to change 
            #an invoice AA line
            cr.execute("UPDATE account_analytic_line \
                SET invoice_id = null \
                WHERE id in (%s);"%(','.join(map(str,ids2))))
            return {}
        except Exception, e:
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e.name)+' '+str(e.value)
                                      )
        
    states = {
        'init': {
            'actions': [],
            'result': {
                        'type':'form', 
                        'arch':sur_form, 
                        'fields':sur_fields, 
                        'state':[
                                    ('end','Cancel'),
                                    ('dissociate','Dissociate lines')
                                ]
                        }
        },
        'dissociate': {
            'actions': [_dissociate_line],
            'result': {
                        'type':'form', 
                        'arch':sur_form2, 
                        'fields':sur_fields, 
                        'state':[
                                    ('end','OK')
                                ]
                        }
        },
        'message': {
            'actions': [],
            'result': {
                        'type':'form', 
                        'arch':sur_form2,
                        'fields':sur_fields, 
                        'state':[
                                    ('end','OK')
                                ]
                    }
        },
    }
wiz_dissociate_aal('dissociate.aal.from.invoice')

