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

# TODO: migrate ir.actions.todo wrt. action_id -> ir.actions.actions (prev. ir.actions.act_window)
# Maybe: investigate impact of 'model' field on ir.translation
# Maybe: ir.ui.menu now has _parent_store = True. Are parent_left/right computed automatically?
# Ignored: removal of integer_big which openerp 6.1 claims is currently unused

from openupgrade import openupgrade

module_namespec = [
    # This is a list of tuples (old module name, new module name)
    ('account_coda', 'l10n_be_coda'),
    ('base_crypt', 'auth_crypt'),
    ('mrp_subproduct', 'mrp_byproduct'),
    ('users_ldap', 'auth_ldap'),
    ('wiki', 'document_page'),
]

column_renames = {
    # login_date: orm can map timestamps to date
    'res_users': [('date', 'login_date')],
}

renamed_xmlids = []

def migrate_ir_translation(cr):
    cr.logged_query(
        cr,
        """ UPDATE ir_translation
            SET state = 'translated'
            WHERE length(value) > 0;
        """)
    cr.logged_query(
        cr,
        """ UPDATE ir_translation
            SET state = 'to_translate'
            WHERE state is NULL;
        """)

def migrate_ir_attachment(cr):
    # Data is now stored in db_datas column
    # and datas is a function field like in the document module
    if not openupgrade.column_exists('ir_attachment', 'db_datas'):
        openupgrade.rename_columns(
            cr, {'ir_attachment': ('datas', 'db_datas')})

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.update_module_names(
        cr, module_namespec
        )
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlids_renames)
    migrate_ir_translation(cr)
    migrate_ir_attachment(cr)
