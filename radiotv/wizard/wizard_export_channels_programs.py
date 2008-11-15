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

def _export(self, cr, uid, data, context):
    """Export (synchronize) the radiotv channels, categories, programs and channel_program_relations to Joomla PHP server."""
    pool = pooler.get_pool(cr.dbname)
    web_ids = pool.get('radiotv.web').search(cr, uid, [('active','=',True)])
    websites = pool.get('radiotv.web').browse(cr, uid, web_ids, context)
    if websites:
        server = xmlrpclib.ServerProxy(websites[0].url + "/tinyerp-synchro.php")
#        print websites[0].url
#        print server.get_table('radiotv_channel', {'id':'int', 'name':'string', 'description':'string'})

        # deletes all many2many relations between channels and programs
        server.reset_channel_program();
        (channel_new, channel_update, channel_delete) = export_table.export_table(self, cr, uid, data, context, server, 'channel',
            ['id', 'name', 'description', 'program_ids'])

        (category_new, category_update, category_delete) = export_table.export_table(self, cr, uid, data, context, server, 'category',
            ['id', 'name', 'description'])

        (program_new, program_update, program_delete) = export_table.export_table(self, cr, uid, data, context, server, 'program',
            ['id', 'name', 'introduction', 'description', 'state', 'team', 'email', 'category_id', 'production_year', 'classification', 'broadcast_language', 'original_language', 'production_type', 'editor', 'production_country_id', 'approx_duration',])
    else:
        raise osv.except_osv('Error!', 'No website defined!\nPlease create one.')

    return {
        'channel_new':channel_new, 'channel_update':channel_update, 'channel_delete':channel_delete,
        'category_new':category_new, 'category_update':category_update, 'category_delete':category_delete,
        'program_new':program_new, 'program_update':program_update, 'program_delete':program_delete,
    }


_export_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Channels, programs and categories export">
    <separator string="Channels exported" colspan="4" />
    <field name="channel_new"/>
    <field name="channel_update"/>
    <field name="channel_delete"/>
    <separator string="Programs exported" colspan="4" />
    <field name="program_new"/>
    <field name="program_update"/>
    <field name="program_delete"/>
    <separator string="Program categories exported" colspan="4" />
    <field name="category_new"/>
    <field name="category_update"/>
    <field name="category_delete"/>
</form>'''


_export_done_fields = {
    'channel_new': {'string':'New channels', 'type':'integer', 'readonly': True},
    'channel_update': {'string':'Updated channels', 'type':'integer', 'readonly': True},
    'channel_delete': {'string':'Deleted channels', 'type':'integer', 'readonly': True},
    'program_new': {'string':'New programs', 'type':'integer', 'readonly': True},
    'program_update': {'string':'Updated programs', 'type':'integer', 'readonly': True},
    'program_delete': {'string':'Deleted programs', 'type':'integer', 'readonly': True},
    'category_new': {'string':'New categories', 'type':'integer', 'readonly': True},
    'category_update': {'string':'Updated categories', 'type':'integer', 'readonly': True},
    'category_delete': {'string':'Deleted categories', 'type':'integer', 'readonly': True},
}


class wizard_export_broadcast(wizard.interface):
    states = {
        'init': {
            'actions': [_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wizard_export_broadcast('radiotv.channel_program.export')
