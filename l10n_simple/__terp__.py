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
    "name" : "Simple Account Chart",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Localisation/Europe",
    "description": "This is the module to manage the accounting chart for Europe in Open ERP.",
    "depends" : ["account_chart"],
    "init_xml" : [],
    "demo_xml" : ["account_demo.xml",
#                  "account.analytic.line.csv" #comment because of template system
                  ],
    "update_xml" : ["tax_configure_wiz.xml","account_pcmn_belgium.xml","l10n_simple_wizard.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

