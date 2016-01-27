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


def hr_expense_ok_field_func(cr, pool, id, vals):
    logger.warning(
        'hr_expense_ok of product.template %d has been set to True '
        'whereas at least one of its product_product was False', id)
    return any(vals)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID
    openupgrade_80.set_message_last_post(
        cr, uid, pool, ['hr.expense.expense']
    )
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', openupgrade.get_legacy_name('hr_expense_ok'),
        'product_tmpl_id',
        'product.template', 'hr_expense_ok',
        compute_func=hr_expense_ok_field_func)
