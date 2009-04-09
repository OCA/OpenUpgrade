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
    "name" : "Maroc Plan comptable général pour les sociétés",
    "version" : "1.0",
    "author" : "SISatlas",
    "category" : "Localisation/Account Charts",
    "description": "This is the module to manage the accounting chart for Morocco in Open ERP.",
    "website": "http://comptabilite.erp-libre.info",
    "depends" : ["base", "account"],
    "init_xml" : [],
    "update_xml" : ["types_de_comptes.xml","currency.xml","plan-maroc.xml","taxes.xml","l10n_ma_wizard.xml"],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

