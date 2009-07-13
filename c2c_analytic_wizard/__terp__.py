# -*- encoding: utf-8 -*-
##############################################################################
#
# @author J Grand-Guillaume ported by nbessi
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
{
    "name" : "Analytic wizard and tools for services companies",
    "description" : """
Add wizard to manage analytic account and invoicing :
 - Associate Analytic Lines to invoice (from an invoice or from analytic line directly)
 - Dissociate Analytic Lines from an invoice
 - Create blank invoice from Analytic Account (with all informations completed)
 - Create invoice from Analytic Lines
 - Get all invoice from Analytic Account (with recurssion in child account)
 - Get Analytic Lines from Analytic Account (with recurssion in child account)
 - Get Analytic Lines from an invoice for controlling
Add report for on analytic account showing the indicators et open invoice.

-----------------------------------------------------------------------------------------------

Ce module comprend un set de wizard pour faciliter la gestion des entreprises de service travaillant avec les comptes analytiques,
par exemple pour la gestion de projet. Il apporte une réelle plus-value en terme d'ergonomie. Ces wizards améliorent la facturation du travail
effectué depuis un projet (compte analytique), permettent d'associer / dissocier des lignes analytiques d'une facture ou encore d'obtenir 
la liste des factures relatives à un projet.
Ajoute egalement un rapport affichant le détails d'un compte analytique et ses factures ouvertes
    """,
    "version" : "1.3",
    "author" : "Camptocamp",
    "category" : "Generic Modules/Others",
    "website": "http://www.camptocamp.com",
    "depends" : [
                    "base",
                    "account",
                    "product",
                    "account_analytic_analysis", 
                    "c2c_reporting_tools", 
                    "hr_timesheet_invoice", 
                    "account_tax_include"
                ],
    "init_xml" : [],
    "update_xml" : [
        "wizard/wizard_view.xml",
        "indicator_account_view.xml", 
        "c2c_analytic_report.xml", 
        "c2c_analytic_wizard.xml",
        "security/wizard_security.xml"
    ],
    "active": False,
    "installable": True
}
