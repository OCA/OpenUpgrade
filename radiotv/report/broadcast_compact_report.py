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

class broadcast_compact_report(report_sxw.rml_parse):

	_day_of_week = ('Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge')

	def __init__(self, cr, uid, name, context):
		super(broadcast_compact_report, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'obt_channel': self.obt_channel,
			'obt_days': self.obt_days,
			'obt_broadcasts': self.obt_broadcasts,
			'lang': context['lang'],
		})

	def obt_channel(self, channel_id):
		return pooler.get_pool(self.cr.dbname).get('radiotv.channel').browse(self.cr, self.uid, channel_id).name

	def obt_days(self, d_from, d_to):
		res = []
		dfrom = time.strptime(d_from, '%Y-%m-%d')
		dto = time.strptime(d_to, '%Y-%m-%d')
		for n in range(int(time.mktime(dfrom)), int(time.mktime(dto))+1, 2*86400):
			d1 = time.localtime(n) # Today
			d2 = time.localtime(n+86400) # Tomorrow
			res.append({'day1': time.strftime('%d-%m-%Y',d1) , 'dow1': self._day_of_week[d1[6]],
						'day2': time.strftime('%d-%m-%Y',d2) , 'dow2': self._day_of_week[d2[6]]})
		return res

	def obt_broadcasts(self, channel_id, day, pday=0):
		res = []
		pool = pooler.get_pool(self.cr.dbname)
		day = day[6:]+'-'+day[3:5]+'-'+day[:2]

		if pday==0:
			broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id),('dt_start','>=','%s 00:00:00' % day),('dt_start','<=','%s 23:59:59' % day)])
		elif pday==1:
			broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id),('dt_start','>=','%s 00:00:00' % day),('dt_start','<=','%s 13:59:59' % day)])
		elif pday==2:
			broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id),('dt_start','>=','%s 14:00:00' % day),('dt_start','<=','%s 19:59:59' % day)])
		else:
			broadcast_ids = pool.get('radiotv.broadcast').search(self.cr, self.uid, [('channel_id','=',channel_id),('dt_start','>=','%s 20:00:00' % day),('dt_start','<=','%s 23:59:59' % day)])
		for bc in pool.get('radiotv.broadcast').browse(self.cr, self.uid, broadcast_ids):
			# Insert at the begining of the list to invert the order
			res.insert(0, {'time': bc.dt_start[11:13]+':'+bc.dt_start[14:16], 'p_name': bc.program_id.name, 'p_introduction': bc.program_id.introduction, 'description': bc.description,})
		if not res:
			res.insert(0, {'time': '', 'p_name': '', 'p_introduction': '', 'description': '',})
		#print res
		return res

report_sxw.report_sxw('report.radiotv.broadcast.compact.report', 'radiotv.broadcast',
		'addons/radiotv/report/broadcast_compact_report.rml',
		parser=broadcast_compact_report, header=False)
