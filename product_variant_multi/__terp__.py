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
    "name" : "Products with multi-level variants",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Inventory Control",
    "description":"""OpenERP is already supporting a product variants at the core level. But
without this module, variants are only mono-axial. OpenERP indeed uses the product.tempate
as the model object and the product.variant as the instance variant.
Using this module, you can now easily deal with multi-axial variants.
A product.template, now has a set of dimensions (like Color, Size, anything you want).
For each dimension, a product.template has a set of dimension values (like Red, Green
for the Color dimension). For each dimension, you can accept or not custom dimension
values. The sale interface product configurator will take it into account.
Once the product.template is set up, you can use a 'generator' button that will populate
the space of the variants. You could also choose to populate only some combinations
by hand instead.
Each variant can have an extra price that will be taken into account when computing
the base listed price. Yet to be implemented: a price extra per variant dimension value.
Finally, this module is better used along with the product_variant_configurator which
will help the salesman selecting the appropriate variant in the sale order line
using dimension criteria instead of having to crawl the full space of variants.
    """,
    "depends" : ["base", "product", "sale"],
    "init_xml" : [],
    "demo_xml" : ["demo_data.xml"],
    "update_xml" : [
        "security/ir.model.access.csv",
        "product_view.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

