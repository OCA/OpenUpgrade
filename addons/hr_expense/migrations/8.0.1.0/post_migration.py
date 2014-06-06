# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Akretion
#    (<http://www.akretion.com>).
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

from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_80

logger = logging.getLogger('OpenUpgrade')


def update_hr_expense_ok(cr, pool):
    field_name = openupgrade.get_legacy_name('hr_expense_ok')
    template_obj = pool.get('product.template')

    openupgrade.logged_query(
        cr,
        """SELECT product_templ_id
        FROM product_product
        WHERE %s = 't';""" % field_name
    )
    template_ids = [row[0] for row in cr.fetchall()]
    template_obj.write(cr, SUPERUSER_ID, template_ids, {'hr_expense_ok': True})
    for template_id in template_ids:
        openupgrade.logged_query(
            cr,
            """SELECT DISTINCT t.id
            FROM product_template t
            LEFT JOIN product_product p1 ON t.id = p1.product_tmpl_id
            LEFT JOIN product_product p2 ON t.id = p2.product_tmpl_id
            WHERE p1.%s = 't'
            AND p2.%s = 'f';""" % (field_name, field_name)
        )
        for row in cr.fetchall():
            logger.warning(
                'hr_expense_ok of product.template %d has been set to True '
                'whereas at least one of its product_product was False',
                row[0]
            )


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID
    openupgrade_80.set_message_last_post(
        cr, uid, pool, ['hr.expense.expense']
    )

    update_hr_expense_ok(cr, pool)
