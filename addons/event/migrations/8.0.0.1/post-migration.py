# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2010-2014 Akretion
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


from openerp.openupgrade import openupgrade, openupgrade_80
from openerp import pooler, SUPERUSER_ID

def load_data(cr):
    openupgrade.load_data(cr, 'event',
                          'migrations/8.0.0.1/modified_data.xml',
                          mode='update')


def delete_event_top_menu(cr, pool):
    """
    """
#     invoice_line_obj = pool.get('account.invoice.line')

    cr.execute("""
        DELETE FROM ir_ui_menu WHERE id IN (
            SELECT id FROM ir_ui_menu WHERE parent_id IN (
            SELECT id FROM ir_ui_menu WHERE parent_id IN (
            SELECT id FROM ir_ui_menu WHERE parent_id ISNULL AND name = 'Events')));

        DELETE FROM ir_ui_menu WHERE id IN (
            SELECT id FROM ir_ui_menu WHERE parent_id IN (
            SELECT id FROM ir_ui_menu WHERE parent_id ISNULL AND name = 'Events'));

        DELETE FROM ir_ui_menu WHERE id = (SELECT id FROM ir_ui_menu WHERE
                parent_id ISNULL AND name = 'Events');""")

#         DELETE FROM ir_ui_menu WHERE
#         parent_id ISNULL AND name = 'Events';""")


def add_form_to_view_mode(cr, pool):
    """
    """

    cr.execute("""
        UPDATE ir_act_window SET view_mode = 'kanban,calendar,tree,form' WHERE
        name = 'Events' AND view_mode = 'kanban,calendar,tree';
    """)



@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
#     openupgrade_80.set_message_last_post(
#         cr, SUPERUSER_ID, pool, ['hr.job', 'hr.employee'])
#     delete_event_top_menu(cr, pool)
#     load_data(cr)
    add_form_to_view_mode(cr, pool)


#    IF IT DOESNT WORK TRY THIS METHOD THROUGH OPENUPGRADE??
#         execute = openupgrade.logged_query
#     queries = [
#         """
#         UPDATE product_product
#         SET produce_delay = (
#             SELECT pt.%s
#             FROM product_template
#             WHERE product_template.id = product_product.product_tmpl_id)
#         """ % openupgrade.get_legacy_name('produce_delay'),
#     ]
#     for sql in queries:
#         execute(cr, sql)