# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Zikzakmedia SL (http://www.zikzakmedia.com) All Rights Reserved.
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
import time
import xmlrpclib
from osv import osv
import export_table

export_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Export broadcasts">
    <field name="d_from"/>
    <field name="d_to"/>
</form>'''


export_fields = {
    'd_from': {'string': 'From', 'type':'date', 'required':True},
    'd_to':  {'string': 'To', 'type':'date'},
}


def _get_data(self, cr, uid, data, context={}):
    return {'d_from': time.strftime('%Y-%m-%d'),}


def _export(self, cr, uid, data, context):
    """Export (synchronize) the radiotv broadcasts to Joomla PHP server."""
    pool = pooler.get_pool(cr.dbname)
    web_ids = pool.get('radiotv.web').search(cr, uid, [('active','=',True)])
    websites = pool.get('radiotv.web').browse(cr, uid, web_ids, context)
    if websites:
        server = xmlrpclib.ServerProxy(websites[0].url + "/tinyerp-synchro.php")

        form = data['form']
        d_from = form.get('d_from', False)
        d_to = form.get('d_to', False)
        filter = []
        filterphp = ''
        if d_from:
            filter.append(('dt_start', '>=', d_from + ' 00:00:00'))
            filterphp += " dt_start >= '" + d_from + " 00:00:00'"
        if d_to:
            filter.append(('dt_start', '<=', d_to + ' 23:59:59'))
            filterphp += " AND dt_start <= '" + d_to + " 23:59:59'"
        #print filterphp
        (broadcast_new, broadcast_update, broadcast_delete) = export_table.export_table(self, cr, uid, data, context, server, 'broadcast',
            ['id', 'dt_start', 'dt_end', 'channel_id', 'program_id', 'description', 'url'], filter, filterphp)
    else:
        raise osv.except_osv('Error!', 'No website defined!\nPlease create one.')

    return {'broadcast_new':broadcast_new, 'broadcast_update':broadcast_update, 'broadcast_delete':broadcast_delete,}


_export_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Broadcast Export">
    <separator string="Broadcasts exported" colspan="4" />
    <field name="broadcast_new"/>
    <newline/>
    <field name="broadcast_update"/>
    <newline/>
    <field name="broadcast_delete"/>
</form>'''


_export_done_fields = {
    'broadcast_new': {'string':'New broadcasts', 'type':'integer', 'readonly': True},
    'broadcast_update': {'string':'Updated broadcasts', 'type':'integer', 'readonly': True},
    'broadcast_delete': {'string':'Deleted broadcasts', 'type':'integer', 'readonly': True},
}


class wizard_export_broadcast(wizard.interface):
    states = {
        'init': {
            'actions': [_get_data],
            'result': {'type':'form', 'arch':export_form, 'fields':export_fields, 'state':[('end','Cancel','gtk-cancel'),('export','Export','',True)]}
        },
        'export': {
            'actions': [_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wizard_export_broadcast('radiotv.broadcast.export')
