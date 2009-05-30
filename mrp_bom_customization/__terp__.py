# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
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
    "name" : "BoM Customization",
    "description":"""TODO!""",
    "version" : "0.5",
    "author" : "Smile.fr",
    "website": "http://www.smile.fr",
    "category" : "Generic Modules/Sales",
    #TODO not sure it should really depend on product_variant_multi (while demo data currently depend on it)
    "depends" : ["mrp", "sale", "product_variant_multi", "sale_product_multistep_configurator"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['security/ir.model.access.csv',
                    'mrp_bom_customization_view.xml',
                    'configurator_view.xml',
                    'sale_view.xml',
                    'stock_view.xml',
                    'mrp_view.xml',
                    'demo_data.xml',],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

