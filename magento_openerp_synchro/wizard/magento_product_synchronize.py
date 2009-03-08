# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi, Jordi Esteve
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


def do_export(self, cr, uid, data, context):

    product_pool = pooler.get_pool(cr.dbname).get('product.product')

    #===============================================================================
    #  Getting ids
    #===============================================================================
    if data['model'] == 'ir.ui.menu':
        prod_ids = product_pool.search(cr, uid, [('exportable', '=', True)]) #,('updated', '=', False)])
    else:
        prod_ids = []
        prod_not = []
        for id in data['ids']:
            exportable_product = product_pool.search(cr, uid, [('id', '=', id), ('exportable', '=', True)])
            if exportable_product:
                prod_ids.append(exportable_product[0])
            else:
                prod_not.append(id)

        if len(prod_not) > 0:
            raise wizard.except_wizard(_("Error"), _("You asked to export non-exportable products: IDs %s") % prod_not)

    return product_pool.magento_export(cr, uid, prod_ids, context)


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Product and Stock Synchronization">
    <separator string="Products exported" colspan="4" />
    <field name="prod_new"/>
    <field name="prod_update"/>
    <field name="prod_fail"/>
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New products', 'readonly': True, 'type':'integer'},
    'prod_update': {'string':'Updated products', 'readonly': True, 'type':'integer'},
    'prod_fail': {'string':'Failed to export products', 'readonly': True, 'type':'integer'},
}

class wiz_magento_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_magento_product_synchronize('magento.products.sync');
