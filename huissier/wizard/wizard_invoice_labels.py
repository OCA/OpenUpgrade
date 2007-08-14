# -*- coding: iso-8859-1 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

# l'interet d'avoir un wizard pour ca est de pouvoir imprimer les vignettes directement
def _invoice_labels(self, uid, datas):
	service = netsvc.LocalService("object_proxy")
	invoice_id = service.execute(uid, 'huissier.vignettes', 'invoice', [datas['id']])
	return {}

class wizard_invoice_labels(wizard.interface):
	states = {
		'init': {
			'actions': [_invoice_labels],
#			'result': {'type': 'state', 'state':'end'}
			'result': {'type': 'print', 'report':'huissier.labels', 'state':'end'}
		}
	}
wizard_invoice_labels('huissier.labels.invoice')


