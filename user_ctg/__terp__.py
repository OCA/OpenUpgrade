# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

{
    'name': 'CTG points Management',
    'version': '0.0.5',
    'category': 'Tools',
    'description': """This Module is managed User CTG points (called CTG points as 'Contribution To Growth points') for
* DMS: Added CTG points to Document's Author  when sent feedback by other people after downloading document through the DMS
* Developments: Added CTG points to Developer  based on LP karma 
* Marketing: Added CTG points to Marketing  base on number of incoming visitors on our website
* Sales: Addded CTG points to Saleman  that sold something and points accordingly to amount sold
* Customer Satisfaction: Added CTG points to resposible person of project when customer send feedback for a service/an integration 
""",
    'author': 'Tiny',
    'depends': ['base', 'sale','document','account_invoice_salesman','project'],
    'update_xml': ['user_ctg_view.xml','security/user_ctg_security.xml','security/ir.model.access.csv','user_ctg_data.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
