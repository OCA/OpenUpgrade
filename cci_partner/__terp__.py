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
    "name" : "CCI Partner",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/CCI",
    "description": """
        Specific module for cci project which will inherit partner module
    """,
    "depends" : ["base", "base_vat", "cci_base_contact", "account_l10nbe_domiciliation", "cci_country"],
    "init_xml" : [],
    "demo_xml" : ["cci_data.xml",
                   #"user_data.xml",
                   "zip_data.xml", "courtesy_data.xml","links_data.xml",
                   "activity_data.xml",
                   #"states_data.xml",
                   #"category_data.xml",
                   "function_data.xml"],

    "update_xml" : ['cci_partner_view.xml','article_sequence.xml','cci_partner_report.xml','cci_partner_wizard.xml','security/security.xml','security/ir.model.access.csv'],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

