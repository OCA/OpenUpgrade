##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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
import wizard

_import_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form title="Sale orders import">
<separator string="Sale orders succesfully imported" colspan="4" />
%s
</form>'''

_import_done_fields = {}


def _do_import(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    esale_oscom_obj = self.pool.get('esale.oscom.web')

    no_of_so = 0
    if data['model'] == 'ir.ui.menu':
        website_ids = esale_oscom_obj.search(cr, uid, [('active', '=', True)])
        for website_id in website_ids:
            no_of_so += esale_oscom_obj.saleorder_import(cr, uid, website_id, context)
    else:
        no_of_so += esale_oscom_obj.saleorder_import(cr, uid, data['id'], context)

    lable_string = "<label string='%s sale order(s) has been imported from the web site.' />" % str(no_of_so)
    wiz_esale_oscom_import_sos.states['init']['result']['arch'] = _import_done_form % lable_string
    return {}


class wiz_esale_oscom_import_sos(wizard.interface):

    states = { 'init' : { 'actions' : [_do_import],
                          'result' : { 'type'   : 'form',
                                       'arch'   : _import_done_form,
                                       'fields' : _import_done_fields,
                                       'state'  : [('end', 'End')]
                                     }
                        }
             }

wiz_esale_oscom_import_sos('esale.oscom.saleorders');
