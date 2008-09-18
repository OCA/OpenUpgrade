# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Smile S.A. (http://www.smile.fr) All Rights Reserved.
# @authors: Sylvain Pamart, Rapha�l Valyi
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

#===============================================================================
#    Information Form & Fields
#===============================================================================

_update_done_form = '''<?xml version="1.0"?>
<form string="Saleorders import">
    <separator string="Magento Sale Orders Update" colspan="4" />
    <field name="updated"/>
</form>'''

_update_done_fields = {
    'updated': {'string':'Sales Orders Updated', 'readonly':True, 'type':'integer'},
}


def _do_update(self, cr, uid, data, context):
    
    #===============================================================================
    #  Init
    #===============================================================================

    updated = 0
    self.pool = pooler.get_pool(cr.dbname)
    logger = netsvc.Logger()

    # Server communication
    magento_web_id=self.pool.get('magento.web').search(cr,uid,[('magento_id','=',1)])
    try:
        magento_web=self.pool.get('magento.web').browse(cr,uid,magento_web_id[0])
        server = xmlrpclib.ServerProxy("%sapp/code/community/Smile_OpenERP_Synchro/openerp-synchro.php" % magento_web.magento_url)# % website.url)
    except:
        raise wizard.except_wizard("UserError", "You must have a declared website with a valid URL! provided URL: %s/openerp-synchro.php" % magento_web.magento_url)
       

    #===============================================================================
    #    Sale Order Error Processing
    #===============================================================================

    to_update_array=self.pool.get('sale.order').search(cr, uid,[('magento_id','>',0)])

    for so_id in to_update_array:
        
        update_so=self.pool.get('sale.order').browse(cr, uid, so_id)
        web_so={
                'magento_id': update_so.magento_id or int(0),
                'status': update_so.state or int(0),
        }
        updated_id=server.update_sale_order([web_so])
    
        if int(updated_id) != int(update_so.magento_id) :
            logger.notifyChannel("Magento SO update", netsvc.LOG_ERROR, "Sale Order ID %s wrong update !" % updated_id)
        else:
            updated += 1

    return {'updated':updated}


#===============================================================================
#   Wizard Declaration
#===============================================================================
        
class wiz_magento_so_update(wizard.interface):
    states = {
        'init': {
            'actions': [_do_update],
            'result': {'type': 'form', 'arch': _update_done_form, 'fields': _update_done_fields,'state': [('end', 'End')] }
        }
    }
wiz_magento_so_update('magento.saleorders.update');
