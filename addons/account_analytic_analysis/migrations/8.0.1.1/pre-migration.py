# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp.openupgrade import openupgrade


@openupgrade.migrate
def migrate(cr, version):
    # if account_analytic_analysis_recurring is installed, uninstall it and
    # move relevant xmlids to this module
    cr.execute(
        "update ir_model_data set module='account_analytic_analysis' "
        "where name in ('account_analytic_cron_for_invoice') "
        "and module='account_analytic_analysis_recurring'")
    cr.execute(
        "update ir_module_module set state='to remove' "
        "where name='account_analytic_analysis_recurring' "
        "and state in ('installed', 'to install', 'to upgrade')")
