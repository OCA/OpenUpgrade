# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

import os
from osv import osv
import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

def prevent_account_installer(cr):
    """
    If the account installer has not run, e.g. 
    after manual installation of account chart
    and if the company country is set, the 
    account module will install a random
    chart on upgrading...
    """
    cr.execute("""
        UPDATE ir_actions_todo
        SET state = 'done'
        WHERE state = 'open'
            AND id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE name = 'account_configuration_installer_todo'
            AND module = 'account')
    """)

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        if not openupgrade.column_exists(
            cr, 'account_bank_statement_line_move_rel', 'statement_line_id'):
            openupgrade.rename_columns(cr, {
                    # many2many table square dance
                    'account_bank_statement_line_move_rel': [
                        ('move_id', 'move_id_tmp'),
                        ('statement_id', 'move_id'),
                        ('move_id_tmp', 'statement_line_id'),
                        ],
                    })
        else:
            logger.info("%s: statement line / move relation table "
                        "columns have already been swapped", me)
        if not openupgrade.column_exists(
            cr, 'account_account_type', 'report_type_tmp'):
            openupgrade.rename_columns(cr, {
                    'account_account_type': [
                        # Report_type is now an unstored function field with a fnct_write.
                        # Preserve the column here to process in the post script 
                        ('report_type', 'report_type_tmp'),
                        ],
                    })
        else:
            logger.info("%s: account type table, column report type"
                        "has already been preserved", me)
        prevent_account_installer(cr)

    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
