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

{
        "name" : "ERP Comparisons",
        "version" : "0.1",
        "author" : "Tiny",
        "website" : "http://www.openerp.com",
        "category" : "Tools",
        "description": """
This module manages the backend of a collaborative comparison website amongst
different products.
        """, 
        "depends" : ['base'],
        "init_xml" : [ ],
        "demo_xml" : [ 
         'data/comparison.factor.csv',
         'data/comparison.item.csv',
         'data/comparison.user.csv',
         'data/comparison.vote.values.csv',
         'data/comparison.vote.csv',
#         'data/comparison.factor.result.csv', 
            ],
        "update_xml" : [
            'comparison_view.xml',
            'security/comparison_security.xml',
            'security/ir.model.access.csv',
            ],
        "active" : False,
        "installable": True,
        "certificate": '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

