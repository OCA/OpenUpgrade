# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
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

from tools import sql
from openupgrade import openupgrade

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    'account_invoice': [
        ('partner_bank', 'partner_bank_id'),
        ('number', 'internal_number'),
        ],
    }

def mgr_refund_journal_type(cr):
    # assign new refund journal types to journal.journal
    cr.execute("UPDATE account_journal SET type = 'purchase_refund' " +
               "where type = 'purchase' and refund_journal = TRUE")
    cr.execute("UPDATE account_journal SET type = 'sale_refund' " +
               "where type = 'sale' and refund_journal = TRUE")

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    # This view, previously in report_account module
    # changes data type of one of the columns
    sql.drop_view_if_exists(cr, 'report_invoice_created')
    mgr_refund_journal_type(cr)

