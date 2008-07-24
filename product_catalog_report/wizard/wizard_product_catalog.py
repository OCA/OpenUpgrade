# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import time
import pooler

_lang_form = '''<?xml version="1.0"?>
<form string="Choose catalog preferencies">
    <separator string="Select a printing language " colspan="4"/>
    <field name="report_lang"/>
   <separator string="Select a Product Categories " colspan="4"/>
    <field name="categories" colspan="4" nolabel="1" />

</form>'''



class wiz_productCatalog(wizard.interface):
    def _get_language(self, cr, uid, context):
        lang_obj=pooler.get_pool(cr.dbname).get('res.lang')
        ids=lang_obj.search(cr, uid, [('active', '=', True),])
        langs=lang_obj.browse(cr, uid, ids)
        return [(lang.code, lang.name ) for lang in langs]

    _lang_fields = {
    'report_lang': {'string':'Language', 'type':'selection', 'selection':_get_language,},
    'categories': {'string':'Select Category', 'type':'many2many', 'relation':'product.category', 'required':True},
    }

    def _load(self,cr,uid,data,context):
        partner_obj=pooler.get_pool(cr.dbname).get('res.partner')
        partners=partner_obj.browse(cr, uid, [data['id']])
        if len(partners)>0:
            data['form']['report_lang']=partners[0].lang
        return data['form']
    states = {
        'init': {
            'actions': [_load],
            'result': {'type': 'form', 'arch':_lang_form, 'fields':_lang_fields, 'state':[('end','Cancel'),('print','Print Product Catalog') ]}
        },
        'print': {
            'actions': [],
            'result': {'type': 'print', 'report': 'product_catalog', 'state':'end'}
        }
    }
wiz_productCatalog('res.partner.product_catalog')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

