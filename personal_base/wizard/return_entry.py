# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2008 Sandas. (http://www.sandas.eu) All Rights Reserved.
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
############################################################

import wizard
import pooler

def _returnEntry(self, cr, uid, data, context):
	entry_pool = pooler.get_pool(cr.dbname).get('personal.base.account.entry')
	line_pool = pooler.get_pool(cr.dbname).get('personal.base.account.entry.line')
	parent_id = line_pool.read(cr, uid, [data['id']], ['parent_id'])[0]['parent_id'][0]
	(entry_pool.browse(cr, uid, [parent_id])[0]).return_entry(cr, uid, [parent_id])
	return {}

class wizard_return_entry(wizard.interface):
	states = {
		'init' : {
			'actions' : [],
			'result': {'type': 'action', 'action':_returnEntry, 'state':'end'}
		},
	}
wizard_return_entry("personal.wizard_return_entry")
