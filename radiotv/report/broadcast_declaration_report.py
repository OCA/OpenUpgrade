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

import pooler
import time
from report import report_sxw
import common

class broadcast_declaration_report(report_sxw.rml_parse):

    _day_of_week = ('Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge')

    def __init__(self, cr, uid, name, context):
        super(broadcast_declaration_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'obt_channel': self.obt_channel,
            'obt_broadcasts': self.obt_broadcasts,
            'obt_programs': self.obt_programs,
            'lang': context['lang'],
        })

    def obt_channel(self, channel_id):
        return pooler.get_pool(self.cr.dbname).get('radiotv.channel').browse(self.cr, self.uid, channel_id).name

    def obt_broadcasts(self, channel_id, d_from, d_to, program_id):
        print channel_id, d_from, d_to, program_id
        res = []
        pool = pooler.get_pool(self.cr.dbname)
        
        dfrom = time.strptime(d_from, '%Y-%m-%d')
        dto = time.strptime(d_to, '%Y-%m-%d')
        for n in range(int(time.mktime(dfrom)), int(time.mktime(dto))+1, 86400):
            d = time.localtime(n)
            day = time.strftime('%Y-%m-%d', d)
            print day
            broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id), ('program_id','=',program_id), ('dt_start','>=','%s 00:00:00' % day),('dt_start','<=','%s 23:59:59' % day)])
            if broadcast_ids:
                info = time.strftime('%d-%m-%Y', d)+": "
                for bc in pool.get('radiotv.broadcast').browse(self.cr, self.uid, broadcast_ids):
                    info += bc.dt_start[11:13]+':'+bc.dt_start[14:16]+', '
                res.append({'info': info[:-2]})
        print res
        return res

    def obt_programs(self, channel_id, d_from, d_to):
        #print channel_id, d_from, d_to
        res = []
        pool = pooler.get_pool(self.cr.dbname)

        c = pool.get('radiotv.channel').browse(self.cr, self.uid, channel_id)
        #print c.program_ids
        for p in c.program_ids:
            broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id), ('program_id','=',p.id), ('dt_start','>=','%s 00:00:00' % d_from), ('dt_start','<=','%s 23:59:59' % d_to)])
            print broadcast_ids
            if broadcast_ids:
                res.append({
                    'id': p.id,
                    'name': p.name,
                    'category_name': p.category_id and p.category_id.name or '',
                    'editor': p.editor,
                    'approx_duration': p.approx_duration,
                    'original_language': p.original_language,
                    'broadcast_language': p.broadcast_language,
                    'production_country': p.production_country_id and p.production_country_id.name or '',
                    'production_year': p.production_year,
                    'classification': p.classification,
                    'production_type': p.production_type,
                 })
        #print res
        return res

report_sxw.report_sxw('report.radiotv.broadcast.declaration.report', 'radiotv.broadcast',
        'addons/radiotv/report/broadcast_declaration_report.rml',
        parser=broadcast_declaration_report, header=False)
