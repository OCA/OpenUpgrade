# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Raphaël Valyi
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

import xmlrpclib
import pooler
import wizard
import netsvc
from xml.parsers.expat import ExpatError


def _do_update(self, cr, uid, data, context):

    updated = 0
    self.pool = pooler.get_pool(cr.dbname)
    logger = netsvc.Logger()

    mw_id = self.pool.get('magento.web').search(cr, uid, [('magento_flag', '=', True)])
    mw = self.pool.get('magento.web').browse(cr, uid, mw_id[0])
    server = mw.connect_custom_api()

    #===============================================================================
    #    Sale Order Error Processing
    #===============================================================================

    to_update_array=self.pool.get('sale.order').search(cr, uid,[('magento_id','>',0)])

    for so_id in to_update_array:
        #Packaging 
        update_so=self.pool.get('sale.order').browse(cr, uid, so_id)
        web_so={
                'magento_id': update_so.magento_id or int(0),
                'status': update_so.state or int(0),
        }
        #Update

        try:
            updated_id=server.update_sale_order([web_so])
        except ExpatError, error:
            logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Error occurred during Sales Orders update, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!\nError %s") % error)
            raise wizard.except_wizard(_("Magento Import"), _("Error occurred during Sales Orders update, See your debug.xmlrpc.log in the Smile_OpenERP_Synch folder in your Apache!"))


        #Report
        if int(updated_id) != int(update_so.magento_id) :
            logger.notifyChannel(_("Magento SO update"), netsvc.LOG_ERROR, _("Sale Order ID %s wrong update !") % updated_id)
        else:
            updated += 1

    return {'updated':updated}


#===============================================================================
#   Wizard Declaration
#===============================================================================

_update_done_form = '''<?xml version="1.0"?>
<form string="Saleorders import">
    <separator string="Magento Sale Orders Update" colspan="4" />
    <field name="updated"/>
</form>'''

_update_done_fields = {
    'updated': {'string':'Sales Orders Updated', 'readonly':True, 'type':'integer'},
}


class wiz_magento_so_update(wizard.interface):
    states = {
        'init': {
            'actions': [_do_update],
            'result': {'type': 'form', 'arch': _update_done_form, 'fields': _update_done_fields,'state': [('end', 'End')] }
        }
    }
wiz_magento_so_update('magento.saleorders.update');
