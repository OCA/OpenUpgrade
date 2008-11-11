# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import ir
import time
import os
import netsvc
import xmlrpclib
import pooler
import wizard
from osv import osv


_export_done_form = '''<?xml version="1.0"?>
<form string="Stock Update">
<separator string="Stock succesfully updated" colspan="4" />
</form>'''

_export_done_fields = {}

def _do_export(self, cr, uid, data, context):
    self.pool = pooler.get_pool(cr.dbname)
    website=self.pool.get('esale_osc.web').browse(cr, uid, [data['id']])[0]
    server = xmlrpclib.ServerProxy("%s/tinyerp-syncro.php" % website.url)
    for osc_product in website.product_ids:
        webproduct={
                'product_id'    : osc_product.esale_osc_id,
                'quantity'      : self.pool.get('product.product')._product_virtual_available(cr, uid, [osc_product.product_id.id], '', False, {'shop':website.shop_id.id})[osc_product.product_id.id]
        }
        osc_id=server.set_product_stock(webproduct)
    return {}

class wiz_esale_osc_stocks(wizard.interface):

    states = {  #'init'     : { 'actions'       : [],
                #               'result'        : { 'type'      : 'form',
                #                                   'arch'      : _import_form,
                #                                   'fields'    : _import_fields,
                #                                   'state'     : [('import', 'Import languages and taxes'), ('end', 'Cancel')]
                #                                   },
                #               },
                'init'      : { 'actions'       : [_do_export],
                                'result'        : { 'type'      : 'form',
                                                    'arch'      : _export_done_form,
                                                    'fields'    : _export_done_fields,
                                                    'state'     : [('end', 'End')]
                                                    }
                                }
                }


wiz_esale_osc_stocks('esale_osc.stocks');

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

