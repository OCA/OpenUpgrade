# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
