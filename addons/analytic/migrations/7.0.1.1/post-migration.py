# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2013-today Sylvain LE GAL
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

from openupgrade import openupgrade
from openupgrade import openupgrade_70
from openerp import pooler, SUPERUSER_ID


def fill_manager_id(cr, pool):
    """
    Fill the new field 'manager_id' depending on
    account_analytic_account.partner_id.user_id
    """
    analytic_obj = pool.get('account.analytic.account')
    cr.execute("""SELECT
        account_analytic_account.id as id,
        res_users.id as manager_id
    FROM account_analytic_account
    INNER JOIN res_partner
        on res_partner.id = account_analytic_account.partner_id
    INNER JOIN res_users on res_partner.user_id = res_users.id; """)
    for row in cr.dictfetchall():
        vals = {
            'manager_id': row['manager_id'],
        }
        analytic_obj.write(cr, SUPERUSER_ID, row['id'], vals)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.analytic.account',
        'partner_id', openupgrade.get_legacy_name('contact_id'))
    fill_manager_id(cr, pool)
