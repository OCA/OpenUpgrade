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

import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')
me = __file__

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    #
    'email_template': [
        ('object_name', 'model_id'),
        ('def_to', 'email_to'),
        ('def_cc', 'email_cc'),
        ('def_bcc', 'email_bcc'),
        ('def_subject', 'subject'),
        ('def_body_text', 'body_text'),
        ('def_body_html', 'body_html'),
        ('use_sign', 'user_signature'),
        ('file_name', 'report_name'),
        ],
    }

def fix_email_from(cr):
    """ 
    Prematurely add the email_from column and fill it with the
    address from the obsolete account model.
    """
    openupgrade.logged_query(
        cr,
        "ALTER TABLE email_template ADD COLUMN email_from "
        "CHARACTER VARYING (128)")
    openupgrade.logged_query(
        cr,
        "UPDATE email_template SET email_from = email_id "
        "FROM email_template_account WHERE "
        "email_template.from_account = email_template_account.id")

@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    openupgrade.rename_columns(cr, column_renames)
    fix_email_from(cr)
    openupgrade.delete_model_workflow(cr, 'email_template.account')
