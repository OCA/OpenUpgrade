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
import pooler
import time
import datetime

copy_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Copy broadcasts from a day to other">
    <label string="Copy the broadcasts from a range of days (or one day) to another range of days. The previous broadcasts in the destination range of days are deleted." colspan="4"/>
    <separator colspan="4"/>

    <label string="Start range" colspan="4"/>
    <field name="d_from"/>
    <field name="d_from2"/>

    <separator colspan="4"/>
    <label string="End range" colspan="4"/>
    <field name="d_to"/>

    <separator colspan="4"/>
    <field name="channel_id"/>
</form>'''

copy_fields = {
    'd_from': {'string': 'From', 'type':'date', 'required':True},
    'd_from2': {'string': 'To', 'type':'date', 'required':True},
    'd_to':  {'string': 'From', 'type':'date', 'required':True},
    'channel_id': {'string': 'Channel', 'type': 'many2one', 'relation':'radiotv.channel', 'required':True},
}

def _get_data(self, cr, uid, data, context={}):
    channel_id = False
    pool = pooler.get_pool(cr.dbname)
    if data['model'] == 'radiotv.channel' and len(data['ids']) == 1:
        channel_id = data['ids'][0]
    if data['model'] == 'radiotv.broadcast' and len(data['ids']) == 1:
        broadcast = pool.get('radiotv.broadcast').browse(cr, uid, data['ids'][0], context)
        channel_id = broadcast.channel_id.id
    return {'d_from': time.strftime('%Y-%m-%d'), 'd_from2': time.strftime('%Y-%m-%d'), 'channel_id': channel_id,}

def _copy(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    form = data['form']
    d_from = form.get('d_from', False)
    d_from2 = form.get('d_from2', False)
    d_to = form.get('d_to', False)
    channel_id = form.get('channel_id', False)
    start = datetime.date(int(d_from[:4]), int(d_from[5:7]), int(d_from[8:]))
    end   = datetime.date(int(d_from2[:4]), int(d_from2[5:7]), int(d_from2[8:]))
    to    = datetime.date(int(d_to[:4]), int(d_to[5:7]), int(d_to[8:]))
    oneday = datetime.timedelta(days=1)
    b = pool.get('radiotv.broadcast')
    while start <= end:
        d_from = "%04i-%02i-%02i" % (start.year, start.month, start.day)
        d_to   = "%04i-%02i-%02i" % (to.year, to.month, to.day)
        #print d_from, d_to
        
        # deletes previous broadcasts
        broadcast_ids = b.search(cr, uid, [('channel_id','=',channel_id),('dt_start','>=','%s 00:00:00' % d_to),('dt_start','<=','%s 23:59:59' % d_to)])
        b.unlink(cr, uid, broadcast_ids)
        
        # copies new broadcasts
        broadcast_ids = b.search(cr, uid, [('channel_id','=',channel_id),('dt_start','>=','%s 00:00:00' % d_from),('dt_start','<=','%s 23:59:59' % d_from)])
        for broadcast in b.browse(cr, uid, broadcast_ids, context):
            vals = {
                'dt_start': '%s %s' % (d_to, broadcast.dt_start[11:]),
                'channel_id': channel_id,
                'program_id': broadcast.program_id.id,
                'description': broadcast.description,
            }
            if broadcast.dt_end:
                vals['dt_end'] = '%s %s' % (d_to, broadcast.dt_end[11:]),
            b.create(cr, uid, vals)
        start = start + oneday
        to = to + oneday
    return {}

class wizard_copy_broadcast(wizard.interface):
    states = {
        'init': {
            'actions': [_get_data],
            'result': {'type':'form', 'arch':copy_form, 'fields':copy_fields, 'state':[('end','Cancel','gtk-cancel'),('copy','Copy','',True)]}
        },
        'copy': {
            'actions': [_copy],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_copy_broadcast('radiotv.broadcast.copy')
